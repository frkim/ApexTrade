# ApexTrade - API Reference

**Version:** 1.0  
**Base URL:** `https://api.apextrade.io/api/v1`  
**Date:** February 1, 2026

---

## Table of Contents

1. [Overview](#1-overview)
2. [Authentication](#2-authentication)
3. [Strategies API](#3-strategies-api)
4. [Backtests API](#4-backtests-api)
5. [Portfolios API](#5-portfolios-api)
6. [Market Data API](#6-market-data-api)
7. [Trades API](#7-trades-api)
8. [Users API](#8-users-api)
9. [WebSocket API](#9-websocket-api)
10. [Error Handling](#10-error-handling)

---

## 1. Overview

### 1.1 API Conventions

| Aspect | Convention |
|--------|------------|
| **Protocol** | HTTPS only |
| **Format** | JSON (Content-Type: application/json) |
| **Authentication** | Bearer JWT token |
| **Versioning** | URL path (`/api/v1/`) |
| **Rate Limiting** | 100 requests/minute per user |
| **Pagination** | `?page=1&limit=20` (max 100) |
| **Sorting** | `?sort=-created_at` (prefix `-` for descending) |
| **Filtering** | `?status=active&symbol=BTC/USDT` |
| **Date Format** | ISO 8601 (`2026-02-01T10:30:00Z`) |

### 1.2 Common Headers

```http
Content-Type: application/json
Authorization: Bearer <access_token>
Accept: application/json
X-Request-ID: <uuid>  # Optional, for tracing
```

### 1.3 Response Envelope

**Success Response:**
```json
{
  "data": { ... },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2026-02-01T10:30:00Z"
  }
}
```

**Paginated Response:**
```json
{
  "data": [ ... ],
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 156,
    "total_pages": 8
  }
}
```

**Error Response:**
```json
{
  "error": {
    "type": "https://apextrade.io/errors/validation-error",
    "title": "Validation Error",
    "status": 422,
    "detail": "Invalid value for 'stop_loss_pct'",
    "instance": "/api/v1/strategies",
    "errors": [
      {
        "field": "stop_loss_pct",
        "message": "Value must be between 0 and 100",
        "code": "value_error.number.not_le"
      }
    ]
  }
}
```

---

## 2. Authentication

### 2.1 Register

Create a new user account.

```http
POST /api/v1/auth/register
```

**Request Body:**
```json
{
  "email": "trader@example.com",
  "password": "SecureP@ssw0rd!",
  "first_name": "Jean",
  "last_name": "Dupont",
  "timezone": "Europe/Paris"
}
```

**Response (201 Created):**
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "trader@example.com",
    "first_name": "Jean",
    "last_name": "Dupont",
    "is_verified": false,
    "created_at": "2026-02-01T10:30:00Z"
  }
}
```

### 2.2 Login

Authenticate and receive tokens.

```http
POST /api/v1/auth/login
```

**Request Body:**
```json
{
  "email": "trader@example.com",
  "password": "SecureP@ssw0rd!"
}
```

**Response (200 OK):**
```json
{
  "data": {
    "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 900,
    "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4..."
  }
}
```

### 2.3 Refresh Token

Get a new access token using refresh token.

```http
POST /api/v1/auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4..."
}
```

**Response (200 OK):**
```json
{
  "data": {
    "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 900
  }
}
```

### 2.4 Logout

Invalidate the refresh token.

```http
POST /api/v1/auth/logout
Authorization: Bearer <access_token>
```

**Response (204 No Content)**

### 2.5 Get Current User

```http
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "trader@example.com",
    "first_name": "Jean",
    "last_name": "Dupont",
    "timezone": "Europe/Paris",
    "preferred_currency": "EUR",
    "is_verified": true,
    "mfa_enabled": false,
    "created_at": "2026-02-01T10:30:00Z",
    "last_login_at": "2026-02-01T14:00:00Z"
  }
}
```

---

## 3. Strategies API

### 3.1 List Strategies

```http
GET /api/v1/strategies
Authorization: Bearer <access_token>
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | int | Page number (default: 1) |
| `limit` | int | Items per page (default: 20, max: 100) |
| `status` | string | Filter by status: `draft`, `active`, `paused`, `archived` |
| `asset` | string | Filter by asset symbol (e.g., `BTC/USDT`) |
| `sort` | string | Sort field: `created_at`, `name`, `status` |

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "str_abc123",
      "name": "RSI Mean Reversion BTC",
      "description": "Buy when RSI < 30, sell when RSI > 70",
      "asset_symbol": "BTC/USDT",
      "timeframe": "1h",
      "status": "active",
      "trading_mode": "paper",
      "version": 3,
      "performance": {
        "total_return_pct": 12.5,
        "win_rate_pct": 58.3,
        "total_trades": 24
      },
      "created_at": "2026-01-15T08:00:00Z",
      "updated_at": "2026-02-01T10:30:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 5,
    "total_pages": 1
  }
}
```

### 3.2 Create Strategy

```http
POST /api/v1/strategies
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "RSI Mean Reversion BTC",
  "description": "Buy when RSI < 30, sell when RSI > 70",
  "asset_symbol": "BTC/USDT",
  "timeframe": "1h",
  "entry_rules": {
    "logic": "AND",
    "conditions": [
      {
        "indicator": "RSI",
        "params": { "period": 14 },
        "operator": "less_than",
        "value": 30
      }
    ]
  },
  "exit_rules": {
    "logic": "OR",
    "conditions": [
      {
        "indicator": "RSI",
        "params": { "period": 14 },
        "operator": "greater_than",
        "value": 70
      },
      {
        "type": "stop_loss",
        "value": 2.0
      },
      {
        "type": "take_profit",
        "value": 5.0
      }
    ]
  },
  "risk_management": {
    "stop_loss_pct": 2.0,
    "take_profit_pct": 5.0,
    "max_position_size_pct": 10.0,
    "max_drawdown_pct": 15.0
  }
}
```

**Response (201 Created):**
```json
{
  "data": {
    "id": "str_abc123",
    "name": "RSI Mean Reversion BTC",
    "status": "draft",
    "version": 1,
    "created_at": "2026-02-01T10:30:00Z"
  }
}
```

### 3.3 Get Strategy

```http
GET /api/v1/strategies/{strategy_id}
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "data": {
    "id": "str_abc123",
    "name": "RSI Mean Reversion BTC",
    "description": "Buy when RSI < 30, sell when RSI > 70",
    "asset_symbol": "BTC/USDT",
    "timeframe": "1h",
    "status": "active",
    "trading_mode": "paper",
    "version": 3,
    "entry_rules": {
      "logic": "AND",
      "conditions": [
        {
          "indicator": "RSI",
          "params": { "period": 14 },
          "operator": "less_than",
          "value": 30
        }
      ]
    },
    "exit_rules": { ... },
    "risk_management": {
      "stop_loss_pct": 2.0,
      "take_profit_pct": 5.0,
      "max_position_size_pct": 10.0,
      "max_drawdown_pct": 15.0
    },
    "created_at": "2026-01-15T08:00:00Z",
    "updated_at": "2026-02-01T10:30:00Z",
    "activated_at": "2026-01-20T09:00:00Z"
  }
}
```

### 3.4 Update Strategy

```http
PUT /api/v1/strategies/{strategy_id}
Authorization: Bearer <access_token>
```

**Request Body (partial update):**
```json
{
  "name": "RSI Mean Reversion BTC v2",
  "entry_rules": {
    "logic": "AND",
    "conditions": [
      {
        "indicator": "RSI",
        "params": { "period": 14 },
        "operator": "less_than",
        "value": 25
      }
    ]
  }
}
```

**Response (200 OK):**
```json
{
  "data": {
    "id": "str_abc123",
    "name": "RSI Mean Reversion BTC v2",
    "version": 4,
    "updated_at": "2026-02-01T11:00:00Z"
  }
}
```

### 3.5 Delete Strategy

```http
DELETE /api/v1/strategies/{strategy_id}
Authorization: Bearer <access_token>
```

**Response (204 No Content)**

### 3.6 Activate Strategy

Start paper or live trading.

```http
POST /api/v1/strategies/{strategy_id}/activate
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "mode": "paper",
  "portfolio_id": "pf_xyz789"
}
```

**Response (200 OK):**
```json
{
  "data": {
    "id": "str_abc123",
    "status": "active",
    "trading_mode": "paper",
    "activated_at": "2026-02-01T11:00:00Z"
  }
}
```

### 3.7 Deactivate Strategy

Stop trading.

```http
POST /api/v1/strategies/{strategy_id}/deactivate
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "data": {
    "id": "str_abc123",
    "status": "paused",
    "trading_mode": null
  }
}
```

---

## 4. Backtests API

### 4.1 List Backtests

```http
GET /api/v1/backtests
Authorization: Bearer <access_token>
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `strategy_id` | uuid | Filter by strategy |
| `status` | string | `pending`, `running`, `completed`, `failed` |
| `sort` | string | `-created_at` (default) |

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "bt_123abc",
      "strategy_id": "str_abc123",
      "strategy_name": "RSI Mean Reversion BTC",
      "status": "completed",
      "start_date": "2024-01-01",
      "end_date": "2025-01-01",
      "initial_capital": 10000.00,
      "final_capital": 14520.00,
      "total_return_pct": 45.20,
      "sharpe_ratio": 1.82,
      "max_drawdown_pct": 12.50,
      "total_trades": 143,
      "created_at": "2026-02-01T10:00:00Z",
      "completed_at": "2026-02-01T10:02:30Z"
    }
  ],
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 12
  }
}
```

### 4.2 Create Backtest

Start a new backtest.

```http
POST /api/v1/backtests
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "strategy_id": "str_abc123",
  "start_date": "2024-01-01",
  "end_date": "2025-01-01",
  "initial_capital": 10000.00,
  "commission_pct": 0.1,
  "slippage_pct": 0.05
}
```

**Response (202 Accepted):**
```json
{
  "data": {
    "id": "bt_123abc",
    "status": "pending",
    "created_at": "2026-02-01T10:00:00Z"
  }
}
```

### 4.3 Get Backtest

```http
GET /api/v1/backtests/{backtest_id}
Authorization: Bearer <access_token>
```

**Response (200 OK) — Running:**
```json
{
  "data": {
    "id": "bt_123abc",
    "status": "running",
    "progress_pct": 45,
    "current_date": "2024-06-15"
  }
}
```

**Response (200 OK) — Completed:**
```json
{
  "data": {
    "id": "bt_123abc",
    "strategy_id": "str_abc123",
    "status": "completed",
    "start_date": "2024-01-01",
    "end_date": "2025-01-01",
    "initial_capital": 10000.00,
    "final_capital": 14520.00,
    
    "metrics": {
      "total_return_pct": 45.20,
      "annualized_return_pct": 45.20,
      "sharpe_ratio": 1.82,
      "sortino_ratio": 2.15,
      "max_drawdown_pct": 12.50,
      "max_drawdown_duration_days": 23,
      "win_rate_pct": 58.30,
      "profit_factor": 1.95,
      "avg_trade_pct": 0.32,
      "avg_win_pct": 2.10,
      "avg_loss_pct": -1.05,
      "total_trades": 143,
      "winning_trades": 83,
      "losing_trades": 60,
      "avg_trade_duration_hours": 18.5
    },
    
    "monthly_returns": {
      "2024-01": 3.2,
      "2024-02": -1.5,
      "2024-03": 5.8,
      "...": "..."
    },
    
    "created_at": "2026-02-01T10:00:00Z",
    "started_at": "2026-02-01T10:00:05Z",
    "completed_at": "2026-02-01T10:02:30Z"
  }
}
```

### 4.4 Get Backtest Trades

```http
GET /api/v1/backtests/{backtest_id}/trades
Authorization: Bearer <access_token>
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | int | Page number |
| `limit` | int | Trades per page |
| `side` | string | `BUY` or `SELL` |

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": 1,
      "date": "2024-01-15T14:00:00Z",
      "side": "BUY",
      "price": 42500.00,
      "quantity": 0.1,
      "value": 4250.00,
      "commission": 4.25,
      "signal_reason": "RSI crossed below 30"
    },
    {
      "id": 2,
      "date": "2024-01-18T09:00:00Z",
      "side": "SELL",
      "price": 44100.00,
      "quantity": 0.1,
      "value": 4410.00,
      "commission": 4.41,
      "pnl": 151.34,
      "pnl_pct": 3.56,
      "signal_reason": "RSI crossed above 70"
    }
  ],
  "meta": {
    "page": 1,
    "limit": 50,
    "total": 143
  }
}
```

### 4.5 Get Backtest Equity Curve

```http
GET /api/v1/backtests/{backtest_id}/equity
Authorization: Bearer <access_token>
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `interval` | string | `daily`, `weekly`, `monthly` |

**Response (200 OK):**
```json
{
  "data": {
    "dates": ["2024-01-01", "2024-01-02", "2024-01-03", "..."],
    "equity": [10000.00, 10050.00, 9980.00, "..."],
    "drawdown": [0, 0, -0.70, "..."],
    "benchmark": [10000.00, 10020.00, 10015.00, "..."]
  }
}
```

### 4.6 Cancel Backtest

```http
DELETE /api/v1/backtests/{backtest_id}
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "data": {
    "id": "bt_123abc",
    "status": "cancelled"
  }
}
```

---

## 5. Portfolios API

### 5.1 List Portfolios

```http
GET /api/v1/portfolios
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "pf_xyz789",
      "name": "Main Paper Portfolio",
      "is_paper": true,
      "broker": null,
      "base_currency": "EUR",
      "initial_balance": 10000.00,
      "current_value": 10850.00,
      "cash_balance": 5000.00,
      "positions_value": 5850.00,
      "unrealized_pnl": 350.00,
      "unrealized_pnl_pct": 3.50,
      "total_return_pct": 8.50,
      "is_active": true,
      "created_at": "2026-01-01T00:00:00Z"
    }
  ]
}
```

### 5.2 Create Portfolio

```http
POST /api/v1/portfolios
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "Crypto Paper Portfolio",
  "is_paper": true,
  "base_currency": "EUR",
  "initial_balance": 10000.00
}
```

**Response (201 Created):**
```json
{
  "data": {
    "id": "pf_abc123",
    "name": "Crypto Paper Portfolio",
    "is_paper": true,
    "initial_balance": 10000.00,
    "cash_balance": 10000.00,
    "created_at": "2026-02-01T10:00:00Z"
  }
}
```

### 5.3 Get Portfolio

```http
GET /api/v1/portfolios/{portfolio_id}
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "data": {
    "id": "pf_xyz789",
    "name": "Main Paper Portfolio",
    "is_paper": true,
    "broker": null,
    "base_currency": "EUR",
    "initial_balance": 10000.00,
    "cash_balance": 5000.00,
    
    "summary": {
      "current_value": 10850.00,
      "positions_value": 5850.00,
      "unrealized_pnl": 350.00,
      "unrealized_pnl_pct": 6.36,
      "realized_pnl": 500.00,
      "total_return": 850.00,
      "total_return_pct": 8.50,
      "day_pnl": 120.00,
      "day_pnl_pct": 1.12
    },
    
    "allocation": [
      { "asset": "BTC/USDT", "value": 3500.00, "pct": 32.26 },
      { "asset": "ETH/USDT", "value": 2350.00, "pct": 21.66 },
      { "asset": "Cash", "value": 5000.00, "pct": 46.08 }
    ],
    
    "active_strategies": [
      {
        "id": "str_abc123",
        "name": "RSI Mean Reversion BTC"
      }
    ],
    
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-02-01T10:30:00Z"
  }
}
```

### 5.4 Get Portfolio Positions

```http
GET /api/v1/portfolios/{portfolio_id}/positions
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "pos_123",
      "symbol": "BTC/USDT",
      "quantity": 0.08,
      "average_entry_price": 41250.00,
      "current_price": 43750.00,
      "market_value": 3500.00,
      "cost_basis": 3300.00,
      "unrealized_pnl": 200.00,
      "unrealized_pnl_pct": 6.06,
      "weight_pct": 32.26,
      "opened_at": "2026-01-20T14:00:00Z"
    },
    {
      "id": "pos_124",
      "symbol": "ETH/USDT",
      "quantity": 1.0,
      "average_entry_price": 2200.00,
      "current_price": 2350.00,
      "market_value": 2350.00,
      "cost_basis": 2200.00,
      "unrealized_pnl": 150.00,
      "unrealized_pnl_pct": 6.82,
      "weight_pct": 21.66,
      "opened_at": "2026-01-25T09:00:00Z"
    }
  ]
}
```

### 5.5 Get Portfolio Equity History

```http
GET /api/v1/portfolios/{portfolio_id}/equity
Authorization: Bearer <access_token>
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `start` | date | Start date (ISO 8601) |
| `end` | date | End date (ISO 8601) |
| `interval` | string | `hourly`, `daily`, `weekly` |

**Response (200 OK):**
```json
{
  "data": {
    "dates": ["2026-01-01", "2026-01-02", "..."],
    "equity": [10000.00, 10050.00, "..."],
    "cash": [10000.00, 9500.00, "..."],
    "positions": [0, 550.00, "..."],
    "drawdown_pct": [0, 0, "..."]
  }
}
```

### 5.6 Get Portfolio Performance

```http
GET /api/v1/portfolios/{portfolio_id}/performance
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "data": {
    "total_return_pct": 8.50,
    "mtd_return_pct": 3.20,
    "ytd_return_pct": 8.50,
    
    "sharpe_ratio": 1.45,
    "sortino_ratio": 1.82,
    "max_drawdown_pct": 5.20,
    "volatility_pct": 12.50,
    
    "win_rate_pct": 62.50,
    "profit_factor": 2.10,
    "avg_trade_pct": 0.85,
    
    "total_trades": 48,
    "winning_trades": 30,
    "losing_trades": 18,
    
    "best_day_pct": 4.50,
    "worst_day_pct": -2.10,
    "avg_daily_return_pct": 0.28,
    
    "by_asset": [
      {
        "symbol": "BTC/USDT",
        "return_pct": 12.30,
        "trades": 24,
        "win_rate_pct": 65.00
      },
      {
        "symbol": "ETH/USDT",
        "return_pct": 4.20,
        "trades": 24,
        "win_rate_pct": 58.33
      }
    ]
  }
}
```

---

## 6. Market Data API

### 6.1 List Symbols

```http
GET /api/v1/market/symbols
Authorization: Bearer <access_token>
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `exchange` | string | Filter by exchange (`binance`, `kraken`) |
| `type` | string | `spot`, `futures` |
| `quote` | string | Quote currency (`USDT`, `EUR`) |

**Response (200 OK):**
```json
{
  "data": [
    {
      "symbol": "BTC/USDT",
      "base": "BTC",
      "quote": "USDT",
      "exchange": "binance",
      "type": "spot",
      "price_precision": 2,
      "quantity_precision": 6,
      "min_quantity": 0.00001,
      "status": "active"
    },
    {
      "symbol": "ETH/USDT",
      "base": "ETH",
      "quote": "USDT",
      "exchange": "binance",
      "type": "spot",
      "price_precision": 2,
      "quantity_precision": 5,
      "min_quantity": 0.0001,
      "status": "active"
    }
  ]
}
```

### 6.2 Get Ticker

Current price for a symbol.

```http
GET /api/v1/market/ticker/{symbol}
Authorization: Bearer <access_token>
```

**Example:** `GET /api/v1/market/ticker/BTC-USDT`

**Response (200 OK):**
```json
{
  "data": {
    "symbol": "BTC/USDT",
    "price": 43750.50,
    "bid": 43749.00,
    "ask": 43752.00,
    "volume_24h": 15234.56,
    "change_24h": 820.50,
    "change_24h_pct": 1.91,
    "high_24h": 44200.00,
    "low_24h": 42800.00,
    "timestamp": "2026-02-01T10:30:00Z"
  }
}
```

### 6.3 Get OHLCV Data

Historical candlestick data.

```http
GET /api/v1/market/ohlcv/{symbol}
Authorization: Bearer <access_token>
```

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `timeframe` | string | Yes | `1m`, `5m`, `15m`, `1h`, `4h`, `1d`, `1w` |
| `start` | datetime | No | Start time (ISO 8601) |
| `end` | datetime | No | End time (ISO 8601) |
| `limit` | int | No | Number of candles (default: 500, max: 1000) |

**Example:** `GET /api/v1/market/ohlcv/BTC-USDT?timeframe=1h&limit=24`

**Response (200 OK):**
```json
{
  "data": {
    "symbol": "BTC/USDT",
    "timeframe": "1h",
    "candles": [
      {
        "timestamp": "2026-02-01T00:00:00Z",
        "open": 43200.00,
        "high": 43450.00,
        "low": 43100.00,
        "close": 43380.00,
        "volume": 125.45
      },
      {
        "timestamp": "2026-02-01T01:00:00Z",
        "open": 43380.00,
        "high": 43600.00,
        "low": 43300.00,
        "close": 43550.00,
        "volume": 98.32
      }
    ]
  },
  "meta": {
    "count": 24,
    "first": "2026-01-31T01:00:00Z",
    "last": "2026-02-01T00:00:00Z"
  }
}
```

### 6.4 Get Order Book

Live order book (WebSocket recommended for real-time).

```http
GET /api/v1/market/orderbook/{symbol}
Authorization: Bearer <access_token>
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `depth` | int | Number of levels (default: 20, max: 100) |

**Response (200 OK):**
```json
{
  "data": {
    "symbol": "BTC/USDT",
    "timestamp": "2026-02-01T10:30:00Z",
    "bids": [
      [43749.00, 1.25],
      [43748.00, 2.50],
      [43747.00, 0.75]
    ],
    "asks": [
      [43752.00, 0.80],
      [43753.00, 1.10],
      [43754.00, 3.20]
    ]
  }
}
```

---

## 7. Trades API

### 7.1 List Trades

```http
GET /api/v1/trades
Authorization: Bearer <access_token>
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `portfolio_id` | uuid | Filter by portfolio |
| `strategy_id` | uuid | Filter by strategy |
| `symbol` | string | Filter by symbol |
| `side` | string | `BUY` or `SELL` |
| `status` | string | `pending`, `open`, `filled`, `cancelled`, `failed` |
| `start` | datetime | Start date |
| `end` | datetime | End date |
| `sort` | string | `-created_at` (default) |

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "trd_abc123",
      "portfolio_id": "pf_xyz789",
      "strategy_id": "str_abc123",
      "strategy_name": "RSI Mean Reversion BTC",
      "symbol": "BTC/USDT",
      "side": "BUY",
      "order_type": "MARKET",
      "quantity": 0.05,
      "filled_quantity": 0.05,
      "price": null,
      "filled_price": 43250.00,
      "value": 2162.50,
      "commission": 2.16,
      "status": "filled",
      "is_paper": true,
      "signal_reason": "RSI crossed below 30",
      "created_at": "2026-02-01T10:25:00Z",
      "filled_at": "2026-02-01T10:25:01Z"
    }
  ],
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 48
  }
}
```

### 7.2 Get Trade

```http
GET /api/v1/trades/{trade_id}
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "data": {
    "id": "trd_abc123",
    "portfolio_id": "pf_xyz789",
    "strategy_id": "str_abc123",
    "strategy_name": "RSI Mean Reversion BTC",
    "symbol": "BTC/USDT",
    "side": "BUY",
    "order_type": "MARKET",
    "quantity": 0.05,
    "filled_quantity": 0.05,
    "price": null,
    "filled_price": 43250.00,
    "value": 2162.50,
    "commission": 2.16,
    "slippage": 0.50,
    "status": "filled",
    "broker_order_id": "binance_123456789",
    "is_paper": true,
    "signal_reason": "RSI crossed below 30",
    "market_conditions": {
      "rsi_14": 28.5,
      "sma_20": 43100.00,
      "volume_24h": 15000.00
    },
    "created_at": "2026-02-01T10:25:00Z",
    "submitted_at": "2026-02-01T10:25:00Z",
    "filled_at": "2026-02-01T10:25:01Z"
  }
}
```

### 7.3 Manual Trade (Paper Only)

Place a manual trade in paper portfolio.

```http
POST /api/v1/trades
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "portfolio_id": "pf_xyz789",
  "symbol": "ETH/USDT",
  "side": "BUY",
  "order_type": "MARKET",
  "quantity": 1.0
}
```

**Response (201 Created):**
```json
{
  "data": {
    "id": "trd_def456",
    "status": "filled",
    "filled_price": 2350.00,
    "value": 2350.00,
    "filled_at": "2026-02-01T10:30:00Z"
  }
}
```

---

## 8. Users API

### 8.1 Get User Profile

```http
GET /api/v1/users/me
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "trader@example.com",
    "first_name": "Jean",
    "last_name": "Dupont",
    "timezone": "Europe/Paris",
    "preferred_currency": "EUR",
    "is_verified": true,
    "mfa_enabled": false,
    "notification_preferences": {
      "email_trade_executed": true,
      "email_daily_summary": true,
      "push_price_alerts": true
    },
    "created_at": "2026-01-01T00:00:00Z"
  }
}
```

### 8.2 Update User Profile

```http
PUT /api/v1/users/me
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "first_name": "Jean-Pierre",
  "timezone": "Europe/Paris",
  "preferred_currency": "EUR",
  "notification_preferences": {
    "email_trade_executed": true,
    "email_daily_summary": false
  }
}
```

**Response (200 OK):**
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "first_name": "Jean-Pierre",
    "updated_at": "2026-02-01T10:30:00Z"
  }
}
```

### 8.3 List API Keys

```http
GET /api/v1/users/me/api-keys
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "key_abc123",
      "name": "Binance Testnet",
      "exchange": "binance",
      "is_testnet": true,
      "permissions": ["read", "trade"],
      "created_at": "2026-01-15T00:00:00Z",
      "last_used_at": "2026-02-01T10:00:00Z"
    }
  ]
}
```

### 8.4 Add API Key

```http
POST /api/v1/users/me/api-keys
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "name": "Binance Testnet",
  "exchange": "binance",
  "api_key": "vmPUZE6mv9SD5VNHk4HlWFsOr6aKE2zvsw0MuIgwCIPy6utIco14y7Ju91duEh8A",
  "api_secret": "NhqPtmdSJYdKjVHjA7PZj4Mge3R5YNiP1e3UZjInClVN65XAbvqqM6A7H5fATj0j",
  "is_testnet": true
}
```

**Response (201 Created):**
```json
{
  "data": {
    "id": "key_abc123",
    "name": "Binance Testnet",
    "exchange": "binance",
    "is_testnet": true,
    "created_at": "2026-02-01T10:00:00Z"
  }
}
```

### 8.5 Delete API Key

```http
DELETE /api/v1/users/me/api-keys/{key_id}
Authorization: Bearer <access_token>
```

**Response (204 No Content)**

---

## 9. WebSocket API

### 9.1 Connection

```javascript
const socket = new WebSocket('wss://api.apextrade.io/ws');

// Authenticate after connection
socket.onopen = () => {
  socket.send(JSON.stringify({
    action: 'authenticate',
    token: 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...'
  }));
};
```

### 9.2 Subscribe to Channels

**Ticker Updates:**
```json
{
  "action": "subscribe",
  "channel": "ticker",
  "symbols": ["BTC/USDT", "ETH/USDT"]
}
```

**Portfolio Updates:**
```json
{
  "action": "subscribe",
  "channel": "portfolio",
  "portfolio_id": "pf_xyz789"
}
```

**Backtest Progress:**
```json
{
  "action": "subscribe",
  "channel": "backtest",
  "backtest_id": "bt_123abc"
}
```

**Strategy Signals:**
```json
{
  "action": "subscribe",
  "channel": "strategy",
  "strategy_id": "str_abc123"
}
```

### 9.3 Event Messages

**Ticker Update:**
```json
{
  "channel": "ticker",
  "event": "update",
  "data": {
    "symbol": "BTC/USDT",
    "price": 43750.50,
    "change_24h_pct": 1.91,
    "timestamp": "2026-02-01T10:30:00.123Z"
  }
}
```

**Trade Executed:**
```json
{
  "channel": "portfolio",
  "event": "trade_executed",
  "data": {
    "trade_id": "trd_abc123",
    "symbol": "BTC/USDT",
    "side": "BUY",
    "quantity": 0.05,
    "price": 43250.00,
    "pnl": null,
    "timestamp": "2026-02-01T10:25:01Z"
  }
}
```

**Portfolio Update:**
```json
{
  "channel": "portfolio",
  "event": "update",
  "data": {
    "portfolio_id": "pf_xyz789",
    "current_value": 10852.50,
    "unrealized_pnl": 352.50,
    "day_pnl": 122.50,
    "timestamp": "2026-02-01T10:30:00Z"
  }
}
```

**Backtest Progress:**
```json
{
  "channel": "backtest",
  "event": "progress",
  "data": {
    "backtest_id": "bt_123abc",
    "progress_pct": 45,
    "current_date": "2024-06-15",
    "current_equity": 11250.00
  }
}
```

**Backtest Complete:**
```json
{
  "channel": "backtest",
  "event": "complete",
  "data": {
    "backtest_id": "bt_123abc",
    "status": "completed",
    "total_return_pct": 45.20,
    "sharpe_ratio": 1.82
  }
}
```

**Strategy Signal:**
```json
{
  "channel": "strategy",
  "event": "signal",
  "data": {
    "strategy_id": "str_abc123",
    "signal": "BUY",
    "symbol": "BTC/USDT",
    "price": 43100.00,
    "reason": "RSI crossed below 30",
    "confidence": 0.85,
    "timestamp": "2026-02-01T10:30:00Z"
  }
}
```

### 9.4 Unsubscribe

```json
{
  "action": "unsubscribe",
  "channel": "ticker",
  "symbols": ["BTC/USDT"]
}
```

### 9.5 Ping/Pong

Keep connection alive:
```json
{
  "action": "ping"
}
```

Response:
```json
{
  "action": "pong",
  "timestamp": "2026-02-01T10:30:00Z"
}
```

---

## 10. Error Handling

### 10.1 HTTP Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Successful GET, PUT, POST (returning data) |
| 201 | Created | Successful resource creation |
| 202 | Accepted | Async operation started (backtest) |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Malformed request syntax |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Valid auth but insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource state conflict |
| 422 | Unprocessable Entity | Validation errors |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error |
| 502 | Bad Gateway | Broker API error |
| 503 | Service Unavailable | Maintenance or overload |
| 504 | Gateway Timeout | Broker API timeout |

### 10.2 Error Types

| Type | Description |
|------|-------------|
| `validation_error` | Request body failed validation |
| `authentication_error` | Auth token issues |
| `authorization_error` | Permission denied |
| `not_found_error` | Resource not found |
| `conflict_error` | State conflict (e.g., already active) |
| `rate_limit_error` | Too many requests |
| `broker_error` | External broker API error |
| `internal_error` | Unexpected server error |

### 10.3 Error Response Examples

**Validation Error (422):**
```json
{
  "error": {
    "type": "https://apextrade.io/errors/validation-error",
    "title": "Validation Error",
    "status": 422,
    "detail": "Request validation failed",
    "instance": "/api/v1/strategies",
    "errors": [
      {
        "field": "asset_symbol",
        "message": "Invalid symbol format. Expected 'BASE/QUOTE'",
        "code": "value_error.str.regex"
      },
      {
        "field": "stop_loss_pct",
        "message": "Value must be between 0 and 100",
        "code": "value_error.number.not_le"
      }
    ]
  }
}
```

**Authentication Error (401):**
```json
{
  "error": {
    "type": "https://apextrade.io/errors/authentication-error",
    "title": "Authentication Failed",
    "status": 401,
    "detail": "Token has expired",
    "code": 1002
  }
}
```

**Rate Limit Error (429):**
```json
{
  "error": {
    "type": "https://apextrade.io/errors/rate-limit-error",
    "title": "Rate Limit Exceeded",
    "status": 429,
    "detail": "You have exceeded the rate limit of 100 requests per minute",
    "retry_after": 45
  }
}
```

**Broker Error (502):**
```json
{
  "error": {
    "type": "https://apextrade.io/errors/broker-error",
    "title": "Broker API Error",
    "status": 502,
    "detail": "Binance API returned error: Insufficient balance",
    "broker": "binance",
    "broker_code": -2010
  }
}
```

### 10.4 Rate Limits

| Endpoint Category | Limit | Window |
|-------------------|-------|--------|
| Authentication | 10 requests | 1 minute |
| Read operations | 100 requests | 1 minute |
| Write operations | 30 requests | 1 minute |
| Backtest creation | 5 requests | 1 minute |
| WebSocket connections | 5 concurrent | - |

Rate limit headers:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 85
X-RateLimit-Reset: 1706785860
```

---

## Appendix A: Supported Indicators

| Indicator | Code | Parameters |
|-----------|------|------------|
| Relative Strength Index | `RSI` | `period` (default: 14) |
| Simple Moving Average | `SMA` | `period` |
| Exponential Moving Average | `EMA` | `period` |
| MACD | `MACD` | `fast`, `slow`, `signal` |
| Bollinger Bands | `BBANDS` | `period`, `std_dev` |
| Average True Range | `ATR` | `period` |
| Stochastic | `STOCH` | `k_period`, `d_period` |
| Volume | `VOLUME` | - |
| Price | `PRICE` | - (close price) |

---

## Appendix B: Condition Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `greater_than` | Value > threshold | RSI > 70 |
| `less_than` | Value < threshold | RSI < 30 |
| `equals` | Value == threshold | - |
| `crosses_above` | Value crosses above threshold | RSI crosses above 30 |
| `crosses_below` | Value crosses below threshold | RSI crosses below 70 |
| `between` | Value in range | RSI between 40-60 |

---

*Document End*
