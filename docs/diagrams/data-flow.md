# ApexTrade - Data Flow Diagrams

**Version:** 1.0  
**Date:** February 1, 2026

---

## 1. Overall Data Flow

```mermaid
flowchart TB
    subgraph "External Data Sources"
        MKT["📊 Market Data APIs<br/>yfinance · CCXT · Alpha Vantage"]
        BRK["🏦 Brokers<br/>Alpaca · Binance · Kraken"]
    end

    subgraph "Data Ingestion Layer"
        FETCH["Data Fetcher<br/>Celery Task"]
        NORM["Normalizer<br/>OHLCV Format"]
        VALID["Validator<br/>Data Quality"]
    end

    subgraph "Storage Layer"
        TS[("TimescaleDB<br/>OHLCV Hypertables")]
        PG[("PostgreSQL<br/>Trades · Strategies")]
        RD[("Redis<br/>Cache · Pubsub")]
        S3[("MinIO<br/>Backtest Reports")]
    end

    subgraph "Processing Layer"
        STRAT["Strategy Engine"]
        BACK["Backtest Engine"]
        EXEC["Trade Executor"]
    end

    subgraph "Presentation Layer"
        API["FastAPI"]
        WS["WebSocket"]
        FE["Next.js Frontend"]
    end

    subgraph "User"
        USER((👤 User))
    end

    %% Ingestion Flow
    MKT -->|HTTP/WS| FETCH
    FETCH --> NORM
    NORM --> VALID
    VALID -->|time-series| TS
    VALID -->|cache| RD

    %% Processing Flow
    TS --> STRAT
    TS --> BACK
    STRAT -->|signals| EXEC
    EXEC -->|orders| BRK
    BRK -->|fills| EXEC
    EXEC -->|trades| PG
    BACK -->|results| PG
    BACK -->|reports| S3

    %% Presentation Flow
    PG --> API
    TS --> API
    RD --> API
    API --> WS
    API --> FE
    WS --> FE
    FE --> USER

    %% Real-time Updates
    EXEC -.->|events| RD
    RD -.->|pubsub| WS

    classDef external fill:#e3f2fd,stroke:#1565c0
    classDef ingest fill:#fff3e0,stroke:#ef6c00
    classDef storage fill:#e8f5e9,stroke:#2e7d32
    classDef process fill:#fce4ec,stroke:#c2185b
    classDef present fill:#f3e5f5,stroke:#7b1fa2

    class MKT,BRK external
    class FETCH,NORM,VALID ingest
    class TS,PG,RD,S3 storage
    class STRAT,BACK,EXEC process
    class API,WS,FE present
```

---

## 2. Market Data Ingestion Flow

```mermaid
sequenceDiagram
    participant SCHED as Celery Beat
    participant WORKER as Celery Worker
    participant CCXT as CCXT/yfinance
    participant NORM as Normalizer
    participant VALID as Validator
    participant TS as TimescaleDB
    participant RD as Redis
    participant WS as WebSocket

    Note over SCHED,WS: Scheduled Data Fetch (Every 1 minute)
    
    SCHED->>WORKER: trigger fetch_ohlcv_task
    WORKER->>CCXT: fetch_ohlcv("BTC/EUR", "1m")
    CCXT-->>WORKER: Raw OHLCV array
    
    WORKER->>NORM: normalize(data, "binance")
    Note over NORM: Convert to standard format<br/>Timezone: UTC<br/>Volume: Base currency
    NORM-->>WORKER: Normalized OHLCV
    
    WORKER->>VALID: validate(data)
    Note over VALID: Check:<br/>• No future timestamps<br/>• High >= Low<br/>• Volume >= 0
    
    alt Validation Passed
        VALID-->>WORKER: Valid data
        WORKER->>TS: INSERT INTO ohlcv
        TS-->>WORKER: Inserted
        WORKER->>RD: SET cache:ticker:BTC/EUR
        WORKER->>RD: PUBLISH price:BTC/EUR
        RD->>WS: Notify subscribers
    else Validation Failed
        VALID-->>WORKER: Validation errors
        WORKER->>RD: Log error
        Note over WORKER: Skip invalid candle
    end
```

---

## 3. Strategy Execution Flow

```mermaid
flowchart TB
    subgraph "Trigger"
        CRON["⏰ Cron Schedule<br/>Every 1 min"]
        PRICE["📈 Price Event<br/>New candle"]
    end

    subgraph "Strategy Evaluation"
        LOAD["Load Active<br/>Strategies"]
        FETCH["Fetch OHLCV<br/>Data"]
        CALC["Calculate<br/>Indicators"]
        EVAL["Evaluate<br/>Conditions"]
    end

    subgraph "Signal Decision"
        CHECK{{"Check<br/>All Rules"}}
        ENTRY["Entry<br/>Signal"]
        EXIT["Exit<br/>Signal"]
        HOLD["Hold<br/>No Action"]
    end

    subgraph "Trade Execution"
        SIZE["Position<br/>Sizing"]
        RISK["Risk<br/>Check"]
        ORDER["Create<br/>Order"]
        SUBMIT["Submit to<br/>Broker"]
    end

    subgraph "Post-Trade"
        FILL["Process<br/>Fill"]
        POS["Update<br/>Position"]
        LOG["Log<br/>Trade"]
        NOTIFY["Send<br/>Notification"]
    end

    CRON --> LOAD
    PRICE --> LOAD
    LOAD --> FETCH
    FETCH --> CALC
    CALC --> EVAL
    EVAL --> CHECK

    CHECK -->|Entry conditions met| ENTRY
    CHECK -->|Exit conditions met| EXIT
    CHECK -->|No conditions met| HOLD

    ENTRY --> SIZE
    EXIT --> SIZE
    SIZE --> RISK
    RISK -->|Approved| ORDER
    RISK -->|Rejected| HOLD
    ORDER --> SUBMIT
    SUBMIT --> FILL
    FILL --> POS
    POS --> LOG
    LOG --> NOTIFY

    HOLD --> END((End))
    NOTIFY --> END

    classDef trigger fill:#e1f5fe,stroke:#0277bd
    classDef eval fill:#fff8e1,stroke:#ff8f00
    classDef decision fill:#f3e5f5,stroke:#8e24aa
    classDef exec fill:#e8f5e9,stroke:#388e3c
    classDef post fill:#fce4ec,stroke:#d81b60

    class CRON,PRICE trigger
    class LOAD,FETCH,CALC,EVAL eval
    class CHECK,ENTRY,EXIT,HOLD decision
    class SIZE,RISK,ORDER,SUBMIT exec
    class FILL,POS,LOG,NOTIFY post
```

---

## 4. Backtest Data Flow

```mermaid
flowchart LR
    subgraph "Input"
        USER((User))
        STRAT["Strategy<br/>Definition"]
        PARAMS["Parameters<br/>Dates · Capital"]
    end

    subgraph "Data Preparation"
        LOAD["Load Historical<br/>OHLCV"]
        SLICE["Slice Date<br/>Range"]
        PREP["Prepare<br/>DataFrames"]
    end

    subgraph "Simulation Engine"
        ITER["Iterate<br/>Candles"]
        IND["Calculate<br/>Indicators"]
        SIG["Generate<br/>Signals"]
        TRADE["Simulate<br/>Trades"]
        PORT["Update<br/>Portfolio"]
    end

    subgraph "Metrics Calculation"
        RET["Returns"]
        DD["Drawdown"]
        SHARPE["Sharpe Ratio"]
        WIN["Win Rate"]
    end

    subgraph "Output"
        RESULTS["Results<br/>JSON"]
        EQUITY["Equity<br/>Curve"]
        TRADES["Trade<br/>List"]
        REPORT["PDF<br/>Report"]
    end

    USER -->|Configure| STRAT
    USER -->|Configure| PARAMS
    STRAT --> LOAD
    PARAMS --> LOAD
    LOAD --> SLICE
    SLICE --> PREP
    PREP --> ITER

    ITER --> IND
    IND --> SIG
    SIG --> TRADE
    TRADE --> PORT
    PORT -->|Next candle| ITER

    PORT --> RET
    PORT --> DD
    RET --> SHARPE
    PORT --> WIN

    RET --> RESULTS
    DD --> RESULTS
    SHARPE --> RESULTS
    WIN --> RESULTS

    RESULTS --> EQUITY
    RESULTS --> TRADES
    RESULTS --> REPORT

    classDef input fill:#e3f2fd,stroke:#1565c0
    classDef prep fill:#fff3e0,stroke:#ef6c00
    classDef sim fill:#e8f5e9,stroke:#2e7d32
    classDef calc fill:#f3e5f5,stroke:#7b1fa2
    classDef output fill:#fce4ec,stroke:#c2185b

    class USER,STRAT,PARAMS input
    class LOAD,SLICE,PREP prep
    class ITER,IND,SIG,TRADE,PORT sim
    class RET,DD,SHARPE,WIN calc
    class RESULTS,EQUITY,TRADES,REPORT output
```

---

## 5. Authentication Flow

```mermaid
sequenceDiagram
    participant USER as User
    participant FE as Frontend
    participant API as FastAPI
    participant DB as PostgreSQL
    participant RD as Redis

    Note over USER,RD: Login Flow
    
    USER->>FE: Enter email/password
    FE->>API: POST /api/auth/login
    API->>DB: SELECT user WHERE email = ?
    DB-->>API: User record
    
    API->>API: Verify password (Argon2id)
    
    alt Password Valid
        API->>API: Generate JWT tokens
        API->>RD: Store refresh token
        API-->>FE: { access_token, refresh_token }
        FE->>FE: Store in secure cookie
        FE-->>USER: Redirect to dashboard
    else Password Invalid
        API-->>FE: 401 Unauthorized
        FE-->>USER: Show error
    end

    Note over USER,RD: Authenticated Request
    
    USER->>FE: Navigate to /strategies
    FE->>API: GET /api/strategies<br/>Header: Authorization: Bearer {token}
    API->>API: Validate JWT
    
    alt Token Valid
        API->>DB: SELECT strategies WHERE user_id = ?
        DB-->>API: Strategies list
        API-->>FE: Strategies JSON
        FE-->>USER: Render strategies
    else Token Expired
        API-->>FE: 401 Token Expired
        FE->>API: POST /api/auth/refresh<br/>{ refresh_token }
        API->>RD: Verify refresh token
        RD-->>API: Token valid
        API->>API: Generate new access token
        API-->>FE: { access_token }
        FE->>API: Retry original request
    end
```

---

## 6. Real-Time Data Flow (WebSocket)

```mermaid
flowchart TB
    subgraph "Data Sources"
        CCXT["CCXT<br/>Price Feed"]
        TRADE["Trade<br/>Executor"]
        ALERT["Alert<br/>System"]
    end

    subgraph "Event Bus"
        RD["Redis Pub/Sub"]
        
        CH1["channel: prices"]
        CH2["channel: trades"]
        CH3["channel: alerts"]
        
        RD --> CH1
        RD --> CH2
        RD --> CH3
    end

    subgraph "WebSocket Manager"
        MANAGER["Connection<br/>Manager"]
        ROOMS["Room<br/>Subscriptions"]
        FILTER["Message<br/>Filter"]
        
        MANAGER --> ROOMS
        ROOMS --> FILTER
    end

    subgraph "Clients"
        C1["Client 1<br/>Dashboard"]
        C2["Client 2<br/>Trading View"]
        C3["Client 3<br/>Mobile"]
    end

    CCXT -->|publish| CH1
    TRADE -->|publish| CH2
    ALERT -->|publish| CH3

    CH1 --> MANAGER
    CH2 --> MANAGER
    CH3 --> MANAGER

    FILTER -->|prices| C1
    FILTER -->|prices| C2
    FILTER -->|trades| C1
    FILTER -->|trades| C2
    FILTER -->|alerts| C1
    FILTER -->|alerts| C3

    classDef source fill:#e3f2fd,stroke:#1565c0
    classDef bus fill:#fff3e0,stroke:#ef6c00
    classDef ws fill:#e8f5e9,stroke:#2e7d32
    classDef client fill:#f3e5f5,stroke:#7b1fa2

    class CCXT,TRADE,ALERT source
    class RD,CH1,CH2,CH3 bus
    class MANAGER,ROOMS,FILTER ws
    class C1,C2,C3 client
```

---

## 7. Error Handling & Recovery Flow

```mermaid
flowchart TB
    subgraph "Error Detection"
        API_ERR["API Error"]
        WORKER_ERR["Worker Error"]
        BROKER_ERR["Broker Error"]
        DB_ERR["Database Error"]
    end

    subgraph "Error Classification"
        CLASS{{"Error<br/>Type?"}}
        RETRY["Retryable"]
        FATAL["Fatal"]
        WARN["Warning"]
    end

    subgraph "Retry Logic"
        BACKOFF["Exponential<br/>Backoff"]
        MAX_RETRY{{"Max<br/>Retries?"}}
        EXEC["Re-execute"]
    end

    subgraph "Recovery Actions"
        LOG["Log to<br/>Loki"]
        ALERT_ADMIN["Alert<br/>Admin"]
        CIRCUIT["Circuit<br/>Breaker"]
        FALLBACK["Use<br/>Fallback"]
    end

    subgraph "User Notification"
        TOAST["Toast<br/>Message"]
        EMAIL["Email<br/>Alert"]
        DASH["Dashboard<br/>Status"]
    end

    API_ERR --> CLASS
    WORKER_ERR --> CLASS
    BROKER_ERR --> CLASS
    DB_ERR --> CLASS

    CLASS -->|Network · Timeout| RETRY
    CLASS -->|Validation · Auth| FATAL
    CLASS -->|Rate Limit| WARN

    RETRY --> BACKOFF
    BACKOFF --> MAX_RETRY
    MAX_RETRY -->|No| EXEC
    EXEC -->|Success| END((End))
    EXEC -->|Fail| MAX_RETRY
    MAX_RETRY -->|Yes| FATAL

    FATAL --> LOG
    LOG --> ALERT_ADMIN
    ALERT_ADMIN --> CIRCUIT
    CIRCUIT --> FALLBACK

    WARN --> LOG
    WARN --> TOAST

    FALLBACK --> DASH
    ALERT_ADMIN --> EMAIL

    classDef error fill:#ffcdd2,stroke:#c62828
    classDef classify fill:#fff9c4,stroke:#f9a825
    classDef retry fill:#c8e6c9,stroke:#388e3c
    classDef recover fill:#e1f5fe,stroke:#0277bd
    classDef notify fill:#f3e5f5,stroke:#7b1fa2

    class API_ERR,WORKER_ERR,BROKER_ERR,DB_ERR error
    class CLASS,RETRY,FATAL,WARN classify
    class BACKOFF,MAX_RETRY,EXEC retry
    class LOG,ALERT_ADMIN,CIRCUIT,FALLBACK recover
    class TOAST,EMAIL,DASH notify
```

---

## 8. Data Lifecycle

```mermaid
gantt
    title Data Retention Timeline
    dateFormat  YYYY-MM-DD
    section Tick Data
    Active Storage (7 days)          :active, tick1, 2026-02-01, 7d
    Deleted                          :done, tick2, after tick1, 1d
    
    section OHLCV
    Active (compressed after 7 days) :active, ohlcv1, 2026-02-01, 365d
    Compressed Archive               :crit, ohlcv2, 2026-02-01, 1825d
    
    section Trades
    Active Storage                   :active, trade1, 2026-02-01, 3650d
    MiFID II Compliance              :trade2, 2026-02-01, 3650d
    
    section Backtests
    Active Results                   :active, bt1, 2026-02-01, 365d
    Archived to MinIO                :bt2, after bt1, 1825d
    
    section Audit Logs
    Active                           :active, audit1, 2026-02-01, 2555d
    Compliance Retention             :audit2, 2026-02-01, 2555d
```

---

## 9. Cache Invalidation Strategy

```mermaid
flowchart TB
    subgraph "Cache Layers"
        L1["L1: In-Memory<br/>(Python dict)<br/>TTL: 60s"]
        L2["L2: Redis<br/>TTL: 5-15min"]
        L3["L3: PostgreSQL<br/>Source of Truth"]
    end

    subgraph "Write Operations"
        WRITE["Write Request"]
        UPD_DB["Update Database"]
        INV_L2["Invalidate L2"]
        INV_L1["Broadcast L1<br/>Invalidation"]
    end

    subgraph "Read Operations"
        READ["Read Request"]
        CHK_L1{{"L1<br/>Hit?"}}
        CHK_L2{{"L2<br/>Hit?"}}
        FETCH["Fetch from DB"]
        POP_L2["Populate L2"]
        POP_L1["Populate L1"]
        RETURN["Return Data"]
    end

    WRITE --> UPD_DB
    UPD_DB --> INV_L2
    INV_L2 --> INV_L1

    READ --> CHK_L1
    CHK_L1 -->|Yes| RETURN
    CHK_L1 -->|No| CHK_L2
    CHK_L2 -->|Yes| POP_L1
    POP_L1 --> RETURN
    CHK_L2 -->|No| FETCH
    FETCH --> POP_L2
    POP_L2 --> POP_L1

    L1 -.->|Miss| L2
    L2 -.->|Miss| L3

    classDef cache fill:#e8f5e9,stroke:#2e7d32
    classDef write fill:#ffcdd2,stroke:#c62828
    classDef read fill:#e3f2fd,stroke:#1565c0

    class L1,L2,L3 cache
    class WRITE,UPD_DB,INV_L2,INV_L1 write
    class READ,CHK_L1,CHK_L2,FETCH,POP_L2,POP_L1,RETURN read
```

---

*Document End*
