# ApexTrade - Technical Specification

**Version:** 1.0  
**Date:** February 1, 2026  
**Status:** Draft  
**Author:** ApexTrade Team

---

## Table of Contents

1. [Overview](#1-overview)
2. [Technology Stack](#2-technology-stack)
3. [System Components](#3-system-components)
4. [Data Models](#4-data-models)
5. [API Design](#5-api-design)
6. [Integration Specifications](#6-integration-specifications)
7. [Security Architecture](#7-security-architecture)
8. [Performance Specifications](#8-performance-specifications)
9. [Error Handling](#9-error-handling)
10. [Testing Strategy](#10-testing-strategy)

---

## 1. Overview

### 1.1 Purpose

This document provides the detailed technical specification for the ApexTrade algorithmic trading platform. It covers the technology choices, component design, data models, API contracts, and integration requirements.

### 1.2 Scope

The specification covers:
- Backend services (Python/FastAPI)
- Frontend application (Next.js)
- Database design (PostgreSQL/TimescaleDB)
- Message queue architecture (Redis/Celery)
- External integrations (brokers, data providers)
- Container orchestration (Docker)

### 1.3 Design Philosophy

| Principle | Description |
|-----------|-------------|
| **Modularity** | Loosely coupled services with clear boundaries |
| **Event-Driven** | Asynchronous processing via message queues |
| **Stateless** | API servers hold no session state |
| **Idempotency** | All operations can be safely retried |
| **Observability** | Comprehensive logging, metrics, and tracing |

---

## 2. Technology Stack

### 2.1 Backend Stack

| Component | Technology | Version | License | Purpose |
|-----------|------------|---------|---------|---------|
| **Runtime** | Python | 3.12+ | PSF | Core language |
| **Web Framework** | FastAPI | 0.109+ | MIT | REST API + WebSocket |
| **ASGI Server** | Uvicorn | 0.27+ | BSD | Production server |
| **ORM** | SQLAlchemy | 2.0+ | MIT | Database abstraction |
| **Validation** | Pydantic | 2.5+ | MIT | Data validation |
| **Task Queue** | Celery | 5.3+ | BSD | Async job processing |
| **Broker** | Redis | 7.2+ | BSD | Message broker + cache |
| **Backtesting** | Backtrader | 1.9+ | GPL | Strategy backtesting |
| **Data Analysis** | pandas | 2.1+ | BSD | Data manipulation |
| **Technical Analysis** | TA-Lib / pandas-ta | Latest | BSD | Indicators |
| **Exchange API** | CCXT | 4.2+ | MIT | Crypto exchange abstraction |
| **HTTP Client** | httpx | 0.26+ | BSD | Async HTTP requests |

### 2.2 Frontend Stack

| Component | Technology | Version | License | Purpose |
|-----------|------------|---------|---------|---------|
| **Framework** | Next.js | 14.1+ | MIT | React SSR framework |
| **Language** | TypeScript | 5.3+ | Apache 2.0 | Type safety |
| **UI Components** | shadcn/ui | Latest | MIT | Component library |
| **Styling** | Tailwind CSS | 3.4+ | MIT | Utility-first CSS |
| **State Management** | Zustand | 4.5+ | MIT | Client state |
| **Data Fetching** | TanStack Query | 5.17+ | MIT | Server state |
| **Charts** | D3.js | 7.8+ | BSD | Custom visualizations |
| **Forms** | React Hook Form | 7.49+ | MIT | Form handling |
| **Validation** | Zod | 3.22+ | MIT | Schema validation |
| **Auth** | NextAuth.js | 5.0+ | ISC | Authentication |
| **WebSocket** | socket.io-client | 4.7+ | MIT | Real-time updates |

### 2.3 Database Stack

| Component | Technology | Version | License | Purpose |
|-----------|------------|---------|---------|---------|
| **Primary DB** | PostgreSQL | 16+ | PostgreSQL | Relational data |
| **Time-Series** | TimescaleDB | 2.13+ | Apache 2.0 | OHLCV data |
| **Cache** | Redis | 7.2+ | BSD | Caching + sessions |
| **Object Storage** | MinIO | Latest | AGPL | File storage |

### 2.4 Infrastructure Stack

| Component | Technology | Version | License | Purpose |
|-----------|------------|---------|---------|---------|
| **Containerization** | Docker | 24+ | Apache 2.0 | Container runtime |
| **Orchestration** | docker-compose | 2.23+ | Apache 2.0 | Local orchestration |
| **Reverse Proxy** | Nginx | 1.25+ | BSD | Load balancing, SSL |
| **Monitoring** | Prometheus | 2.48+ | Apache 2.0 | Metrics collection |
| **Dashboards** | Grafana | 10.2+ | AGPL | Visualization |
| **Logging** | Loki | 2.9+ | AGPL | Log aggregation |

---

## 3. System Components

### 3.1 Component Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              APEXTRADE SYSTEM                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        PRESENTATION LAYER                            │   │
│  │  ┌───────────────────────────────────────────────────────────────┐  │   │
│  │  │  Next.js Frontend (SSR + CSR)                                  │  │   │
│  │  │  • Dashboard views       • Strategy builder                    │  │   │
│  │  │  • Backtest viewer       • Portfolio manager                   │  │   │
│  │  │  • Real-time charts      • Settings & config                   │  │   │
│  │  └───────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                      │                                       │
│                                      ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                          API LAYER                                   │   │
│  │  ┌───────────────────────────────────────────────────────────────┐  │   │
│  │  │  FastAPI Application                                           │  │   │
│  │  │  • REST endpoints        • WebSocket handlers                  │  │   │
│  │  │  • Authentication        • Rate limiting                       │  │   │
│  │  │  • Request validation    • Response serialization              │  │   │
│  │  └───────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                      │                                       │
│                                      ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        SERVICE LAYER                                 │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │   │
│  │  │ Rule Engine │ │  Strategy   │ │  Backtest   │ │  Portfolio  │   │   │
│  │  │   Service   │ │   Service   │ │   Service   │ │   Service   │   │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │   │
│  │  │  Execution  │ │ Market Data │ │    User     │ │   Alert     │   │   │
│  │  │   Service   │ │   Service   │ │   Service   │ │   Service   │   │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                      │                                       │
│                                      ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        WORKER LAYER                                  │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │   │
│  │  │  Backtest   │ │  Strategy   │ │  Execution  │ │ Market Data │   │   │
│  │  │   Worker    │ │   Worker    │ │   Worker    │ │   Worker    │   │   │
│  │  │  (Celery)   │ │  (Celery)   │ │  (Celery)   │ │  (Celery)   │   │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                      │                                       │
│                                      ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         DATA LAYER                                   │   │
│  │  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐              │   │
│  │  │  PostgreSQL   │ │  TimescaleDB  │ │    Redis      │              │   │
│  │  │  (Users,      │ │  (OHLCV,      │ │  (Cache,      │              │   │
│  │  │   Strategies) │ │   Ticks)      │ │   Sessions)   │              │   │
│  │  └───────────────┘ └───────────────┘ └───────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Service Definitions

#### 3.2.1 Rule Engine Service

**Purpose:** Evaluate trading conditions and generate signals.

```python
# Interface
class RuleEngineService:
    def create_rule(rule: RuleDefinition) -> Rule
    def evaluate_rule(rule_id: str, market_data: MarketData) -> Signal
    def validate_rule(rule: RuleDefinition) -> ValidationResult
    def get_rule_dependencies(rule_id: str) -> List[Indicator]
```

**Responsibilities:**
- Parse rule definitions (JSON/DSL)
- Evaluate conditions against market data
- Support logical operators (AND, OR, NOT)
- Calculate required technical indicators
- Generate BUY/SELL/HOLD signals

**Rule Definition Schema:**
```json
{
  "id": "rule_001",
  "name": "RSI Oversold Buy",
  "conditions": [
    {
      "indicator": "RSI",
      "params": {"period": 14},
      "operator": "less_than",
      "value": 30
    }
  ],
  "logic": "AND",
  "signal": "BUY"
}
```

#### 3.2.2 Strategy Service

**Purpose:** Manage trading strategies composed of multiple rules.

```python
# Interface
class StrategyService:
    def create_strategy(strategy: StrategyDefinition) -> Strategy
    def update_strategy(strategy_id: str, updates: dict) -> Strategy
    def activate_strategy(strategy_id: str, mode: TradingMode) -> None
    def deactivate_strategy(strategy_id: str) -> None
    def get_strategy_performance(strategy_id: str) -> PerformanceMetrics
```

**Responsibilities:**
- CRUD operations for strategies
- Version control for strategy changes
- Strategy state management (draft, active, paused)
- Performance tracking per strategy

**Strategy Definition Schema:**
```json
{
  "id": "strategy_001",
  "name": "Mean Reversion BTC",
  "description": "Buy when RSI oversold, sell when overbought",
  "asset": "BTC/USDT",
  "timeframe": "1h",
  "entry_rules": ["rule_001"],
  "exit_rules": ["rule_002"],
  "risk_management": {
    "stop_loss_pct": 2.0,
    "take_profit_pct": 5.0,
    "max_position_size": 0.1
  }
}
```

#### 3.2.3 Backtest Service

**Purpose:** Simulate strategies against historical data.

```python
# Interface
class BacktestService:
    def run_backtest(config: BacktestConfig) -> BacktestResult
    def get_backtest_status(backtest_id: str) -> BacktestStatus
    def cancel_backtest(backtest_id: str) -> None
    def get_backtest_trades(backtest_id: str) -> List[Trade]
```

**Responsibilities:**
- Fetch historical data for date range
- Execute strategy logic on each candle
- Track simulated portfolio state
- Calculate performance metrics
- Generate trade log

**Backtest Configuration:**
```json
{
  "strategy_id": "strategy_001",
  "start_date": "2024-01-01",
  "end_date": "2025-01-01",
  "initial_capital": 10000,
  "commission_pct": 0.1,
  "slippage_pct": 0.05
}
```

**Backtest Result:**
```json
{
  "backtest_id": "bt_abc123",
  "total_return_pct": 45.2,
  "sharpe_ratio": 1.8,
  "max_drawdown_pct": 12.5,
  "win_rate_pct": 58.3,
  "total_trades": 143,
  "profit_factor": 1.95,
  "equity_curve": [...],
  "trades": [...]
}
```

#### 3.2.4 Execution Service

**Purpose:** Execute orders on brokers/exchanges.

```python
# Interface
class ExecutionService:
    def place_order(order: OrderRequest) -> Order
    def cancel_order(order_id: str) -> None
    def get_order_status(order_id: str) -> OrderStatus
    def get_open_orders() -> List[Order]
    def sync_positions() -> List[Position]
```

**Responsibilities:**
- Translate signals to broker orders
- Handle order lifecycle (placed, filled, cancelled)
- Implement retry logic for failed orders
- Sync positions with broker
- Enforce risk limits before execution

**Order Types Supported:**
| Type | Description |
|------|-------------|
| `MARKET` | Execute immediately at best price |
| `LIMIT` | Execute at specified price or better |
| `STOP_LOSS` | Trigger market order when price reaches level |
| `TAKE_PROFIT` | Trigger limit order when price reaches target |

#### 3.2.5 Market Data Service

**Purpose:** Ingest and serve market data.

```python
# Interface
class MarketDataService:
    def get_ohlcv(symbol: str, timeframe: str, start: datetime, end: datetime) -> DataFrame
    def get_ticker(symbol: str) -> Ticker
    def subscribe_ticker(symbol: str, callback: Callable) -> Subscription
    def get_supported_symbols() -> List[Symbol]
```

**Responsibilities:**
- Fetch historical OHLCV data
- Stream real-time price updates
- Cache frequently accessed data
- Normalize data across providers
- Handle rate limiting

**Data Sources Priority:**
1. **Crypto:** CCXT (Binance, Kraken)
2. **Stocks:** yfinance (historical), Alpaca (real-time)
3. **Forex:** Alpha Vantage, ECB rates

#### 3.2.6 Portfolio Service

**Purpose:** Track portfolio state and performance.

```python
# Interface
class PortfolioService:
    def get_portfolio(user_id: str) -> Portfolio
    def get_positions(user_id: str) -> List[Position]
    def calculate_pnl(user_id: str, period: str) -> PnLReport
    def get_equity_curve(user_id: str, start: datetime, end: datetime) -> List[EquityPoint]
```

**Responsibilities:**
- Track open positions
- Calculate unrealized P&L
- Historical equity tracking
- Asset allocation breakdown
- Multi-currency support (EUR, USD)

### 3.3 Worker Definitions

#### 3.3.1 Backtest Worker

**Queue:** `backtest_queue`  
**Concurrency:** 4 workers  
**Timeout:** 10 minutes

```python
@celery.task(bind=True, max_retries=3)
def run_backtest_task(self, backtest_config: dict):
    """
    Execute backtest in background.
    Publishes progress updates to Redis pub/sub.
    """
    pass
```

#### 3.3.2 Strategy Worker

**Queue:** `strategy_queue`  
**Concurrency:** 2 workers  
**Timeout:** 30 seconds

```python
@celery.task(bind=True)
def evaluate_strategy_task(self, strategy_id: str, market_data: dict):
    """
    Evaluate strategy rules against new market data.
    Generates signals for execution.
    """
    pass
```

#### 3.3.3 Execution Worker

**Queue:** `execution_queue`  
**Concurrency:** 1 worker (serial execution)  
**Timeout:** 60 seconds

```python
@celery.task(bind=True, max_retries=5)
def execute_order_task(self, order_request: dict):
    """
    Place order on broker.
    Retries on transient failures.
    """
    pass
```

#### 3.3.4 Market Data Worker

**Queue:** `market_data_queue`  
**Concurrency:** 2 workers  
**Timeout:** 5 minutes

```python
@celery.task(bind=True)
def sync_historical_data_task(self, symbol: str, timeframe: str, days: int):
    """
    Fetch and store historical OHLCV data.
    """
    pass
```

---

## 4. Data Models

### 4.1 Entity Relationship Diagram

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│    User     │───────│  Portfolio  │───────│  Position   │
└─────────────┘       └─────────────┘       └─────────────┘
      │                                            │
      │                                            │
      ▼                                            ▼
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│  Strategy   │───────│    Rule     │       │    Trade    │
└─────────────┘       └─────────────┘       └─────────────┘
      │                     │
      │                     │
      ▼                     ▼
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│  Backtest   │       │  Indicator  │       │  OHLCV      │
└─────────────┘       └─────────────┘       └─────────────┘
```

### 4.2 Core Entity Definitions

#### 4.2.1 User

```python
class User(Base):
    __tablename__ = "users"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    
    # Profile
    first_name: Mapped[str] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="Europe/Paris")
    preferred_currency: Mapped[str] = mapped_column(String(3), default="EUR")
    
    # Settings
    is_active: Mapped[bool] = mapped_column(default=True)
    is_verified: Mapped[bool] = mapped_column(default=False)
    mfa_enabled: Mapped[bool] = mapped_column(default=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    last_login_at: Mapped[datetime] = mapped_column(nullable=True)
    
    # Relationships
    portfolios: Mapped[List["Portfolio"]] = relationship(back_populates="user")
    strategies: Mapped[List["Strategy"]] = relationship(back_populates="user")
    api_keys: Mapped[List["ApiKey"]] = relationship(back_populates="user")
```

#### 4.2.2 Strategy

```python
class Strategy(Base):
    __tablename__ = "strategies"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    
    # Definition
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text, nullable=True)
    version: Mapped[int] = mapped_column(default=1)
    
    # Configuration
    asset_symbol: Mapped[str] = mapped_column(String(20))  # e.g., "BTC/USDT"
    timeframe: Mapped[str] = mapped_column(String(5))  # e.g., "1h", "4h", "1d"
    entry_rules: Mapped[dict] = mapped_column(JSONB)  # Rule definitions
    exit_rules: Mapped[dict] = mapped_column(JSONB)
    
    # Risk Management
    stop_loss_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=True)
    take_profit_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=True)
    max_position_size_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=10.0)
    max_drawdown_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=True)
    
    # State
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft, active, paused, archived
    trading_mode: Mapped[str] = mapped_column(String(20), nullable=True)  # paper, live
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    activated_at: Mapped[datetime] = mapped_column(nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="strategies")
    backtests: Mapped[List["Backtest"]] = relationship(back_populates="strategy")
    trades: Mapped[List["Trade"]] = relationship(back_populates="strategy")
```

#### 4.2.3 Backtest

```python
class Backtest(Base):
    __tablename__ = "backtests"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    strategy_id: Mapped[UUID] = mapped_column(ForeignKey("strategies.id"), index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    
    # Configuration
    start_date: Mapped[date] = mapped_column()
    end_date: Mapped[date] = mapped_column()
    initial_capital: Mapped[Decimal] = mapped_column(Numeric(15, 2))
    commission_pct: Mapped[Decimal] = mapped_column(Numeric(5, 4), default=0.001)
    slippage_pct: Mapped[Decimal] = mapped_column(Numeric(5, 4), default=0.0005)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, running, completed, failed
    progress_pct: Mapped[int] = mapped_column(default=0)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Results (populated on completion)
    final_capital: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=True)
    total_return_pct: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=True)
    sharpe_ratio: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=True)
    sortino_ratio: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=True)
    max_drawdown_pct: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=True)
    win_rate_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=True)
    profit_factor: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=True)
    total_trades: Mapped[int] = mapped_column(nullable=True)
    
    # Detailed results stored in JSONB
    equity_curve: Mapped[dict] = mapped_column(JSONB, nullable=True)
    monthly_returns: Mapped[dict] = mapped_column(JSONB, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    started_at: Mapped[datetime] = mapped_column(nullable=True)
    completed_at: Mapped[datetime] = mapped_column(nullable=True)
    
    # Relationships
    strategy: Mapped["Strategy"] = relationship(back_populates="backtests")
    trades: Mapped[List["BacktestTrade"]] = relationship(back_populates="backtest")
```

#### 4.2.4 Trade

```python
class Trade(Base):
    __tablename__ = "trades"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    strategy_id: Mapped[UUID] = mapped_column(ForeignKey("strategies.id"), index=True)
    portfolio_id: Mapped[UUID] = mapped_column(ForeignKey("portfolios.id"), index=True)
    
    # Order Details
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    side: Mapped[str] = mapped_column(String(4))  # BUY, SELL
    order_type: Mapped[str] = mapped_column(String(20))  # MARKET, LIMIT, STOP_LOSS
    
    # Quantities
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 8))
    price: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=True)  # null for market orders
    filled_quantity: Mapped[Decimal] = mapped_column(Numeric(18, 8), default=0)
    filled_price: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=True)
    
    # Costs
    commission: Mapped[Decimal] = mapped_column(Numeric(15, 8), default=0)
    slippage: Mapped[Decimal] = mapped_column(Numeric(15, 8), default=0)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, open, filled, cancelled, failed
    broker_order_id: Mapped[str] = mapped_column(String(100), nullable=True)
    
    # P&L (for closing trades)
    realized_pnl: Mapped[Decimal] = mapped_column(Numeric(15, 8), nullable=True)
    
    # Trading Mode
    is_paper: Mapped[bool] = mapped_column(default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    submitted_at: Mapped[datetime] = mapped_column(nullable=True)
    filled_at: Mapped[datetime] = mapped_column(nullable=True)
    
    # Relationships
    strategy: Mapped["Strategy"] = relationship(back_populates="trades")
    portfolio: Mapped["Portfolio"] = relationship(back_populates="trades")
```

#### 4.2.5 Portfolio

```python
class Portfolio(Base):
    __tablename__ = "portfolios"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    
    # Configuration
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text, nullable=True)
    base_currency: Mapped[str] = mapped_column(String(3), default="EUR")
    
    # Type
    is_paper: Mapped[bool] = mapped_column(default=True)  # Paper vs Live
    broker: Mapped[str] = mapped_column(String(50), nullable=True)  # binance, alpaca, etc.
    
    # Balances
    initial_balance: Mapped[Decimal] = mapped_column(Numeric(15, 2))
    cash_balance: Mapped[Decimal] = mapped_column(Numeric(15, 2))
    
    # Status
    is_active: Mapped[bool] = mapped_column(default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="portfolios")
    positions: Mapped[List["Position"]] = relationship(back_populates="portfolio")
    trades: Mapped[List["Trade"]] = relationship(back_populates="portfolio")
```

#### 4.2.6 Position

```python
class Position(Base):
    __tablename__ = "positions"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    portfolio_id: Mapped[UUID] = mapped_column(ForeignKey("portfolios.id"), index=True)
    
    # Asset
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    
    # Quantities
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 8))
    average_entry_price: Mapped[Decimal] = mapped_column(Numeric(18, 8))
    
    # Current State
    current_price: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=True)
    unrealized_pnl: Mapped[Decimal] = mapped_column(Numeric(15, 8), nullable=True)
    unrealized_pnl_pct: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=True)
    
    # Status
    is_open: Mapped[bool] = mapped_column(default=True)
    
    # Timestamps
    opened_at: Mapped[datetime] = mapped_column(default=func.now())
    closed_at: Mapped[datetime] = mapped_column(nullable=True)
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
    
    # Relationships
    portfolio: Mapped["Portfolio"] = relationship(back_populates="positions")
```

### 4.3 TimescaleDB Hypertables

#### 4.3.1 OHLCV Data

```sql
CREATE TABLE ohlcv (
    time        TIMESTAMPTZ NOT NULL,
    symbol      TEXT NOT NULL,
    timeframe   TEXT NOT NULL,
    open        NUMERIC(18, 8) NOT NULL,
    high        NUMERIC(18, 8) NOT NULL,
    low         NUMERIC(18, 8) NOT NULL,
    close       NUMERIC(18, 8) NOT NULL,
    volume      NUMERIC(24, 8) NOT NULL,
    source      TEXT DEFAULT 'binance',
    
    PRIMARY KEY (time, symbol, timeframe)
);

-- Convert to hypertable
SELECT create_hypertable('ohlcv', 'time');

-- Create indexes
CREATE INDEX idx_ohlcv_symbol ON ohlcv (symbol, time DESC);
CREATE INDEX idx_ohlcv_timeframe ON ohlcv (symbol, timeframe, time DESC);

-- Add compression policy (compress data older than 7 days)
ALTER TABLE ohlcv SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'symbol,timeframe'
);
SELECT add_compression_policy('ohlcv', INTERVAL '7 days');

-- Add retention policy (drop data older than 5 years)
SELECT add_retention_policy('ohlcv', INTERVAL '5 years');
```

#### 4.3.2 Equity History

```sql
CREATE TABLE equity_history (
    time            TIMESTAMPTZ NOT NULL,
    portfolio_id    UUID NOT NULL,
    equity_value    NUMERIC(15, 2) NOT NULL,
    cash_balance    NUMERIC(15, 2) NOT NULL,
    positions_value NUMERIC(15, 2) NOT NULL,
    daily_pnl       NUMERIC(15, 2),
    daily_pnl_pct   NUMERIC(8, 4),
    
    PRIMARY KEY (time, portfolio_id)
);

SELECT create_hypertable('equity_history', 'time');

CREATE INDEX idx_equity_portfolio ON equity_history (portfolio_id, time DESC);
```

---

## 5. API Design

### 5.1 API Conventions

| Aspect | Convention |
|--------|------------|
| **Base URL** | `/api/v1` |
| **Format** | JSON |
| **Authentication** | Bearer JWT token |
| **Pagination** | `?page=1&limit=20` |
| **Sorting** | `?sort=-created_at` (prefix `-` for desc) |
| **Filtering** | `?status=active&symbol=BTC/USDT` |
| **Errors** | RFC 7807 Problem Details |

### 5.2 Authentication Endpoints

```
POST   /api/v1/auth/register      # Create new account
POST   /api/v1/auth/login         # Get access token
POST   /api/v1/auth/refresh       # Refresh access token
POST   /api/v1/auth/logout        # Invalidate token
POST   /api/v1/auth/forgot        # Request password reset
POST   /api/v1/auth/reset         # Reset password
GET    /api/v1/auth/me            # Get current user
```

### 5.3 Strategy Endpoints

```
GET    /api/v1/strategies                    # List user strategies
POST   /api/v1/strategies                    # Create strategy
GET    /api/v1/strategies/{id}               # Get strategy details
PUT    /api/v1/strategies/{id}               # Update strategy
DELETE /api/v1/strategies/{id}               # Delete strategy
POST   /api/v1/strategies/{id}/activate      # Activate for trading
POST   /api/v1/strategies/{id}/deactivate    # Pause trading
POST   /api/v1/strategies/{id}/clone         # Duplicate strategy
GET    /api/v1/strategies/{id}/versions      # Version history
```

### 5.4 Backtest Endpoints

```
GET    /api/v1/backtests                     # List user backtests
POST   /api/v1/backtests                     # Start new backtest
GET    /api/v1/backtests/{id}                # Get backtest status/results
DELETE /api/v1/backtests/{id}                # Cancel running backtest
GET    /api/v1/backtests/{id}/trades         # Get backtest trade log
GET    /api/v1/backtests/{id}/equity         # Get equity curve data
GET    /api/v1/backtests/{id}/report         # Download PDF report
```

### 5.5 Portfolio Endpoints

```
GET    /api/v1/portfolios                    # List user portfolios
POST   /api/v1/portfolios                    # Create portfolio
GET    /api/v1/portfolios/{id}               # Get portfolio details
PUT    /api/v1/portfolios/{id}               # Update portfolio
DELETE /api/v1/portfolios/{id}               # Delete portfolio
GET    /api/v1/portfolios/{id}/positions     # Get open positions
GET    /api/v1/portfolios/{id}/trades        # Get trade history
GET    /api/v1/portfolios/{id}/performance   # Get performance metrics
GET    /api/v1/portfolios/{id}/equity        # Get equity curve
```

### 5.6 Market Data Endpoints

```
GET    /api/v1/market/symbols                # List available symbols
GET    /api/v1/market/ticker/{symbol}        # Get current price
GET    /api/v1/market/ohlcv/{symbol}         # Get OHLCV data
GET    /api/v1/market/orderbook/{symbol}     # Get order book (live)
```

### 5.7 WebSocket Events

```
# Client -> Server
{
  "action": "subscribe",
  "channel": "ticker",
  "symbols": ["BTC/USDT", "ETH/USDT"]
}

{
  "action": "subscribe",
  "channel": "portfolio",
  "portfolio_id": "uuid"
}

# Server -> Client
{
  "channel": "ticker",
  "data": {
    "symbol": "BTC/USDT",
    "price": 45230.50,
    "change_24h_pct": 2.35,
    "timestamp": "2026-02-01T10:30:00Z"
  }
}

{
  "channel": "trade",
  "data": {
    "trade_id": "uuid",
    "symbol": "BTC/USDT",
    "side": "BUY",
    "quantity": 0.1,
    "price": 45230.50,
    "status": "filled"
  }
}

{
  "channel": "backtest_progress",
  "data": {
    "backtest_id": "uuid",
    "progress_pct": 45,
    "current_date": "2024-06-15"
  }
}
```

---

## 6. Integration Specifications

### 6.1 CCXT (Crypto Exchanges)

**Supported Exchanges:**
- Binance (primary)
- Kraken
- Coinbase Pro

**Integration Pattern:**
```python
import ccxt

class BinanceAdapter:
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'sandbox': testnet,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot'
            }
        })
    
    async def fetch_ohlcv(self, symbol: str, timeframe: str, since: int, limit: int):
        return await self.exchange.fetch_ohlcv(symbol, timeframe, since, limit)
    
    async def create_order(self, symbol: str, order_type: str, side: str, amount: float, price: float = None):
        return await self.exchange.create_order(symbol, order_type, side, amount, price)
    
    async def fetch_balance(self):
        return await self.exchange.fetch_balance()
```

### 6.2 Alpaca (US Stocks)

**Note:** Paper trading only for non-US residents.

```python
from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient

class AlpacaAdapter:
    def __init__(self, api_key: str, api_secret: str, paper: bool = True):
        self.trading = TradingClient(api_key, api_secret, paper=paper)
        self.data = StockHistoricalDataClient(api_key, api_secret)
    
    def get_account(self):
        return self.trading.get_account()
    
    def place_order(self, symbol: str, qty: float, side: str, order_type: str):
        from alpaca.trading.requests import MarketOrderRequest
        request = MarketOrderRequest(symbol=symbol, qty=qty, side=side, type=order_type)
        return self.trading.submit_order(request)
```

### 6.3 yfinance (Historical Data)

```python
import yfinance as yf

class YFinanceAdapter:
    def fetch_ohlcv(self, symbol: str, start: str, end: str, interval: str = "1d"):
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start, end=end, interval=interval)
        return df[['Open', 'High', 'Low', 'Close', 'Volume']]
    
    def get_ticker_info(self, symbol: str):
        ticker = yf.Ticker(symbol)
        return ticker.info
```

### 6.4 Rate Limiting Strategy

| Provider | Rate Limit | Strategy |
|----------|------------|----------|
| Binance | 1200 req/min | Token bucket with 20 req/s burst |
| Kraken | 15 req/s | Fixed delay 67ms between calls |
| Alpaca | 200 req/min | Token bucket with 3 req/s burst |
| yfinance | ~2000 req/hour | Cache aggressively, batch requests |

---

## 7. Security Architecture

### 7.1 Authentication Flow

```
┌──────────┐         ┌──────────┐         ┌──────────┐
│  Client  │         │   API    │         │   DB     │
└────┬─────┘         └────┬─────┘         └────┬─────┘
     │                    │                    │
     │  POST /auth/login  │                    │
     │  {email, password} │                    │
     │───────────────────▶│                    │
     │                    │  Verify password   │
     │                    │───────────────────▶│
     │                    │◀───────────────────│
     │                    │                    │
     │  {access_token,    │                    │
     │   refresh_token}   │                    │
     │◀───────────────────│                    │
     │                    │                    │
     │  GET /strategies   │                    │
     │  Authorization:    │                    │
     │  Bearer {token}    │                    │
     │───────────────────▶│                    │
     │                    │  Validate JWT      │
     │                    │  Extract user_id   │
     │                    │───────────────────▶│
     │  {strategies: [...]}                    │
     │◀───────────────────│◀───────────────────│
```

### 7.2 JWT Token Structure

```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user_uuid",
    "email": "user@example.com",
    "iat": 1706780400,
    "exp": 1706784000,
    "type": "access"
  }
}
```

**Token Lifetimes:**
| Token Type | Lifetime | Storage |
|------------|----------|---------|
| Access Token | 15 minutes | Memory only |
| Refresh Token | 7 days | HttpOnly cookie |

### 7.3 API Key Encryption

Broker API keys are encrypted at rest using AES-256-GCM:

```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

class ApiKeyEncryption:
    def __init__(self, master_key: bytes):
        self.fernet = Fernet(master_key)
    
    def encrypt(self, api_key: str) -> bytes:
        return self.fernet.encrypt(api_key.encode())
    
    def decrypt(self, encrypted_key: bytes) -> str:
        return self.fernet.decrypt(encrypted_key).decode()
```

### 7.4 Security Headers

```python
# FastAPI middleware
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```

### 7.5 Input Validation

All API inputs validated with Pydantic:

```python
from pydantic import BaseModel, Field, validator
from decimal import Decimal

class CreateStrategyRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    asset_symbol: str = Field(..., pattern=r'^[A-Z]{2,10}/[A-Z]{2,10}$')
    timeframe: str = Field(..., pattern=r'^[1-9][0-9]?[mhd]$')
    stop_loss_pct: Decimal = Field(None, ge=0, le=100)
    take_profit_pct: Decimal = Field(None, ge=0, le=1000)
    
    @validator('asset_symbol')
    def validate_supported_symbol(cls, v):
        supported = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']  # etc.
        if v not in supported:
            raise ValueError(f'Symbol {v} not supported')
        return v
```

---

## 8. Performance Specifications

### 8.1 Caching Strategy

| Data Type | Cache Location | TTL | Invalidation |
|-----------|----------------|-----|--------------|
| User session | Redis | 15 min | On logout |
| Ticker prices | Redis | 5 sec | On new price |
| OHLCV (historical) | TimescaleDB + Redis | 1 hour | On new candle close |
| Strategy config | Redis | 5 min | On update |
| Portfolio state | Redis | 30 sec | On trade |

### 8.2 Database Indexes

```sql
-- PostgreSQL indexes
CREATE INDEX idx_strategies_user_status ON strategies (user_id, status);
CREATE INDEX idx_trades_portfolio_time ON trades (portfolio_id, created_at DESC);
CREATE INDEX idx_trades_strategy ON trades (strategy_id, created_at DESC);
CREATE INDEX idx_backtests_user_status ON backtests (user_id, status, created_at DESC);

-- TimescaleDB continuous aggregates
CREATE MATERIALIZED VIEW ohlcv_1h
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', time) AS bucket,
    symbol,
    first(open, time) AS open,
    max(high) AS high,
    min(low) AS low,
    last(close, time) AS close,
    sum(volume) AS volume
FROM ohlcv
WHERE timeframe = '1m'
GROUP BY bucket, symbol;
```

### 8.3 Connection Pooling

```python
# SQLAlchemy async pool configuration
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Redis connection pool
import redis.asyncio as redis

redis_pool = redis.ConnectionPool.from_url(
    REDIS_URL,
    max_connections=50,
    decode_responses=True
)
```

---

## 9. Error Handling

### 9.1 Error Response Format (RFC 7807)

```json
{
  "type": "https://apextrade.io/errors/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "The 'stop_loss_pct' field must be between 0 and 100",
  "instance": "/api/v1/strategies",
  "errors": [
    {
      "field": "stop_loss_pct",
      "message": "Value must be between 0 and 100",
      "code": "value_error.number.not_le"
    }
  ]
}
```

### 9.2 Error Codes

| Code Range | Category | Example |
|------------|----------|---------|
| 400-499 | Client errors | Invalid input, unauthorized |
| 500-599 | Server errors | Database unavailable |
| 1000-1999 | Authentication | Token expired, invalid credentials |
| 2000-2999 | Strategy | Invalid rule, strategy not found |
| 3000-3999 | Backtest | Insufficient data, timeout |
| 4000-4999 | Execution | Order rejected, insufficient funds |
| 5000-5999 | Market Data | Symbol not found, rate limited |

### 9.3 Retry Policies

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((ConnectionError, TimeoutError))
)
async def place_order_with_retry(exchange, order):
    return await exchange.create_order(**order)
```

---

## 10. Testing Strategy

### 10.1 Test Pyramid

```
                    ┌───────────────┐
                    │     E2E       │  10%
                    │   (Playwright)│
                    └───────┬───────┘
                            │
                ┌───────────┴───────────┐
                │    Integration        │  30%
                │  (pytest + testcontainers)
                └───────────┬───────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │              Unit Tests               │  60%
        │         (pytest + hypothesis)         │
        └───────────────────────────────────────┘
```

### 10.2 Test Categories

| Category | Framework | Coverage Target |
|----------|-----------|-----------------|
| Unit Tests | pytest + hypothesis | 80% |
| Integration Tests | pytest + testcontainers | 60% |
| API Tests | pytest + httpx | 90% endpoints |
| E2E Tests | Playwright | Critical paths |
| Performance Tests | Locust | Baseline metrics |
| Strategy Tests | Custom backtest harness | All strategies |

### 10.3 Test Fixtures

```python
# conftest.py
import pytest
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("timescale/timescaledb:latest-pg16") as postgres:
        yield postgres

@pytest.fixture(scope="session")
def redis_container():
    with RedisContainer("redis:7-alpine") as redis:
        yield redis

@pytest.fixture
def test_client(postgres_container, redis_container):
    # Configure app with test containers
    from app.main import app
    from httpx import AsyncClient
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
```

### 10.4 Strategy Testing Framework

```python
class StrategyTestCase:
    """Base class for strategy unit tests."""
    
    def __init__(self, strategy: Strategy, test_data: pd.DataFrame):
        self.strategy = strategy
        self.data = test_data
    
    def test_signal_generation(self):
        """Verify strategy generates expected signals."""
        signals = self.strategy.generate_signals(self.data)
        assert signals is not None
        assert len(signals) == len(self.data)
    
    def test_no_lookahead_bias(self):
        """Verify strategy doesn't use future data."""
        # Run strategy with partial data
        for i in range(100, len(self.data)):
            partial_data = self.data.iloc[:i]
            signal = self.strategy.generate_signal(partial_data)
            # Signal should only depend on data up to index i
            assert self._verify_no_future_data(signal, i)
    
    def test_deterministic(self):
        """Verify strategy produces same results on same data."""
        result1 = self.strategy.generate_signals(self.data)
        result2 = self.strategy.generate_signals(self.data)
        pd.testing.assert_frame_equal(result1, result2)
```

---

## Appendix A: Environment Variables

```bash
# Application
APP_NAME=apextrade
APP_ENV=development  # development, staging, production
DEBUG=true
SECRET_KEY=your-secret-key-min-32-chars

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/apextrade
TIMESCALE_URL=postgresql+asyncpg://user:pass@localhost:5433/apextrade_ts

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1

# JWT
JWT_SECRET_KEY=your-jwt-secret
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Encryption
API_KEY_ENCRYPTION_KEY=your-32-byte-key

# External APIs
BINANCE_API_KEY=
BINANCE_API_SECRET=
BINANCE_TESTNET=true

ALPACA_API_KEY=
ALPACA_API_SECRET=
ALPACA_PAPER=true

# Monitoring
PROMETHEUS_ENABLED=true
SENTRY_DSN=

# Feature Flags
FEATURE_LIVE_TRADING=false
FEATURE_MULTI_EXCHANGE=false
```

---

## Appendix B: Error Codes Reference

| Code | Name | HTTP Status | Description |
|------|------|-------------|-------------|
| 1001 | AUTH_INVALID_CREDENTIALS | 401 | Email or password incorrect |
| 1002 | AUTH_TOKEN_EXPIRED | 401 | JWT token has expired |
| 1003 | AUTH_TOKEN_INVALID | 401 | JWT token is malformed |
| 1004 | AUTH_REFRESH_INVALID | 401 | Refresh token invalid or expired |
| 2001 | STRATEGY_NOT_FOUND | 404 | Strategy does not exist |
| 2002 | STRATEGY_INVALID_RULES | 422 | Rule definition is invalid |
| 2003 | STRATEGY_ALREADY_ACTIVE | 409 | Strategy is already running |
| 3001 | BACKTEST_INSUFFICIENT_DATA | 422 | Not enough historical data |
| 3002 | BACKTEST_TIMEOUT | 504 | Backtest took too long |
| 3003 | BACKTEST_CANCELLED | 200 | Backtest was cancelled by user |
| 4001 | EXECUTION_INSUFFICIENT_FUNDS | 422 | Not enough balance |
| 4002 | EXECUTION_ORDER_REJECTED | 422 | Broker rejected order |
| 4003 | EXECUTION_BROKER_ERROR | 502 | Broker API error |
| 5001 | MARKET_SYMBOL_NOT_FOUND | 404 | Trading pair not supported |
| 5002 | MARKET_RATE_LIMITED | 429 | Too many requests to data provider |

---

*Document End*
