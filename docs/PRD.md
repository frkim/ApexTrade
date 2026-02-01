# ApexTrade - Product Requirements Document (PRD)

**Version:** 1.0  
**Date:** February 1, 2026  
**Status:** Draft  
**Author:** ApexTrade Team

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Vision & Goals](#2-vision--goals)
3. [User Personas](#3-user-personas)
4. [Functional Requirements](#4-functional-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [User Stories](#6-user-stories)
7. [Success Metrics](#7-success-metrics)
8. [Roadmap](#8-roadmap)
9. [Constraints & Assumptions](#9-constraints--assumptions)
10. [Glossary](#10-glossary)

---

## 1. Executive Summary

### 1.1 Product Overview

**ApexTrade** is a comprehensive algorithmic trading platform designed for retail and semi-professional traders. The platform enables users to create, test, and execute automated trading strategies across multiple asset classes including stocks, cryptocurrencies, and forex.

### 1.2 Problem Statement

Retail traders face several challenges:
- **Manual trading is time-consuming** and emotionally driven
- **Backtesting tools are often expensive** or require advanced programming skills
- **No unified platform** exists that combines strategy creation, testing, and execution
- **Professional-grade tools** are inaccessible to individual traders

### 1.3 Solution

ApexTrade provides:
- **Visual rule engine** for creating trading strategies without coding
- **Comprehensive backtesting** with historical data
- **Paper trading simulation** for risk-free testing
- **Live execution** via broker integrations
- **Professional dashboards** for portfolio monitoring and analytics

### 1.4 Target Market

- **Primary:** Retail traders in France/EU seeking automated trading solutions
- **Secondary:** Algo trading enthusiasts and developers
- **Tertiary:** Small trading firms and prop traders

---

## 2. Vision & Goals

### 2.1 Product Vision

*"Democratize algorithmic trading by providing professional-grade tools that are accessible, affordable, and easy to use for every trader."*

### 2.2 Strategic Goals

| Goal | Description | Timeline |
|------|-------------|----------|
| **G1** | Launch MVP with core backtesting and paper trading | Q1 2026 |
| **G2** | Integrate live trading with EU-compatible brokers | Q2 2026 |
| **G3** | Achieve 1,000 active users | Q3 2026 |
| **G4** | Expand to multi-asset support (stocks, crypto, forex) | Q4 2026 |

### 2.3 Design Principles

1. **Simplicity First** — Complex functionality with simple UX
2. **Transparency** — All trading decisions are explainable and auditable
3. **Safety** — Multiple safeguards to prevent catastrophic losses
4. **Performance** — Sub-second strategy execution and real-time data
5. **Open Source** — Community-driven development with OSS stack

---

## 3. User Personas

### 3.1 Persona 1: Alexandre — The Weekend Trader

| Attribute | Details |
|-----------|---------|
| **Age** | 35 |
| **Occupation** | Software Engineer |
| **Location** | Lyon, France |
| **Trading Experience** | 3 years, manual trading |
| **Technical Skills** | High (Python, data analysis) |
| **Goals** | Automate strategies, reduce screen time |
| **Pain Points** | No time for manual trading, emotional decisions |
| **Preferred Assets** | Crypto, Tech stocks |

**Quote:** *"I have good trading ideas but no time to execute them consistently."*

### 3.2 Persona 2: Marie — The Cautious Investor

| Attribute | Details |
|-----------|---------|
| **Age** | 45 |
| **Occupation** | Financial Analyst |
| **Location** | Paris, France |
| **Trading Experience** | 10+ years |
| **Technical Skills** | Medium (Excel, basic SQL) |
| **Goals** | Protect capital, steady returns |
| **Pain Points** | Fear of automation, needs validation |
| **Preferred Assets** | ETFs, Blue-chip stocks |

**Quote:** *"I want to test strategies thoroughly before risking real money."*

### 3.3 Persona 3: Thomas — The Algo Enthusiast

| Attribute | Details |
|-----------|---------|
| **Age** | 28 |
| **Occupation** | Data Scientist |
| **Location** | Bordeaux, France |
| **Trading Experience** | 5 years, algorithmic |
| **Technical Skills** | Very High (Python, ML, APIs) |
| **Goals** | Build and optimize complex strategies |
| **Pain Points** | Existing platforms are too limiting |
| **Preferred Assets** | Crypto, Derivatives |

**Quote:** *"I need full control over my strategies and access to raw data."*

---

## 4. Functional Requirements

### 4.1 Core Features

#### 4.1.1 Rule Engine (F-RE)

| ID | Requirement | Priority | Description |
|----|-------------|----------|-------------|
| F-RE-001 | Create trading rules | Must | Users can define buy/sell conditions using a visual builder |
| F-RE-002 | Condition operators | Must | Support AND, OR, NOT logical operators |
| F-RE-003 | Technical indicators | Must | Built-in RSI, MACD, SMA, EMA, Bollinger Bands |
| F-RE-004 | Price conditions | Must | Compare price to fixed values or moving averages |
| F-RE-005 | Volume conditions | Should | Filter by volume thresholds |
| F-RE-006 | Time-based rules | Should | Trade only during specific hours/days |
| F-RE-007 | Custom expressions | Could | Advanced users can write custom formulas |

#### 4.1.2 Trading Strategies (F-TS)

| ID | Requirement | Priority | Description |
|----|-------------|----------|-------------|
| F-TS-001 | Strategy templates | Must | Pre-built strategies (Mean Reversion, Trend Following, etc.) |
| F-TS-002 | Strategy parameters | Must | Configurable parameters for each strategy |
| F-TS-003 | Multi-asset strategies | Should | Single strategy across multiple assets |
| F-TS-004 | Strategy versioning | Should | Track changes and rollback |
| F-TS-005 | Strategy sharing | Could | Export/import strategies |

#### 4.1.3 Backtesting Engine (F-BT)

| ID | Requirement | Priority | Description |
|----|-------------|----------|-------------|
| F-BT-001 | Historical simulation | Must | Run strategies against historical data |
| F-BT-002 | Date range selection | Must | Choose custom backtest periods |
| F-BT-003 | Performance metrics | Must | Calculate Sharpe ratio, max drawdown, win rate |
| F-BT-004 | Trade log | Must | Detailed log of all simulated trades |
| F-BT-005 | Commission modeling | Should | Account for trading fees |
| F-BT-006 | Slippage simulation | Should | Model realistic execution prices |
| F-BT-007 | Walk-forward analysis | Could | Rolling window backtests |
| F-BT-008 | Monte Carlo simulation | Could | Randomized trade order analysis |

#### 4.1.4 Paper Trading (F-PT)

| ID | Requirement | Priority | Description |
|----|-------------|----------|-------------|
| F-PT-001 | Simulated execution | Must | Execute trades with fake money |
| F-PT-002 | Real-time data | Must | Use live market prices |
| F-PT-003 | Virtual portfolio | Must | Track simulated positions and P&L |
| F-PT-004 | Switch to live | Should | Easy transition to real trading |

#### 4.1.5 Live Trading (F-LT)

| ID | Requirement | Priority | Description |
|----|-------------|----------|-------------|
| F-LT-001 | Broker connection | Must | Connect to supported brokers |
| F-LT-002 | Order execution | Must | Place market/limit orders |
| F-LT-003 | Position management | Must | View and close positions |
| F-LT-004 | Stop-loss | Must | Automatic stop-loss orders |
| F-LT-005 | Take-profit | Must | Automatic take-profit orders |
| F-LT-006 | Order confirmation | Should | Require confirmation for large trades |
| F-LT-007 | Kill switch | Must | Emergency stop all trading |

#### 4.1.6 Portfolio Dashboard (F-PD)

| ID | Requirement | Priority | Description |
|----|-------------|----------|-------------|
| F-PD-001 | Portfolio overview | Must | Total value, daily P&L, allocation |
| F-PD-002 | Position list | Must | All open positions with performance |
| F-PD-003 | Historical performance | Must | Equity curve over time |
| F-PD-004 | Asset allocation | Should | Pie chart of holdings |
| F-PD-005 | Risk metrics | Should | Portfolio beta, VaR |

#### 4.1.7 Performance Analytics (F-PA)

| ID | Requirement | Priority | Description |
|----|-------------|----------|-------------|
| F-PA-001 | Strategy comparison | Must | Compare multiple strategies side-by-side |
| F-PA-002 | Trade analysis | Must | Win/loss ratio, average trade duration |
| F-PA-003 | Drawdown analysis | Must | Maximum and current drawdown |
| F-PA-004 | Calendar heatmap | Should | Daily P&L visualization |
| F-PA-005 | Export reports | Should | PDF/CSV export of analytics |

#### 4.1.8 Market Data (F-MD)

| ID | Requirement | Priority | Description |
|----|-------------|----------|-------------|
| F-MD-001 | Real-time quotes | Must | Live bid/ask prices |
| F-MD-002 | Historical OHLCV | Must | Candlestick data for backtesting |
| F-MD-003 | Multiple timeframes | Must | 1m, 5m, 15m, 1h, 4h, 1d candles |
| F-MD-004 | Watchlists | Should | Custom asset watchlists |
| F-MD-005 | Price alerts | Could | Notifications on price levels |

### 4.2 Supported Asset Classes

| Asset Class | Data Source | Paper Trading | Live Trading |
|-------------|-------------|---------------|--------------|
| **Crypto** | CCXT (Binance, Kraken) | Binance Testnet | Binance, Kraken |
| **US Stocks** | yfinance, Alpaca | Alpaca Paper | Alpaca (non-EU) |
| **EU Stocks** | yfinance | Internal simulation | DEGIRO (unofficial) |
| **Forex** | Alpha Vantage | Internal simulation | TBD |

### 4.3 Broker Integrations (France-Compatible)

| Broker | Status | API Type | Assets | Notes |
|--------|--------|----------|--------|-------|
| **Alpaca** | MVP | Official REST | US Stocks | Paper trading only (US residents for live) |
| **Binance** | MVP | Official REST/WS | Crypto | Testnet for paper, live available |
| **Kraken** | Phase 2 | Official REST | Crypto | Sandbox available |
| **DEGIRO** | Phase 2 | Unofficial | EU Stocks | Requires reverse engineering |
| **Interactive Brokers** | Phase 3 | Official TWS | Multi-asset | Requires account |

---

## 5. Non-Functional Requirements

### 5.1 Performance (NFR-P)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-P-001 | API response time | < 100ms (p95) |
| NFR-P-002 | Strategy execution latency | < 500ms |
| NFR-P-003 | Backtest speed | 10 years data in < 60s |
| NFR-P-004 | Concurrent users | 100 simultaneous |
| NFR-P-005 | Data ingestion rate | 1000 ticks/second |

### 5.2 Reliability (NFR-R)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-R-001 | System uptime | 99.5% |
| NFR-R-002 | Data durability | No data loss |
| NFR-R-003 | Failover time | < 5 minutes |
| NFR-R-004 | Backup frequency | Daily |

### 5.3 Security (NFR-S)

| ID | Requirement | Description |
|----|-------------|-------------|
| NFR-S-001 | Authentication | JWT-based with refresh tokens |
| NFR-S-002 | API keys encryption | AES-256 at rest |
| NFR-S-003 | HTTPS | TLS 1.3 for all connections |
| NFR-S-004 | Rate limiting | 100 requests/minute per user |
| NFR-S-005 | Audit logging | All trading actions logged |

### 5.4 Compliance (NFR-C)

| ID | Requirement | Description |
|----|-------------|-------------|
| NFR-C-001 | GDPR | User data export and deletion |
| NFR-C-002 | Audit trail | MiFID II-ready transaction logs |
| NFR-C-003 | Risk warnings | Display regulatory disclaimers |

### 5.5 Usability (NFR-U)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-U-001 | Onboarding time | < 10 minutes to first backtest |
| NFR-U-002 | Mobile responsive | Works on tablet/mobile |
| NFR-U-003 | Accessibility | WCAG 2.1 AA compliance |
| NFR-U-004 | Language | French and English |

---

## 6. User Stories

### 6.1 Strategy Creation

```
As a trader,
I want to create a trading strategy using visual building blocks,
So that I can automate my trading rules without coding.

Acceptance Criteria:
- [ ] Can select from list of technical indicators
- [ ] Can combine conditions with AND/OR
- [ ] Can set entry and exit rules separately
- [ ] Can preview strategy logic in plain English
```

### 6.2 Backtesting

```
As a trader,
I want to backtest my strategy against historical data,
So that I can evaluate its performance before risking real money.

Acceptance Criteria:
- [ ] Can select date range for backtest
- [ ] Can see equity curve visualization
- [ ] Can view detailed trade log
- [ ] Can see key metrics (Sharpe, drawdown, win rate)
```

### 6.3 Paper Trading

```
As a trader,
I want to run my strategy in paper trading mode,
So that I can validate it with live market conditions.

Acceptance Criteria:
- [ ] Strategy executes on real-time prices
- [ ] Virtual portfolio tracks gains/losses
- [ ] Can run for user-defined duration
- [ ] Matches expected behavior from backtest
```

### 6.4 Live Trading

```
As a trader,
I want to connect my broker and execute trades automatically,
So that my strategy runs without manual intervention.

Acceptance Criteria:
- [ ] Can authenticate with broker API
- [ ] Orders are placed as per strategy signals
- [ ] Stop-loss and take-profit are enforced
- [ ] Can pause/stop trading with one click
```

### 6.5 Portfolio Monitoring

```
As a trader,
I want to see my portfolio performance in a dashboard,
So that I can monitor my investments at a glance.

Acceptance Criteria:
- [ ] Dashboard shows total portfolio value
- [ ] Can see breakdown by asset
- [ ] Historical equity curve displayed
- [ ] Real-time updates without page refresh
```

---

## 7. Success Metrics

### 7.1 Key Performance Indicators (KPIs)

| Metric | Definition | Target (6 months) |
|--------|------------|-------------------|
| **Active Users** | Users with ≥1 login/week | 500 |
| **Strategies Created** | Total strategies across all users | 2,000 |
| **Backtests Run** | Total backtest executions | 10,000 |
| **Paper Trades** | Simulated trades executed | 50,000 |
| **Live Trades** | Real trades executed | 5,000 |
| **User Retention** | 30-day retention rate | 40% |

### 7.2 Quality Metrics

| Metric | Target |
|--------|--------|
| System uptime | > 99.5% |
| API error rate | < 0.1% |
| Average page load time | < 2 seconds |
| User satisfaction (NPS) | > 30 |

### 7.3 Business Metrics (Future)

| Metric | Description |
|--------|-------------|
| Conversion rate | Free → Paid users |
| MRR | Monthly recurring revenue |
| CAC | Customer acquisition cost |
| LTV | Lifetime value per user |

---

## 8. Roadmap

### 8.1 Phase 1: MVP (Q1 2026)

**Goal:** Core backtesting and paper trading functionality

| Feature | Status |
|---------|--------|
| User authentication | 🔲 Planned |
| Rule engine (basic) | 🔲 Planned |
| 5 pre-built strategies | 🔲 Planned |
| Backtest engine | 🔲 Planned |
| Portfolio dashboard | 🔲 Planned |
| Crypto data (Binance) | 🔲 Planned |
| Paper trading (crypto) | 🔲 Planned |
| Basic charts (D3.js) | 🔲 Planned |

### 8.2 Phase 2: Live Trading (Q2 2026)

**Goal:** Enable real trading with broker integrations

| Feature | Status |
|---------|--------|
| Binance live trading | 🔲 Planned |
| Kraken integration | 🔲 Planned |
| Advanced rule engine | 🔲 Planned |
| More technical indicators | 🔲 Planned |
| Alert system | 🔲 Planned |
| Mobile responsive UI | 🔲 Planned |

### 8.3 Phase 3: Advanced Features (Q3-Q4 2026)

**Goal:** Professional-grade analytics and multi-broker support

| Feature | Status |
|---------|--------|
| DEGIRO integration | 🔲 Planned |
| Multi-asset portfolios | 🔲 Planned |
| Advanced analytics | 🔲 Planned |
| Strategy marketplace | 🔲 Planned |
| API for external tools | 🔲 Planned |
| Team/collaboration features | 🔲 Planned |

---

## 9. Constraints & Assumptions

### 9.1 Constraints

| Constraint | Impact |
|------------|--------|
| **Budget:** OSS/free tools only for POC | Limits data provider options |
| **Regulatory:** MiFID II compliance for EU | Requires audit trail, risk warnings |
| **Broker APIs:** Some are unofficial | May break without warning |
| **Data quality:** Free data has delays | Real-time requires paid feeds later |

### 9.2 Assumptions

| Assumption | Risk if False |
|------------|---------------|
| Users have basic trading knowledge | Need more onboarding content |
| Binance Testnet remains available | Alternative needed |
| yfinance continues to work | Switch to paid provider |
| Docker available on user machines | Provide cloud-hosted option |

### 9.3 Dependencies

| Dependency | Owner | Status |
|------------|-------|--------|
| Binance API | Binance | Stable |
| yfinance library | Community | Active |
| CCXT library | Community | Active |
| TimescaleDB | Timescale Inc | OSS |

---

## 10. Glossary

| Term | Definition |
|------|------------|
| **Backtest** | Simulating a strategy on historical data |
| **Paper Trading** | Simulated trading with fake money and live prices |
| **OHLCV** | Open, High, Low, Close, Volume — candlestick data |
| **Drawdown** | Peak-to-trough decline in portfolio value |
| **Sharpe Ratio** | Risk-adjusted return metric |
| **Rule Engine** | System for defining trading conditions |
| **Strategy** | Set of rules that generate buy/sell signals |
| **Stop-Loss** | Order to sell when price drops below threshold |
| **Take-Profit** | Order to sell when price reaches target |
| **Kill Switch** | Emergency mechanism to halt all trading |
| **MiFID II** | EU financial markets regulation |
| **CCXT** | CryptoCurrency eXchange Trading library |

---

## Appendix A: Competitive Analysis

| Competitor | Strengths | Weaknesses | ApexTrade Advantage |
|------------|-----------|------------|---------------------|
| TradingView | Excellent charts, social | No automation | Full automation |
| 3Commas | Easy bots, cloud | Expensive, crypto only | Free, multi-asset |
| Freqtrade | OSS, customizable | CLI only, complex | Visual UI |
| QuantConnect | Powerful, ML support | Steep learning curve | Simpler UX |
| MetaTrader | Industry standard | Outdated UI, MQL4/5 only | Modern stack, Python |

---

## Appendix B: Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Broker API changes | Medium | High | Abstract broker layer, monitor updates |
| Data provider outage | Low | High | Multiple fallback sources |
| User losses money | Medium | Critical | Warnings, paper trading first, kill switch |
| Regulatory issues | Low | Critical | Legal review, compliance features |
| Security breach | Low | Critical | Encryption, audits, penetration testing |

---

*Document End*
