# ApexTrade - Database Schema

**Version:** 1.0  
**Date:** February 1, 2026  
**Database:** PostgreSQL 16 + TimescaleDB 2.13+

---

## Table of Contents

1. [Overview](#1-overview)
2. [Entity Relationship Diagram](#2-entity-relationship-diagram)
3. [PostgreSQL Schema](#3-postgresql-schema)
4. [TimescaleDB Schema](#4-timescaledb-schema)
5. [Indexes & Constraints](#5-indexes--constraints)
6. [Migrations](#6-migrations)
7. [Data Retention](#7-data-retention)

---

## 1. Overview

### 1.1 Database Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          APEXTRADE DATABASES                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────────────────┐   ┌─────────────────────────────┐         │
│   │     PostgreSQL 16           │   │     TimescaleDB             │         │
│   │     (apextrade)             │   │     (apextrade_ts)          │         │
│   │                             │   │                             │         │
│   │  ┌───────────────────────┐  │   │  ┌───────────────────────┐  │         │
│   │  │ users                 │  │   │  │ ohlcv (hypertable)    │  │         │
│   │  │ strategies            │  │   │  │ equity_history        │  │         │
│   │  │ rules                 │  │   │  │ tick_data             │  │         │
│   │  │ backtests             │  │   │  └───────────────────────┘  │         │
│   │  │ backtest_trades       │  │   │                             │         │
│   │  │ portfolios            │  │   │  Continuous Aggregates:     │         │
│   │  │ positions             │  │   │  ┌───────────────────────┐  │         │
│   │  │ trades                │  │   │  │ ohlcv_1h              │  │         │
│   │  │ api_keys              │  │   │  │ ohlcv_1d              │  │         │
│   │  │ alerts                │  │   │  └───────────────────────┘  │         │
│   │  │ audit_logs            │  │   │                             │         │
│   │  └───────────────────────┘  │   └─────────────────────────────┘         │
│   │                             │                                            │
│   └─────────────────────────────┘                                            │
│                                                                              │
│   ┌─────────────────────────────┐                                            │
│   │     Redis 7                 │                                            │
│   │     (cache + sessions)      │                                            │
│   │                             │                                            │
│   │  Keys:                      │                                            │
│   │  • session:{user_id}        │                                            │
│   │  • cache:ticker:{symbol}    │                                            │
│   │  • cache:portfolio:{id}     │                                            │
│   │  • rate_limit:{user_id}     │                                            │
│   └─────────────────────────────┘                                            │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Schema Conventions

| Convention | Description |
|------------|-------------|
| **Table names** | Plural, snake_case (`strategies`, `backtest_trades`) |
| **Column names** | snake_case (`created_at`, `user_id`) |
| **Primary keys** | `id` as UUID v4 |
| **Foreign keys** | `{table}_id` (e.g., `user_id`, `strategy_id`) |
| **Timestamps** | `TIMESTAMPTZ` with `created_at`, `updated_at` |
| **Booleans** | `is_` prefix (`is_active`, `is_paper`) |
| **Enums** | Stored as `VARCHAR` with CHECK constraints |
| **JSON** | `JSONB` for flexible schemas |
| **Money** | `NUMERIC(18,8)` for prices, `NUMERIC(15,2)` for portfolio values |

---

## 2. Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                            ENTITY RELATIONSHIP DIAGRAM                               │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│                                                                                      │
│   ┌───────────────┐                                                                 │
│   │    users      │                                                                 │
│   ├───────────────┤                                                                 │
│   │ PK id         │                                                                 │
│   │    email      │                                                                 │
│   │    password   │                                                                 │
│   └───────┬───────┘                                                                 │
│           │                                                                          │
│           │ 1                                                                        │
│           │                                                                          │
│     ┌─────┼─────────────────────┬─────────────────────┐                             │
│     │     │                     │                     │                              │
│     ▼ N   ▼ N                   ▼ N                   ▼ N                            │
│   ┌───────────────┐   ┌───────────────┐   ┌───────────────┐   ┌───────────────┐     │
│   │  strategies   │   │  portfolios   │   │   api_keys    │   │    alerts     │     │
│   ├───────────────┤   ├───────────────┤   ├───────────────┤   ├───────────────┤     │
│   │ PK id         │   │ PK id         │   │ PK id         │   │ PK id         │     │
│   │ FK user_id    │   │ FK user_id    │   │ FK user_id    │   │ FK user_id    │     │
│   │    name       │   │    name       │   │    exchange   │   │    symbol     │     │
│   │    asset      │   │    is_paper   │   │    api_key    │   │    condition  │     │
│   │    rules      │   │    balance    │   │    encrypted  │   │    triggered  │     │
│   └───────┬───────┘   └───────┬───────┘   └───────────────┘   └───────────────┘     │
│           │                   │                                                      │
│           │ 1                 │ 1                                                    │
│           │                   │                                                      │
│     ┌─────┴─────┐       ┌─────┴─────────────────┐                                   │
│     │           │       │                       │                                    │
│     ▼ N         ▼ N     ▼ N                     ▼ N                                  │
│   ┌───────────────┐   ┌───────────────┐   ┌───────────────┐                         │
│   │   backtests   │   │   positions   │   │    trades     │                         │
│   ├───────────────┤   ├───────────────┤   ├───────────────┤                         │
│   │ PK id         │   │ PK id         │   │ PK id         │                         │
│   │ FK strategy_id│   │ FK portfolio  │   │ FK portfolio  │                         │
│   │    start_date │   │    symbol     │   │ FK strategy   │                         │
│   │    end_date   │   │    quantity   │   │    symbol     │                         │
│   │    results    │   │    avg_price  │   │    side       │                         │
│   └───────┬───────┘   └───────────────┘   │    price      │                         │
│           │                               └───────────────┘                         │
│           │ 1                                                                        │
│           │                                                                          │
│           ▼ N                                                                        │
│   ┌───────────────┐                                                                 │
│   │backtest_trades│                                                                 │
│   ├───────────────┤                                                                 │
│   │ PK id         │                                                                 │
│   │ FK backtest_id│                                                                 │
│   │    symbol     │                                                                 │
│   │    side       │                                                                 │
│   │    price      │                                                                 │
│   │    pnl        │                                                                 │
│   └───────────────┘                                                                 │
│                                                                                      │
│                                                                                      │
│   TIMESCALEDB (Hypertables)                                                         │
│   ─────────────────────────                                                         │
│                                                                                      │
│   ┌───────────────┐   ┌───────────────┐   ┌───────────────┐                         │
│   │     ohlcv     │   │equity_history │   │   tick_data   │                         │
│   ├───────────────┤   ├───────────────┤   ├───────────────┤                         │
│   │ PK time       │   │ PK time       │   │ PK time       │                         │
│   │ PK symbol     │   │ PK portfolio  │   │ PK symbol     │                         │
│   │ PK timeframe  │   │    equity     │   │    bid        │                         │
│   │    open       │   │    cash       │   │    ask        │                         │
│   │    high       │   │    positions  │   │    last       │                         │
│   │    low        │   │    pnl        │   │    volume     │                         │
│   │    close      │   └───────────────┘   └───────────────┘                         │
│   │    volume     │                                                                 │
│   └───────────────┘                                                                 │
│                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. PostgreSQL Schema

### 3.1 Users Table

```sql
-- Users table
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    
    -- Profile
    first_name      VARCHAR(100),
    last_name       VARCHAR(100),
    timezone        VARCHAR(50) DEFAULT 'Europe/Paris',
    preferred_currency VARCHAR(3) DEFAULT 'EUR',
    
    -- Status
    is_active       BOOLEAN DEFAULT TRUE,
    is_verified     BOOLEAN DEFAULT FALSE,
    mfa_enabled     BOOLEAN DEFAULT FALSE,
    mfa_secret      VARCHAR(255),
    
    -- Notification Preferences
    notification_preferences JSONB DEFAULT '{
        "email_trade_executed": true,
        "email_daily_summary": true,
        "push_price_alerts": true
    }'::jsonb,
    
    -- Timestamps
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    last_login_at   TIMESTAMPTZ,
    verified_at     TIMESTAMPTZ,
    
    -- Constraints
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT valid_timezone CHECK (timezone ~ '^[A-Za-z]+/[A-Za-z_]+$'),
    CONSTRAINT valid_currency CHECK (preferred_currency ~ '^[A-Z]{3}$')
);

-- Indexes
CREATE INDEX idx_users_email ON users (email);
CREATE INDEX idx_users_active ON users (is_active) WHERE is_active = TRUE;

-- Trigger: Update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### 3.2 Strategies Table

```sql
-- Trading strategies
CREATE TABLE strategies (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Definition
    name            VARCHAR(100) NOT NULL,
    description     TEXT,
    version         INTEGER DEFAULT 1,
    
    -- Configuration
    asset_symbol    VARCHAR(20) NOT NULL,
    timeframe       VARCHAR(5) NOT NULL,
    
    -- Rules (JSONB for flexibility)
    entry_rules     JSONB NOT NULL,
    exit_rules      JSONB NOT NULL,
    
    -- Risk Management
    stop_loss_pct       NUMERIC(5,2),
    take_profit_pct     NUMERIC(5,2),
    max_position_size_pct NUMERIC(5,2) DEFAULT 10.00,
    max_drawdown_pct    NUMERIC(5,2),
    trailing_stop_pct   NUMERIC(5,2),
    
    -- State
    status          VARCHAR(20) DEFAULT 'draft',
    trading_mode    VARCHAR(20),
    
    -- Timestamps
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    activated_at    TIMESTAMPTZ,
    last_signal_at  TIMESTAMPTZ,
    
    -- Constraints
    CONSTRAINT valid_status CHECK (status IN ('draft', 'active', 'paused', 'archived')),
    CONSTRAINT valid_trading_mode CHECK (trading_mode IN ('paper', 'live') OR trading_mode IS NULL),
    CONSTRAINT valid_timeframe CHECK (timeframe ~ '^[1-9][0-9]?[mhdwM]$'),
    CONSTRAINT valid_symbol CHECK (asset_symbol ~ '^[A-Z]{2,10}/[A-Z]{2,10}$'),
    CONSTRAINT valid_stop_loss CHECK (stop_loss_pct IS NULL OR (stop_loss_pct >= 0 AND stop_loss_pct <= 100)),
    CONSTRAINT valid_take_profit CHECK (take_profit_pct IS NULL OR (take_profit_pct >= 0 AND take_profit_pct <= 1000)),
    CONSTRAINT valid_position_size CHECK (max_position_size_pct > 0 AND max_position_size_pct <= 100)
);

-- Indexes
CREATE INDEX idx_strategies_user ON strategies (user_id);
CREATE INDEX idx_strategies_user_status ON strategies (user_id, status);
CREATE INDEX idx_strategies_active ON strategies (status, trading_mode) 
    WHERE status = 'active';
CREATE INDEX idx_strategies_asset ON strategies (asset_symbol);

-- GIN index for JSONB rules (for querying by indicator)
CREATE INDEX idx_strategies_entry_rules ON strategies USING GIN (entry_rules);

-- Trigger for updated_at
CREATE TRIGGER strategies_updated_at
    BEFORE UPDATE ON strategies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for version increment
CREATE OR REPLACE FUNCTION increment_strategy_version()
RETURNS TRIGGER AS $$
BEGIN
    IF (OLD.entry_rules IS DISTINCT FROM NEW.entry_rules) OR 
       (OLD.exit_rules IS DISTINCT FROM NEW.exit_rules) THEN
        NEW.version = OLD.version + 1;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER strategies_version
    BEFORE UPDATE ON strategies
    FOR EACH ROW
    EXECUTE FUNCTION increment_strategy_version();
```

### 3.3 Backtests Table

```sql
-- Backtest runs
CREATE TABLE backtests (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_id     UUID NOT NULL REFERENCES strategies(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Configuration
    start_date      DATE NOT NULL,
    end_date        DATE NOT NULL,
    initial_capital NUMERIC(15,2) NOT NULL,
    commission_pct  NUMERIC(5,4) DEFAULT 0.0010,
    slippage_pct    NUMERIC(5,4) DEFAULT 0.0005,
    
    -- Strategy snapshot (frozen at backtest time)
    strategy_snapshot JSONB NOT NULL,
    
    -- Status
    status          VARCHAR(20) DEFAULT 'pending',
    progress_pct    INTEGER DEFAULT 0,
    error_message   TEXT,
    
    -- Results (populated on completion)
    final_capital       NUMERIC(15,2),
    total_return_pct    NUMERIC(10,4),
    annualized_return_pct NUMERIC(10,4),
    sharpe_ratio        NUMERIC(6,4),
    sortino_ratio       NUMERIC(6,4),
    calmar_ratio        NUMERIC(6,4),
    max_drawdown_pct    NUMERIC(6,4),
    max_drawdown_duration_days INTEGER,
    win_rate_pct        NUMERIC(5,2),
    profit_factor       NUMERIC(6,4),
    avg_trade_pct       NUMERIC(8,4),
    avg_win_pct         NUMERIC(8,4),
    avg_loss_pct        NUMERIC(8,4),
    total_trades        INTEGER,
    winning_trades      INTEGER,
    losing_trades       INTEGER,
    avg_trade_duration_minutes INTEGER,
    
    -- Detailed results
    equity_curve        JSONB,
    monthly_returns     JSONB,
    drawdown_periods    JSONB,
    
    -- Timestamps
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    
    -- Constraints
    CONSTRAINT valid_backtest_status CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    CONSTRAINT valid_date_range CHECK (end_date > start_date),
    CONSTRAINT valid_capital CHECK (initial_capital > 0),
    CONSTRAINT valid_progress CHECK (progress_pct >= 0 AND progress_pct <= 100)
);

-- Indexes
CREATE INDEX idx_backtests_user ON backtests (user_id);
CREATE INDEX idx_backtests_strategy ON backtests (strategy_id);
CREATE INDEX idx_backtests_user_status ON backtests (user_id, status, created_at DESC);
CREATE INDEX idx_backtests_running ON backtests (status) WHERE status = 'running';
```

### 3.4 Backtest Trades Table

```sql
-- Individual trades within a backtest
CREATE TABLE backtest_trades (
    id              BIGSERIAL PRIMARY KEY,
    backtest_id     UUID NOT NULL REFERENCES backtests(id) ON DELETE CASCADE,
    
    -- Trade details
    trade_number    INTEGER NOT NULL,
    entry_date      TIMESTAMPTZ NOT NULL,
    exit_date       TIMESTAMPTZ,
    
    -- Execution
    symbol          VARCHAR(20) NOT NULL,
    side            VARCHAR(4) NOT NULL,
    quantity        NUMERIC(18,8) NOT NULL,
    entry_price     NUMERIC(18,8) NOT NULL,
    exit_price      NUMERIC(18,8),
    
    -- Costs
    commission      NUMERIC(15,8) DEFAULT 0,
    slippage        NUMERIC(15,8) DEFAULT 0,
    
    -- P&L
    gross_pnl       NUMERIC(15,8),
    net_pnl         NUMERIC(15,8),
    pnl_pct         NUMERIC(8,4),
    
    -- Context
    entry_signal    TEXT,
    exit_signal     TEXT,
    market_conditions JSONB,
    
    -- Status
    is_open         BOOLEAN DEFAULT TRUE,
    
    -- Constraints
    CONSTRAINT valid_side CHECK (side IN ('BUY', 'SELL')),
    CONSTRAINT valid_quantity CHECK (quantity > 0),
    CONSTRAINT valid_prices CHECK (entry_price > 0 AND (exit_price IS NULL OR exit_price > 0))
);

-- Indexes
CREATE INDEX idx_backtest_trades_backtest ON backtest_trades (backtest_id);
CREATE INDEX idx_backtest_trades_date ON backtest_trades (backtest_id, entry_date);

-- Partitioning by backtest_id not needed (cascade delete handles cleanup)
```

### 3.5 Portfolios Table

```sql
-- User portfolios (paper or live)
CREATE TABLE portfolios (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Configuration
    name            VARCHAR(100) NOT NULL,
    description     TEXT,
    base_currency   VARCHAR(3) DEFAULT 'EUR',
    
    -- Type
    is_paper        BOOLEAN DEFAULT TRUE,
    broker          VARCHAR(50),
    broker_account_id VARCHAR(100),
    
    -- Balances
    initial_balance NUMERIC(15,2) NOT NULL,
    cash_balance    NUMERIC(15,2) NOT NULL,
    
    -- Cached totals (updated periodically)
    positions_value NUMERIC(15,2) DEFAULT 0,
    total_value     NUMERIC(15,2),
    unrealized_pnl  NUMERIC(15,2) DEFAULT 0,
    realized_pnl    NUMERIC(15,2) DEFAULT 0,
    
    -- Status
    is_active       BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_broker CHECK (
        (is_paper = TRUE AND broker IS NULL) OR
        (is_paper = FALSE AND broker IS NOT NULL)
    ),
    CONSTRAINT valid_currency CHECK (base_currency ~ '^[A-Z]{3}$'),
    CONSTRAINT valid_balance CHECK (initial_balance >= 0)
);

-- Indexes
CREATE INDEX idx_portfolios_user ON portfolios (user_id);
CREATE INDEX idx_portfolios_user_active ON portfolios (user_id, is_active) WHERE is_active = TRUE;
CREATE INDEX idx_portfolios_broker ON portfolios (broker) WHERE is_paper = FALSE;

-- Trigger for updated_at
CREATE TRIGGER portfolios_updated_at
    BEFORE UPDATE ON portfolios
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### 3.6 Positions Table

```sql
-- Open positions in portfolios
CREATE TABLE positions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    portfolio_id    UUID NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    
    -- Asset
    symbol          VARCHAR(20) NOT NULL,
    
    -- Quantities
    quantity        NUMERIC(18,8) NOT NULL,
    average_entry_price NUMERIC(18,8) NOT NULL,
    
    -- Current state (cached, updated frequently)
    current_price   NUMERIC(18,8),
    market_value    NUMERIC(15,2),
    cost_basis      NUMERIC(15,2) NOT NULL,
    unrealized_pnl  NUMERIC(15,8),
    unrealized_pnl_pct NUMERIC(8,4),
    
    -- Realized P&L from partial closes
    realized_pnl    NUMERIC(15,8) DEFAULT 0,
    
    -- Status
    is_open         BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    opened_at       TIMESTAMPTZ DEFAULT NOW(),
    closed_at       TIMESTAMPTZ,
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_quantity CHECK (quantity != 0),
    CONSTRAINT valid_price CHECK (average_entry_price > 0),
    CONSTRAINT unique_open_position UNIQUE (portfolio_id, symbol) WHERE (is_open = TRUE)
);

-- Indexes
CREATE INDEX idx_positions_portfolio ON positions (portfolio_id);
CREATE INDEX idx_positions_portfolio_open ON positions (portfolio_id, is_open) WHERE is_open = TRUE;
CREATE INDEX idx_positions_symbol ON positions (symbol);

-- Trigger for updated_at
CREATE TRIGGER positions_updated_at
    BEFORE UPDATE ON positions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### 3.7 Trades Table

```sql
-- Executed trades (paper or live)
CREATE TABLE trades (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    portfolio_id    UUID NOT NULL REFERENCES portfolios(id) ON DELETE CASCADE,
    strategy_id     UUID REFERENCES strategies(id) ON DELETE SET NULL,
    position_id     UUID REFERENCES positions(id) ON DELETE SET NULL,
    
    -- Order details
    symbol          VARCHAR(20) NOT NULL,
    side            VARCHAR(4) NOT NULL,
    order_type      VARCHAR(20) NOT NULL,
    
    -- Quantities
    quantity        NUMERIC(18,8) NOT NULL,
    price           NUMERIC(18,8),  -- null for market orders
    
    -- Execution
    filled_quantity NUMERIC(18,8) DEFAULT 0,
    filled_price    NUMERIC(18,8),
    filled_value    NUMERIC(15,2),
    
    -- Costs
    commission      NUMERIC(15,8) DEFAULT 0,
    slippage        NUMERIC(15,8) DEFAULT 0,
    
    -- P&L (for closing trades)
    realized_pnl    NUMERIC(15,8),
    
    -- Status
    status          VARCHAR(20) DEFAULT 'pending',
    broker_order_id VARCHAR(100),
    error_message   TEXT,
    
    -- Trading mode
    is_paper        BOOLEAN NOT NULL,
    
    -- Context
    signal_reason   TEXT,
    market_conditions JSONB,
    
    -- Timestamps
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    submitted_at    TIMESTAMPTZ,
    filled_at       TIMESTAMPTZ,
    cancelled_at    TIMESTAMPTZ,
    
    -- Constraints
    CONSTRAINT valid_trade_side CHECK (side IN ('BUY', 'SELL')),
    CONSTRAINT valid_order_type CHECK (order_type IN ('MARKET', 'LIMIT', 'STOP_LOSS', 'TAKE_PROFIT', 'STOP_LIMIT')),
    CONSTRAINT valid_trade_status CHECK (status IN ('pending', 'submitted', 'partial', 'filled', 'cancelled', 'failed', 'expired')),
    CONSTRAINT valid_trade_quantity CHECK (quantity > 0),
    CONSTRAINT valid_filled_quantity CHECK (filled_quantity >= 0 AND filled_quantity <= quantity)
);

-- Indexes
CREATE INDEX idx_trades_user ON trades (user_id);
CREATE INDEX idx_trades_portfolio ON trades (portfolio_id);
CREATE INDEX idx_trades_strategy ON trades (strategy_id);
CREATE INDEX idx_trades_portfolio_time ON trades (portfolio_id, created_at DESC);
CREATE INDEX idx_trades_symbol ON trades (symbol, created_at DESC);
CREATE INDEX idx_trades_status ON trades (status) WHERE status IN ('pending', 'submitted', 'partial');
CREATE INDEX idx_trades_broker_order ON trades (broker_order_id) WHERE broker_order_id IS NOT NULL;
```

### 3.8 API Keys Table

```sql
-- Encrypted broker API keys
CREATE TABLE api_keys (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Configuration
    name            VARCHAR(100) NOT NULL,
    exchange        VARCHAR(50) NOT NULL,
    is_testnet      BOOLEAN DEFAULT TRUE,
    
    -- Encrypted credentials
    api_key_encrypted   BYTEA NOT NULL,
    api_secret_encrypted BYTEA NOT NULL,
    passphrase_encrypted BYTEA,  -- Some exchanges require passphrase
    
    -- Permissions
    permissions     VARCHAR(50)[] DEFAULT ARRAY['read'],
    
    -- Validation
    is_valid        BOOLEAN DEFAULT TRUE,
    last_validated_at TIMESTAMPTZ,
    validation_error TEXT,
    
    -- Usage tracking
    last_used_at    TIMESTAMPTZ,
    request_count   INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_exchange CHECK (exchange IN ('binance', 'kraken', 'alpaca', 'coinbase', 'degiro')),
    CONSTRAINT valid_permissions CHECK (permissions <@ ARRAY['read', 'trade', 'withdraw'])
);

-- Indexes
CREATE INDEX idx_api_keys_user ON api_keys (user_id);
CREATE INDEX idx_api_keys_user_exchange ON api_keys (user_id, exchange);
CREATE UNIQUE INDEX idx_api_keys_unique ON api_keys (user_id, exchange, is_testnet);

-- Trigger for updated_at
CREATE TRIGGER api_keys_updated_at
    BEFORE UPDATE ON api_keys
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### 3.9 Alerts Table

```sql
-- Price and condition alerts
CREATE TABLE alerts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Target
    symbol          VARCHAR(20) NOT NULL,
    
    -- Condition
    alert_type      VARCHAR(20) NOT NULL,
    condition       VARCHAR(20) NOT NULL,
    threshold       NUMERIC(18,8) NOT NULL,
    
    -- Optional indicator for indicator-based alerts
    indicator       VARCHAR(20),
    indicator_params JSONB,
    
    -- Notification
    notify_email    BOOLEAN DEFAULT TRUE,
    notify_push     BOOLEAN DEFAULT TRUE,
    message         TEXT,
    
    -- State
    is_active       BOOLEAN DEFAULT TRUE,
    is_triggered    BOOLEAN DEFAULT FALSE,
    is_recurring    BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    triggered_at    TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ,
    
    -- Constraints
    CONSTRAINT valid_alert_type CHECK (alert_type IN ('price', 'indicator', 'volume', 'change_pct')),
    CONSTRAINT valid_condition CHECK (condition IN ('above', 'below', 'crosses_above', 'crosses_below', 'equals'))
);

-- Indexes
CREATE INDEX idx_alerts_user ON alerts (user_id);
CREATE INDEX idx_alerts_active ON alerts (symbol, is_active, is_triggered) 
    WHERE is_active = TRUE AND is_triggered = FALSE;
```

### 3.10 Audit Logs Table

```sql
-- Audit trail for compliance
CREATE TABLE audit_logs (
    id              BIGSERIAL PRIMARY KEY,
    user_id         UUID REFERENCES users(id) ON DELETE SET NULL,
    
    -- Action
    action          VARCHAR(50) NOT NULL,
    resource_type   VARCHAR(50) NOT NULL,
    resource_id     UUID,
    
    -- Context
    ip_address      INET,
    user_agent      TEXT,
    
    -- Changes
    old_values      JSONB,
    new_values      JSONB,
    
    -- Metadata
    metadata        JSONB,
    
    -- Timestamp
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_action CHECK (action IN (
        'login', 'logout', 'register',
        'create', 'read', 'update', 'delete',
        'activate', 'deactivate',
        'order_placed', 'order_filled', 'order_cancelled',
        'api_key_created', 'api_key_deleted',
        'settings_changed'
    ))
);

-- Indexes
CREATE INDEX idx_audit_logs_user ON audit_logs (user_id);
CREATE INDEX idx_audit_logs_resource ON audit_logs (resource_type, resource_id);
CREATE INDEX idx_audit_logs_time ON audit_logs (created_at DESC);
CREATE INDEX idx_audit_logs_action ON audit_logs (action, created_at DESC);

-- Partition by time (monthly)
-- Note: Implement partitioning for production
```

---

## 4. TimescaleDB Schema

### 4.1 OHLCV Data (Hypertable)

```sql
-- Connect to TimescaleDB database
\c apextrade_ts

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- OHLCV candlestick data
CREATE TABLE ohlcv (
    time        TIMESTAMPTZ NOT NULL,
    symbol      TEXT NOT NULL,
    timeframe   TEXT NOT NULL,
    open        NUMERIC(18,8) NOT NULL,
    high        NUMERIC(18,8) NOT NULL,
    low         NUMERIC(18,8) NOT NULL,
    close       NUMERIC(18,8) NOT NULL,
    volume      NUMERIC(24,8) NOT NULL,
    
    -- Metadata
    source      TEXT DEFAULT 'binance',
    
    -- Constraints
    CONSTRAINT valid_ohlcv CHECK (
        high >= low AND
        high >= open AND
        high >= close AND
        low <= open AND
        low <= close AND
        volume >= 0
    )
);

-- Convert to hypertable (chunk by week)
SELECT create_hypertable('ohlcv', 'time', chunk_time_interval => INTERVAL '7 days');

-- Create unique constraint for upserts
CREATE UNIQUE INDEX idx_ohlcv_unique ON ohlcv (time, symbol, timeframe);

-- Indexes for queries
CREATE INDEX idx_ohlcv_symbol_time ON ohlcv (symbol, time DESC);
CREATE INDEX idx_ohlcv_symbol_timeframe_time ON ohlcv (symbol, timeframe, time DESC);

-- Enable compression
ALTER TABLE ohlcv SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'symbol, timeframe',
    timescaledb.compress_orderby = 'time DESC'
);

-- Add compression policy (compress chunks older than 7 days)
SELECT add_compression_policy('ohlcv', INTERVAL '7 days');

-- Add retention policy (keep 5 years of data)
SELECT add_retention_policy('ohlcv', INTERVAL '5 years');
```

### 4.2 Continuous Aggregates

```sql
-- Hourly aggregates from 1-minute data
CREATE MATERIALIZED VIEW ohlcv_1h
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', time) AS bucket,
    symbol,
    '1h' AS timeframe,
    first(open, time) AS open,
    max(high) AS high,
    min(low) AS low,
    last(close, time) AS close,
    sum(volume) AS volume,
    count(*) AS candle_count
FROM ohlcv
WHERE timeframe = '1m'
GROUP BY bucket, symbol
WITH NO DATA;

-- Refresh policy for hourly (every 10 minutes)
SELECT add_continuous_aggregate_policy('ohlcv_1h',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '10 minutes'
);

-- Daily aggregates from hourly data
CREATE MATERIALIZED VIEW ohlcv_1d
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 day', bucket) AS bucket,
    symbol,
    '1d' AS timeframe,
    first(open, bucket) AS open,
    max(high) AS high,
    min(low) AS low,
    last(close, bucket) AS close,
    sum(volume) AS volume,
    sum(candle_count) AS candle_count
FROM ohlcv_1h
GROUP BY time_bucket('1 day', bucket), symbol
WITH NO DATA;

-- Refresh policy for daily (every hour)
SELECT add_continuous_aggregate_policy('ohlcv_1d',
    start_offset => INTERVAL '3 days',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 hour'
);
```

### 4.3 Equity History (Hypertable)

```sql
-- Portfolio equity snapshots
CREATE TABLE equity_history (
    time            TIMESTAMPTZ NOT NULL,
    portfolio_id    UUID NOT NULL,
    
    -- Values
    equity_value    NUMERIC(15,2) NOT NULL,
    cash_balance    NUMERIC(15,2) NOT NULL,
    positions_value NUMERIC(15,2) NOT NULL,
    
    -- P&L
    daily_pnl       NUMERIC(15,2),
    daily_pnl_pct   NUMERIC(8,4),
    cumulative_pnl  NUMERIC(15,2),
    cumulative_pnl_pct NUMERIC(8,4),
    
    -- Drawdown
    peak_equity     NUMERIC(15,2),
    drawdown        NUMERIC(15,2),
    drawdown_pct    NUMERIC(8,4)
);

-- Convert to hypertable
SELECT create_hypertable('equity_history', 'time', chunk_time_interval => INTERVAL '30 days');

-- Indexes
CREATE INDEX idx_equity_portfolio_time ON equity_history (portfolio_id, time DESC);

-- Compression
ALTER TABLE equity_history SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'portfolio_id',
    timescaledb.compress_orderby = 'time DESC'
);

SELECT add_compression_policy('equity_history', INTERVAL '30 days');
SELECT add_retention_policy('equity_history', INTERVAL '10 years');
```

### 4.4 Tick Data (Hypertable)

```sql
-- Real-time tick data (optional, for high-frequency strategies)
CREATE TABLE tick_data (
    time        TIMESTAMPTZ NOT NULL,
    symbol      TEXT NOT NULL,
    
    -- Prices
    bid         NUMERIC(18,8),
    ask         NUMERIC(18,8),
    last_price  NUMERIC(18,8) NOT NULL,
    
    -- Volume
    last_volume NUMERIC(18,8),
    
    -- Source
    source      TEXT DEFAULT 'binance'
);

-- Convert to hypertable (chunk by day for high volume)
SELECT create_hypertable('tick_data', 'time', chunk_time_interval => INTERVAL '1 day');

-- Indexes
CREATE INDEX idx_tick_symbol_time ON tick_data (symbol, time DESC);

-- Aggressive compression (compress after 1 day)
ALTER TABLE tick_data SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'symbol',
    timescaledb.compress_orderby = 'time DESC'
);

SELECT add_compression_policy('tick_data', INTERVAL '1 day');

-- Short retention (7 days - tick data is large)
SELECT add_retention_policy('tick_data', INTERVAL '7 days');
```

---

## 5. Indexes & Constraints

### 5.1 Index Summary

| Table | Index | Type | Purpose |
|-------|-------|------|---------|
| users | email | B-tree | Login lookup |
| strategies | user_id, status | B-tree | Dashboard queries |
| strategies | entry_rules | GIN | Rule search |
| backtests | user_id, status, created_at | B-tree | History listing |
| trades | portfolio_id, created_at | B-tree | Trade history |
| trades | broker_order_id | B-tree | Order sync |
| positions | portfolio_id, is_open | B-tree | Open positions |
| ohlcv | symbol, time | B-tree | Price queries |
| ohlcv | symbol, timeframe, time | B-tree | Candle queries |

### 5.2 Foreign Key Constraints

```sql
-- All foreign keys use ON DELETE CASCADE or SET NULL
-- CASCADE: Child records deleted with parent
-- SET NULL: Child records preserved, FK nullified

-- strategies -> users: CASCADE (delete user = delete strategies)
-- backtests -> strategies: CASCADE
-- backtest_trades -> backtests: CASCADE
-- portfolios -> users: CASCADE
-- positions -> portfolios: CASCADE
-- trades -> portfolios: CASCADE
-- trades -> strategies: SET NULL (preserve trade history)
-- api_keys -> users: CASCADE
-- alerts -> users: CASCADE
-- audit_logs -> users: SET NULL (preserve audit trail)
```

### 5.3 Check Constraints Summary

| Table | Constraint | Rule |
|-------|------------|------|
| users | email_format | Valid email regex |
| strategies | valid_status | IN ('draft', 'active', 'paused', 'archived') |
| strategies | valid_symbol | Matches 'BASE/QUOTE' pattern |
| backtests | valid_date_range | end_date > start_date |
| backtests | valid_capital | initial_capital > 0 |
| trades | valid_side | IN ('BUY', 'SELL') |
| trades | valid_status | IN ('pending', 'submitted', 'filled', ...) |
| ohlcv | valid_ohlcv | high >= low, volume >= 0 |

---

## 6. Migrations

### 6.1 Alembic Configuration

```python
# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine
from alembic import context

from app.core.database import Base
from app.models import *  # Import all models

config = context.config
fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
```

### 6.2 Migration Commands

```bash
# Create migration from model changes
alembic revision --autogenerate -m "description"

# Apply all pending migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history

# View current version
alembic current
```

### 6.3 Sample Migration

```python
# alembic/versions/001_initial_schema.py
"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2026-02-01 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100)),
        sa.Column('last_name', sa.String(100)),
        sa.Column('timezone', sa.String(50), default='Europe/Paris'),
        sa.Column('preferred_currency', sa.String(3), default='EUR'),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    op.create_index('idx_users_email', 'users', ['email'])
    
    # ... more tables


def downgrade():
    op.drop_table('users')
```

---

## 7. Data Retention

### 7.1 Retention Policies

| Data Type | Retention | Reason |
|-----------|-----------|--------|
| **Users** | Forever | Account data |
| **Strategies** | Forever | User-created content |
| **Backtests** | 1 year | Can be re-run |
| **Backtest Trades** | 1 year | Detailed logs |
| **Trades** | 10 years | Regulatory (MiFID II) |
| **Audit Logs** | 7 years | Compliance |
| **OHLCV** | 5 years | Historical analysis |
| **Equity History** | 10 years | Performance tracking |
| **Tick Data** | 7 days | High volume, only for live |

### 7.2 Archival Strategy

```sql
-- Archive old backtests to cold storage (MinIO)
-- This would be a scheduled job

-- 1. Export to JSON
COPY (
    SELECT row_to_json(b)
    FROM backtests b
    WHERE created_at < NOW() - INTERVAL '1 year'
    AND status = 'completed'
) TO '/tmp/backtests_archive.json';

-- 2. Delete after verification
DELETE FROM backtests
WHERE created_at < NOW() - INTERVAL '1 year'
AND status = 'completed';
```

### 7.3 GDPR Compliance

```sql
-- User data export (GDPR Article 15)
CREATE OR REPLACE FUNCTION export_user_data(user_uuid UUID)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'user', row_to_json(u),
        'strategies', (SELECT jsonb_agg(row_to_json(s)) FROM strategies s WHERE s.user_id = user_uuid),
        'portfolios', (SELECT jsonb_agg(row_to_json(p)) FROM portfolios p WHERE p.user_id = user_uuid),
        'trades', (SELECT jsonb_agg(row_to_json(t)) FROM trades t WHERE t.user_id = user_uuid),
        'exported_at', NOW()
    )
    INTO result
    FROM users u
    WHERE u.id = user_uuid;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- User data deletion (GDPR Article 17)
-- Note: CASCADE constraints handle most deletion
CREATE OR REPLACE FUNCTION delete_user_data(user_uuid UUID)
RETURNS VOID AS $$
BEGIN
    -- Audit log entry before deletion
    INSERT INTO audit_logs (user_id, action, resource_type, resource_id)
    VALUES (user_uuid, 'delete', 'user', user_uuid);
    
    -- Delete user (cascades to related data)
    DELETE FROM users WHERE id = user_uuid;
    
    -- Anonymize remaining audit logs
    UPDATE audit_logs
    SET user_id = NULL, ip_address = NULL
    WHERE user_id = user_uuid;
END;
$$ LANGUAGE plpgsql;
```

---

*Document End*
