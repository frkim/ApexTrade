# ApexTrade - System Architecture Diagram

**Version:** 1.0  
**Date:** February 1, 2026

---

## High-Level System Architecture

```mermaid
graph TB
    subgraph "External Services"
        BROKER[("🏦 Brokers<br/>Alpaca · Binance<br/>Kraken")]
        MARKET[("📊 Market Data<br/>yfinance · CCXT<br/>Alpha Vantage")]
        MAIL[("📧 Email Service<br/>SMTP")]
    end

    subgraph "Presentation Layer"
        USER((👤 User))
        BROWSER["🌐 Web Browser"]
        
        USER --> BROWSER
        BROWSER --> NGINX
    end

    subgraph "Edge Layer"
        NGINX["Nginx<br/>Reverse Proxy<br/>SSL Termination"]
        NGINX -->|HTTPS| FRONTEND
        NGINX -->|/api/*| API
        NGINX -->|/ws/*| WS
    end

    subgraph "Frontend Container"
        FRONTEND["Next.js 14<br/>React + TypeScript<br/>:3000"]
        SHADCN["shadcn/ui<br/>Components"]
        D3["D3.js<br/>Charts"]
        NEXTAUTH["NextAuth.js<br/>Session"]
        
        FRONTEND --> SHADCN
        FRONTEND --> D3
        FRONTEND --> NEXTAUTH
    end

    subgraph "Backend Containers"
        API["FastAPI<br/>REST API<br/>:8000"]
        WS["WebSocket<br/>Manager"]
        STRATEGY["Strategy<br/>Engine"]
        BACKTEST["Backtest<br/>Engine"]
        EXECUTOR["Trade<br/>Executor"]
        
        API --> STRATEGY
        API --> BACKTEST
        API --> EXECUTOR
        API --> WS
    end

    subgraph "Background Workers"
        CELERY_W["Celery Workers<br/>ㅤx4 concurrency"]
        CELERY_B["Celery Beat<br/>Scheduler"]
        FLOWER["Flower<br/>Monitoring<br/>:5555"]
        
        CELERY_B -->|schedules| CELERY_W
    end

    subgraph "Data Layer"
        POSTGRES[("PostgreSQL 16<br/>Main DB<br/>:5432")]
        TIMESCALE[("TimescaleDB<br/>Time-Series<br/>:5433")]
        REDIS[("Redis 7<br/>Cache + Queue<br/>:6379")]
        MINIO[("MinIO<br/>Object Storage<br/>:9000")]
    end

    subgraph "Monitoring Stack"
        PROMETHEUS["Prometheus<br/>Metrics<br/>:9090"]
        GRAFANA["Grafana<br/>Dashboards<br/>:3001"]
        LOKI["Loki<br/>Log Aggregation<br/>:3100"]
        PROMTAIL["Promtail<br/>Log Collector"]
        
        PROMTAIL --> LOKI
        PROMETHEUS --> GRAFANA
        LOKI --> GRAFANA
    end

    %% API Connections
    API --> POSTGRES
    API --> TIMESCALE
    API --> REDIS
    
    %% Worker Connections
    CELERY_W --> REDIS
    CELERY_W --> POSTGRES
    CELERY_W --> TIMESCALE
    CELERY_W --> MINIO
    
    %% External Connections
    EXECUTOR --> BROKER
    STRATEGY --> MARKET
    BACKTEST --> TIMESCALE
    API --> MAIL

    %% Monitoring
    API -.->|metrics| PROMETHEUS
    CELERY_W -.->|logs| PROMTAIL
    POSTGRES -.->|metrics| PROMETHEUS

    classDef external fill:#e1f5fe,stroke:#01579b
    classDef frontend fill:#f3e5f5,stroke:#4a148c
    classDef backend fill:#e8f5e9,stroke:#1b5e20
    classDef data fill:#fff3e0,stroke:#e65100
    classDef monitoring fill:#fce4ec,stroke:#880e4f

    class BROKER,MARKET,MAIL external
    class FRONTEND,SHADCN,D3,NEXTAUTH frontend
    class API,WS,STRATEGY,BACKTEST,EXECUTOR,CELERY_W,CELERY_B,FLOWER backend
    class POSTGRES,TIMESCALE,REDIS,MINIO data
    class PROMETHEUS,GRAFANA,LOKI,PROMTAIL monitoring
```

---

## Component Interaction Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant API as FastAPI
    participant SE as Strategy Engine
    participant RD as Redis
    participant PG as PostgreSQL
    participant TS as TimescaleDB
    participant CW as Celery Worker
    participant BR as Broker API

    rect rgb(240, 248, 255)
        Note over U,FE: User Interaction
        U->>FE: Access Dashboard
        FE->>API: GET /api/portfolio
        API->>RD: Check Cache
        alt Cache Hit
            RD-->>API: Return cached data
        else Cache Miss
            API->>PG: Query portfolio
            PG-->>API: Portfolio data
            API->>RD: Store in cache
        end
        API-->>FE: Portfolio JSON
        FE-->>U: Render Dashboard
    end

    rect rgb(255, 248, 240)
        Note over U,CW: Strategy Activation
        U->>FE: Activate Strategy
        FE->>API: POST /api/strategies/{id}/activate
        API->>PG: Update status = 'active'
        API->>RD: Publish activation event
        API-->>FE: Strategy activated
        FE-->>U: Show confirmation
    end

    rect rgb(240, 255, 240)
        Note over CW,BR: Trade Execution
        CW->>TS: Fetch OHLCV data
        CW->>SE: Evaluate conditions
        SE-->>CW: Signal: BUY
        CW->>PG: Log signal
        CW->>BR: Place order
        BR-->>CW: Order ID
        CW->>PG: Save trade
        CW->>RD: Publish trade event
    end

    rect rgb(248, 240, 255)
        Note over FE,CW: Real-time Updates
        API->>FE: WebSocket: trade_executed
        FE-->>U: Toast notification
        FE->>API: GET /api/trades/latest
        API-->>FE: Updated trades
        FE-->>U: Update trade list
    end
```

---

## Microservice Boundaries

```mermaid
graph LR
    subgraph "API Gateway"
        NGINX["Nginx"]
    end

    subgraph "User Service"
        AUTH["Authentication"]
        USERS["User Management"]
        KEYS["API Key Vault"]
    end

    subgraph "Trading Service"
        STRAT["Strategy CRUD"]
        EVAL["Signal Evaluation"]
        EXEC["Order Execution"]
    end

    subgraph "Data Service"
        MARKET["Market Data"]
        HIST["Historical Data"]
        AGGR["Aggregations"]
    end

    subgraph "Analytics Service"
        BACK["Backtesting"]
        PERF["Performance"]
        REPORT["Reporting"]
    end

    subgraph "Notification Service"
        ALERT["Alerts"]
        EMAIL["Email"]
        PUSH["Push Notifications"]
    end

    NGINX --> AUTH
    NGINX --> STRAT
    NGINX --> MARKET
    NGINX --> BACK
    NGINX --> ALERT

    AUTH --> USERS
    AUTH --> KEYS
    STRAT --> EVAL
    EVAL --> EXEC
    MARKET --> HIST
    HIST --> AGGR
    BACK --> PERF
    PERF --> REPORT
    ALERT --> EMAIL
    ALERT --> PUSH

    classDef gateway fill:#bbdefb,stroke:#1565c0
    classDef user fill:#c8e6c9,stroke:#2e7d32
    classDef trading fill:#fff9c4,stroke:#f9a825
    classDef data fill:#d1c4e9,stroke:#512da8
    classDef analytics fill:#ffccbc,stroke:#bf360c
    classDef notif fill:#b2ebf2,stroke:#00838f

    class NGINX gateway
    class AUTH,USERS,KEYS user
    class STRAT,EVAL,EXEC trading
    class MARKET,HIST,AGGR data
    class BACK,PERF,REPORT analytics
    class ALERT,EMAIL,PUSH notif
```

---

## Technology Stack Matrix

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           APEXTRADE TECH STACK                                   │
├───────────────┬─────────────────────────────────────────────────────────────────┤
│               │                                                                  │
│  PRESENTATION │  Next.js 14 │ React 18 │ TypeScript │ Tailwind CSS │ D3.js     │
│     LAYER     │  shadcn/ui │ NextAuth.js │ SWR │ Zustand                        │
│               │                                                                  │
├───────────────┼─────────────────────────────────────────────────────────────────┤
│               │                                                                  │
│  APPLICATION  │  FastAPI │ Pydantic │ SQLAlchemy 2.0 │ Celery │ Redis          │
│     LAYER     │  WebSocket │ JWT Auth │ CORS │ Rate Limiting                   │
│               │                                                                  │
├───────────────┼─────────────────────────────────────────────────────────────────┤
│               │                                                                  │
│   BUSINESS    │  Strategy Engine │ Rule Parser │ Signal Generator              │
│    LOGIC      │  Backtest Engine │ Trade Executor │ Portfolio Manager          │
│               │                                                                  │
├───────────────┼─────────────────────────────────────────────────────────────────┤
│               │                                                                  │
│  DATA ACCESS  │  PostgreSQL 16 │ TimescaleDB │ Redis │ MinIO                   │
│     LAYER     │  Alembic Migrations │ Connection Pooling │ Caching             │
│               │                                                                  │
├───────────────┼─────────────────────────────────────────────────────────────────┤
│               │                                                                  │
│ INFRASTRUCTURE│  Docker │ Docker Compose │ Nginx │ Let's Encrypt               │
│     LAYER     │  Prometheus │ Grafana │ Loki │ Promtail                        │
│               │                                                                  │
├───────────────┼─────────────────────────────────────────────────────────────────┤
│               │                                                                  │
│   EXTERNAL    │  Alpaca API │ Binance/CCXT │ yfinance │ Alpha Vantage          │
│ INTEGRATIONS  │  SMTP │ WebSocket Feeds                                         │
│               │                                                                  │
└───────────────┴─────────────────────────────────────────────────────────────────┘
```

---

## Security Architecture

```mermaid
graph TB
    subgraph "Internet"
        USER((User))
        ATTACKER((Attacker))
    end

    subgraph "Edge Security"
        FW["Firewall<br/>UFW/iptables"]
        RATE["Rate Limiting<br/>30 req/s"]
        WAF["Nginx<br/>Security Headers"]
        SSL["TLS 1.3<br/>HTTPS Only"]
    end

    subgraph "Application Security"
        AUTH["JWT Authentication<br/>15min expiry"]
        RBAC["Role-Based Access<br/>User/Admin"]
        VALID["Input Validation<br/>Pydantic"]
        CORS["CORS<br/>Whitelist"]
    end

    subgraph "Data Security"
        ENCRYPT["AES-256-GCM<br/>API Key Encryption"]
        HASH["Argon2id<br/>Password Hashing"]
        SSL_DB["SSL/TLS<br/>DB Connections"]
    end

    subgraph "Audit & Compliance"
        LOGS["Audit Logs<br/>7 years retention"]
        GDPR["GDPR Compliance<br/>Data Export/Delete"]
        MIFID["MiFID II Ready<br/>Trade Records"]
    end

    USER --> FW
    ATTACKER -.->|blocked| FW
    FW --> RATE
    RATE --> WAF
    WAF --> SSL
    SSL --> AUTH
    AUTH --> RBAC
    RBAC --> VALID
    VALID --> CORS
    CORS --> ENCRYPT
    ENCRYPT --> HASH
    HASH --> SSL_DB
    SSL_DB --> LOGS
    LOGS --> GDPR
    GDPR --> MIFID

    classDef blocked fill:#ffcdd2,stroke:#c62828
    classDef security fill:#c8e6c9,stroke:#2e7d32
    classDef data fill:#fff9c4,stroke:#f9a825
    classDef audit fill:#e1f5fe,stroke:#0277bd

    class ATTACKER blocked
    class FW,RATE,WAF,SSL,AUTH,RBAC,VALID,CORS security
    class ENCRYPT,HASH,SSL_DB data
    class LOGS,GDPR,MIFID audit
```

---

## Scalability Patterns

```mermaid
graph TB
    subgraph "Horizontal Scaling"
        LB["Load Balancer"]
        API1["API Instance 1"]
        API2["API Instance 2"]
        API3["API Instance N"]
        
        LB --> API1
        LB --> API2
        LB --> API3
    end

    subgraph "Worker Scaling"
        QUEUE["Redis Queue"]
        W1["Worker 1"]
        W2["Worker 2"]
        W3["Worker N"]
        
        QUEUE --> W1
        QUEUE --> W2
        QUEUE --> W3
    end

    subgraph "Database Scaling"
        PG_PRIMARY["PostgreSQL<br/>Primary"]
        PG_REPLICA["PostgreSQL<br/>Read Replica"]
        TS_HT["TimescaleDB<br/>Hypertables"]
        COMPRESS["Compression<br/>+ Retention"]
        
        PG_PRIMARY --> PG_REPLICA
        TS_HT --> COMPRESS
    end

    subgraph "Caching Layers"
        L1["L1: Application Cache<br/>(in-memory)"]
        L2["L2: Redis Cache<br/>(distributed)"]
        L3["L3: CDN Cache<br/>(static assets)"]
    end

    API1 --> L1
    L1 --> L2
    L2 --> PG_PRIMARY
    L2 --> PG_REPLICA
```

---

*Document End*
