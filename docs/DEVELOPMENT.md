# ApexTrade - Development Guide

**Version:** 1.0  
**Date:** February 1, 2026  
**Author:** ApexTrade Team

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Getting Started](#2-getting-started)
3. [Project Structure](#3-project-structure)
4. [Development Workflow](#4-development-workflow)
5. [Coding Standards](#5-coding-standards)
6. [Testing](#6-testing)
7. [Debugging](#7-debugging)
8. [Common Tasks](#8-common-tasks)
9. [Troubleshooting](#9-troubleshooting)
10. [Contributing](#10-contributing)

---

## 1. Prerequisites

### 1.1 Required Software

| Software | Version | Purpose |
|----------|---------|---------|
| **Docker Desktop** | 24.0+ | Container runtime |
| **Docker Compose** | 2.23+ | Container orchestration |
| **Python** | 3.12+ | Backend development |
| **Node.js** | 20 LTS | Frontend development |
| **pnpm** | 8.0+ | Package manager (faster than npm) |
| **Git** | 2.40+ | Version control |

### 1.2 Recommended Tools

| Tool | Purpose |
|------|---------|
| **VS Code** | IDE with excellent Python/TypeScript support |
| **DBeaver** | Database GUI for PostgreSQL |
| **Postman / Insomnia** | API testing |
| **Docker Desktop Dashboard** | Container monitoring |

### 1.3 VS Code Extensions

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "charliermarsh.ruff",
    "ms-python.black-formatter",
    "bradlc.vscode-tailwindcss",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "ms-azuretools.vscode-docker",
    "prisma.prisma",
    "mtxr.sqltools",
    "mtxr.sqltools-driver-pg"
  ]
}
```

### 1.4 System Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| **CPU** | 4 cores | 8 cores |
| **RAM** | 8 GB | 16 GB |
| **Disk** | 20 GB free | 50 GB SSD |
| **OS** | Windows 10/11, macOS 12+, Ubuntu 22.04+ | - |

---

## 2. Getting Started

### 2.1 Clone Repository

```bash
git clone https://github.com/frkim/ApexTrade.git
cd ApexTrade
```

### 2.2 Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings (API keys, secrets)
# Required for development:
#   - SECRET_KEY (generate: openssl rand -hex 32)
#   - JWT_SECRET_KEY (generate: openssl rand -hex 32)
```

### 2.3 Start Development Environment

```bash
# Start all services
docker-compose up -d

# Or start with build (after code changes)
docker-compose up -d --build

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f api
```

### 2.4 Verify Installation

```bash
# Check all containers are running
docker-compose ps

# Expected output:
# NAME                    STATUS
# apextrade-nginx         running
# apextrade-frontend      running
# apextrade-api           running
# apextrade-worker-...    running
# apextrade-postgres      running
# apextrade-timescaledb   running
# apextrade-redis         running
```

### 2.5 Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend** | http://localhost | - |
| **API Docs** | http://localhost/api/docs | - |
| **Grafana** | http://localhost:3001 | admin / (from .env) |
| **MinIO Console** | http://localhost:9001 | (from .env) |
| **PostgreSQL** | localhost:5432 | (from .env) |
| **TimescaleDB** | localhost:5433 | (from .env) |
| **Redis** | localhost:6379 | - |

### 2.6 Initial Data Setup

```bash
# Run database migrations
docker-compose exec api alembic upgrade head

# Seed development data (optional)
docker-compose exec api python -m scripts.seed_data

# Download initial market data (optional)
docker-compose exec api python -m scripts.fetch_historical_data --symbol BTC/USDT --days 365
```

---

## 3. Project Structure

```
ApexTrade/
├── .github/                    # GitHub Actions CI/CD
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
│
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI application entry
│   │   ├── config.py          # Settings & environment
│   │   │
│   │   ├── api/               # API routes
│   │   │   ├── __init__.py
│   │   │   ├── deps.py        # Dependency injection
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py
│   │   │       ├── strategies.py
│   │   │       ├── backtests.py
│   │   │       ├── portfolios.py
│   │   │       ├── trades.py
│   │   │       ├── market_data.py
│   │   │       └── users.py
│   │   │
│   │   ├── core/              # Core utilities
│   │   │   ├── __init__.py
│   │   │   ├── database.py    # SQLAlchemy setup
│   │   │   ├── redis.py       # Redis client
│   │   │   ├── security.py    # JWT, hashing
│   │   │   └── events.py      # Event bus
│   │   │
│   │   ├── models/            # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── strategy.py
│   │   │   ├── backtest.py
│   │   │   ├── portfolio.py
│   │   │   ├── trade.py
│   │   │   └── market_data.py
│   │   │
│   │   ├── schemas/           # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── strategy.py
│   │   │   ├── backtest.py
│   │   │   ├── portfolio.py
│   │   │   └── trade.py
│   │   │
│   │   ├── services/          # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── rule_engine.py
│   │   │   ├── strategy_service.py
│   │   │   ├── backtest_service.py
│   │   │   ├── execution_service.py
│   │   │   ├── market_data_service.py
│   │   │   └── portfolio_service.py
│   │   │
│   │   ├── tasks/             # Celery tasks
│   │   │   ├── __init__.py
│   │   │   ├── backtest.py
│   │   │   ├── strategy.py
│   │   │   ├── execution.py
│   │   │   └── market_data.py
│   │   │
│   │   ├── integrations/      # External APIs
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── binance.py
│   │   │   ├── kraken.py
│   │   │   ├── alpaca.py
│   │   │   └── yfinance.py
│   │   │
│   │   └── utils/             # Helper functions
│   │       ├── __init__.py
│   │       ├── indicators.py  # Technical analysis
│   │       └── validators.py
│   │
│   ├── alembic/               # Database migrations
│   │   ├── versions/
│   │   └── env.py
│   │
│   ├── tests/                 # Backend tests
│   │   ├── conftest.py
│   │   ├── unit/
│   │   ├── integration/
│   │   └── fixtures/
│   │
│   ├── scripts/               # Utility scripts
│   │   ├── seed_data.py
│   │   └── fetch_historical_data.py
│   │
│   ├── Dockerfile
│   ├── pyproject.toml         # Python dependencies
│   ├── requirements.txt
│   └── alembic.ini
│
├── frontend/                   # Next.js frontend
│   ├── src/
│   │   ├── app/               # Next.js App Router
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── (auth)/
│   │   │   │   ├── login/
│   │   │   │   └── register/
│   │   │   ├── dashboard/
│   │   │   ├── strategies/
│   │   │   ├── backtests/
│   │   │   ├── portfolios/
│   │   │   └── settings/
│   │   │
│   │   ├── components/        # React components
│   │   │   ├── ui/            # shadcn/ui components
│   │   │   ├── charts/        # D3.js chart components
│   │   │   ├── forms/
│   │   │   ├── layout/
│   │   │   └── dashboard/
│   │   │
│   │   ├── lib/               # Utilities
│   │   │   ├── api.ts         # API client
│   │   │   ├── websocket.ts   # WebSocket client
│   │   │   ├── utils.ts
│   │   │   └── constants.ts
│   │   │
│   │   ├── hooks/             # Custom React hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── usePortfolio.ts
│   │   │   └── useWebSocket.ts
│   │   │
│   │   ├── stores/            # Zustand stores
│   │   │   ├── authStore.ts
│   │   │   └── portfolioStore.ts
│   │   │
│   │   └── types/             # TypeScript types
│   │       ├── api.ts
│   │       ├── strategy.ts
│   │       └── portfolio.ts
│   │
│   ├── public/                # Static assets
│   ├── Dockerfile
│   ├── package.json
│   ├── pnpm-lock.yaml
│   ├── next.config.js
│   ├── tailwind.config.js
│   └── tsconfig.json
│
├── docs/                       # Documentation
│   ├── PRD.md
│   ├── TECHNICAL_SPEC.md
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── DEVELOPMENT.md
│   ├── DATABASE_SCHEMA.md
│   ├── DEPLOYMENT.md
│   └── diagrams/
│
├── monitoring/                 # Monitoring configs
│   ├── prometheus.yml
│   ├── grafana/
│   │   └── dashboards/
│   └── loki/
│
├── nginx/                      # Nginx config
│   ├── nginx.conf
│   └── ssl/
│
├── docker-compose.yml          # Development compose
├── docker-compose.prod.yml     # Production compose
├── .env.example                # Environment template
├── .gitignore
├── README.md
└── Makefile                    # Common commands
```

---

## 4. Development Workflow

### 4.1 Backend Development

```bash
# Enter backend container for development
docker-compose exec api bash

# Or run Python directly
docker-compose exec api python -c "print('Hello')"

# Install new package
docker-compose exec api pip install package-name

# Update requirements.txt
docker-compose exec api pip freeze > requirements.txt

# Run migrations
docker-compose exec api alembic upgrade head

# Create new migration
docker-compose exec api alembic revision --autogenerate -m "Add column"

# Run tests
docker-compose exec api pytest

# Format code
docker-compose exec api black app/
docker-compose exec api ruff check app/ --fix
```

### 4.2 Frontend Development

```bash
# Enter frontend container
docker-compose exec frontend sh

# Install dependencies
docker-compose exec frontend pnpm install

# Add new package
docker-compose exec frontend pnpm add package-name

# Run linter
docker-compose exec frontend pnpm lint

# Format code
docker-compose exec frontend pnpm format

# Build for production
docker-compose exec frontend pnpm build
```

### 4.3 Database Operations

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U apextrade -d apextrade

# Connect to TimescaleDB
docker-compose exec timescaledb psql -U apextrade -d apextrade_ts

# Backup database
docker-compose exec postgres pg_dump -U apextrade apextrade > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T postgres psql -U apextrade apextrade
```

### 4.4 Celery Tasks

```bash
# View active tasks
docker-compose exec worker-backtest celery -A app.celery inspect active

# Purge all tasks
docker-compose exec worker-backtest celery -A app.celery purge

# Monitor tasks in real-time
docker-compose exec worker-backtest celery -A app.celery events
```

### 4.5 Git Workflow

```bash
# Create feature branch
git checkout -b feature/add-new-indicator

# Make changes and commit
git add .
git commit -m "feat: add Stochastic RSI indicator"

# Push and create PR
git push origin feature/add-new-indicator

# Rebase with main before merge
git fetch origin
git rebase origin/main
```

---

## 5. Coding Standards

### 5.1 Python (Backend)

**Style Guide:** PEP 8 + Black + Ruff

```python
# File: app/services/strategy_service.py

"""Strategy service for managing trading strategies."""

from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.strategy import Strategy
from app.schemas.strategy import StrategyCreate, StrategyUpdate
from app.core.exceptions import StrategyNotFoundError


class StrategyService:
    """Service for strategy CRUD operations."""

    def __init__(self, db: AsyncSession):
        """Initialize with database session.
        
        Args:
            db: Async SQLAlchemy session
        """
        self.db = db

    async def get_by_id(self, strategy_id: UUID) -> Optional[Strategy]:
        """Fetch strategy by ID.
        
        Args:
            strategy_id: UUID of the strategy
            
        Returns:
            Strategy if found, None otherwise
        """
        result = await self.db.execute(
            select(Strategy).where(Strategy.id == strategy_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: UUID, data: StrategyCreate) -> Strategy:
        """Create a new strategy.
        
        Args:
            user_id: Owner user ID
            data: Strategy creation data
            
        Returns:
            Created strategy
        """
        strategy = Strategy(
            user_id=user_id,
            name=data.name,
            description=data.description,
            asset_symbol=data.asset_symbol,
            timeframe=data.timeframe,
            entry_rules=data.entry_rules.model_dump(),
            exit_rules=data.exit_rules.model_dump(),
        )
        self.db.add(strategy)
        await self.db.commit()
        await self.db.refresh(strategy)
        return strategy
```

**Configuration (pyproject.toml):**
```toml
[tool.black]
line-length = 88
target-version = ['py312']

[tool.ruff]
line-length = 88
select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "SIM"]
ignore = ["E501"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

### 5.2 TypeScript (Frontend)

**Style Guide:** ESLint + Prettier

```typescript
// File: src/components/dashboard/PortfolioCard.tsx

import { type FC } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { formatCurrency, formatPercent } from '@/lib/utils';
import type { Portfolio } from '@/types/portfolio';

interface PortfolioCardProps {
  portfolio: Portfolio;
  onSelect?: (id: string) => void;
}

/**
 * Displays portfolio summary with key metrics.
 */
export const PortfolioCard: FC<PortfolioCardProps> = ({ 
  portfolio, 
  onSelect 
}) => {
  const handleClick = () => {
    onSelect?.(portfolio.id);
  };

  return (
    <Card 
      className="cursor-pointer hover:shadow-lg transition-shadow"
      onClick={handleClick}
    >
      <CardHeader>
        <CardTitle className="text-lg">{portfolio.name}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4">
          <MetricItem 
            label="Value" 
            value={formatCurrency(portfolio.currentValue)} 
          />
          <MetricItem 
            label="Return" 
            value={formatPercent(portfolio.totalReturnPct)}
            className={portfolio.totalReturnPct >= 0 ? 'text-green-600' : 'text-red-600'}
          />
        </div>
      </CardContent>
    </Card>
  );
};

interface MetricItemProps {
  label: string;
  value: string;
  className?: string;
}

const MetricItem: FC<MetricItemProps> = ({ label, value, className }) => (
  <div>
    <p className="text-sm text-muted-foreground">{label}</p>
    <p className={`text-xl font-semibold ${className ?? ''}`}>{value}</p>
  </div>
);
```

**Configuration (.eslintrc.json):**
```json
{
  "extends": [
    "next/core-web-vitals",
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "prettier"
  ],
  "rules": {
    "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
    "@typescript-eslint/explicit-function-return-type": "off",
    "prefer-const": "error"
  }
}
```

### 5.3 Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation |
| `style` | Formatting (no code change) |
| `refactor` | Code restructuring |
| `test` | Adding tests |
| `chore` | Maintenance tasks |

**Examples:**
```bash
feat(strategy): add Bollinger Bands indicator support
fix(backtest): correct Sharpe ratio calculation
docs(api): add WebSocket event documentation
refactor(services): extract rule evaluation logic
test(portfolio): add integration tests for positions
chore(deps): upgrade FastAPI to 0.110.0
```

---

## 6. Testing

### 6.1 Backend Tests

```bash
# Run all tests
docker-compose exec api pytest

# Run with coverage
docker-compose exec api pytest --cov=app --cov-report=html

# Run specific test file
docker-compose exec api pytest tests/unit/test_rule_engine.py

# Run specific test
docker-compose exec api pytest tests/unit/test_rule_engine.py::test_rsi_condition -v

# Run with markers
docker-compose exec api pytest -m "not slow"
```

**Test Structure:**
```python
# tests/unit/test_rule_engine.py

import pytest
from decimal import Decimal

from app.services.rule_engine import RuleEngine, Rule, Condition


class TestRuleEngine:
    """Tests for RuleEngine service."""

    @pytest.fixture
    def rule_engine(self):
        """Create RuleEngine instance."""
        return RuleEngine()

    @pytest.fixture
    def sample_market_data(self):
        """Sample OHLCV data for testing."""
        return {
            "symbol": "BTC/USDT",
            "close": Decimal("43500.00"),
            "rsi_14": Decimal("28.5"),
            "sma_20": Decimal("43000.00"),
        }

    def test_rsi_less_than_condition(self, rule_engine, sample_market_data):
        """RSI below threshold should trigger."""
        condition = Condition(
            indicator="RSI",
            params={"period": 14},
            operator="less_than",
            value=30,
        )
        
        result = rule_engine.evaluate_condition(condition, sample_market_data)
        
        assert result is True

    def test_rsi_greater_than_condition(self, rule_engine, sample_market_data):
        """RSI above threshold should not trigger."""
        condition = Condition(
            indicator="RSI",
            params={"period": 14},
            operator="greater_than",
            value=70,
        )
        
        result = rule_engine.evaluate_condition(condition, sample_market_data)
        
        assert result is False

    @pytest.mark.parametrize("rsi_value,expected", [
        (25, True),
        (30, False),  # Equal to threshold, not less than
        (35, False),
    ])
    def test_rsi_threshold_boundary(self, rule_engine, rsi_value, expected):
        """Test RSI threshold boundary conditions."""
        market_data = {"rsi_14": Decimal(str(rsi_value))}
        condition = Condition(
            indicator="RSI",
            params={"period": 14},
            operator="less_than",
            value=30,
        )
        
        result = rule_engine.evaluate_condition(condition, market_data)
        
        assert result is expected
```

### 6.2 Frontend Tests

```bash
# Run tests
docker-compose exec frontend pnpm test

# Run with watch
docker-compose exec frontend pnpm test:watch

# Run with coverage
docker-compose exec frontend pnpm test:coverage
```

**Test Structure:**
```typescript
// src/components/dashboard/__tests__/PortfolioCard.test.tsx

import { render, screen, fireEvent } from '@testing-library/react';
import { PortfolioCard } from '../PortfolioCard';
import type { Portfolio } from '@/types/portfolio';

describe('PortfolioCard', () => {
  const mockPortfolio: Portfolio = {
    id: 'pf_123',
    name: 'Test Portfolio',
    currentValue: 10500,
    totalReturnPct: 5.0,
  };

  it('renders portfolio name', () => {
    render(<PortfolioCard portfolio={mockPortfolio} />);
    
    expect(screen.getByText('Test Portfolio')).toBeInTheDocument();
  });

  it('displays formatted currency value', () => {
    render(<PortfolioCard portfolio={mockPortfolio} />);
    
    expect(screen.getByText('€10,500.00')).toBeInTheDocument();
  });

  it('shows positive return in green', () => {
    render(<PortfolioCard portfolio={mockPortfolio} />);
    
    const returnElement = screen.getByText('+5.00%');
    expect(returnElement).toHaveClass('text-green-600');
  });

  it('calls onSelect when clicked', () => {
    const handleSelect = jest.fn();
    render(<PortfolioCard portfolio={mockPortfolio} onSelect={handleSelect} />);
    
    fireEvent.click(screen.getByRole('article'));
    
    expect(handleSelect).toHaveBeenCalledWith('pf_123');
  });
});
```

### 6.3 Integration Tests

```python
# tests/integration/test_strategies_api.py

import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.integration
class TestStrategiesAPI:
    """Integration tests for Strategies API."""

    @pytest.fixture
    async def authenticated_client(self, test_user):
        """Client with valid authentication."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/v1/auth/login", json={
                "email": test_user.email,
                "password": "testpassword123"
            })
            token = response.json()["data"]["access_token"]
            client.headers["Authorization"] = f"Bearer {token}"
            yield client

    async def test_create_strategy(self, authenticated_client):
        """Create a new strategy via API."""
        response = await authenticated_client.post("/api/v1/strategies", json={
            "name": "Test RSI Strategy",
            "asset_symbol": "BTC/USDT",
            "timeframe": "1h",
            "entry_rules": {
                "logic": "AND",
                "conditions": [
                    {"indicator": "RSI", "params": {"period": 14}, "operator": "less_than", "value": 30}
                ]
            },
            "exit_rules": {
                "logic": "OR",
                "conditions": [
                    {"indicator": "RSI", "params": {"period": 14}, "operator": "greater_than", "value": 70}
                ]
            }
        })
        
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["name"] == "Test RSI Strategy"
        assert data["status"] == "draft"

    async def test_list_strategies(self, authenticated_client, test_strategy):
        """List user strategies."""
        response = await authenticated_client.get("/api/v1/strategies")
        
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) >= 1
        assert any(s["id"] == str(test_strategy.id) for s in data)
```

### 6.4 Test Coverage Requirements

| Component | Minimum Coverage |
|-----------|------------------|
| Services | 80% |
| API Routes | 90% |
| Models | 70% |
| UI Components | 60% |
| Integration | Critical paths |

---

## 7. Debugging

### 7.1 Backend Debugging

**VS Code launch.json:**
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI Debug",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
      "jinja": true,
      "env": {
        "PYTHONPATH": "${workspaceFolder}/backend"
      }
    }
  ]
}
```

**Using debugpy in container:**
```python
# Add to app/main.py for debugging
import debugpy
debugpy.listen(("0.0.0.0", 5678))
print("Waiting for debugger...")
debugpy.wait_for_client()
```

### 7.2 Logging

```python
# app/core/logging.py
import logging
import sys

from app.config import settings


def setup_logging():
    """Configure application logging."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    
    # Reduce noise from libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


# Usage in services
logger = logging.getLogger(__name__)

class StrategyService:
    async def activate(self, strategy_id: UUID):
        logger.info(f"Activating strategy {strategy_id}")
        try:
            # ... activation logic
            logger.debug(f"Strategy {strategy_id} activated successfully")
        except Exception as e:
            logger.error(f"Failed to activate strategy {strategy_id}: {e}")
            raise
```

### 7.3 Database Debugging

```bash
# Enable SQL query logging
docker-compose exec api python -c "
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)
"

# Query TimescaleDB directly
docker-compose exec timescaledb psql -U apextrade -d apextrade_ts -c "
SELECT time, symbol, close 
FROM ohlcv 
WHERE symbol = 'BTC/USDT' 
ORDER BY time DESC 
LIMIT 10;
"
```

### 7.4 Celery Task Debugging

```bash
# Check task status
docker-compose exec api python -c "
from app.celery import celery_app
i = celery_app.control.inspect()
print('Active:', i.active())
print('Reserved:', i.reserved())
print('Scheduled:', i.scheduled())
"

# Enable task tracing
docker-compose exec worker-backtest celery -A app.celery worker --loglevel=DEBUG
```

---

## 8. Common Tasks

### 8.1 Add New API Endpoint

```bash
# 1. Create schema (backend/app/schemas/new_feature.py)
# 2. Create model if needed (backend/app/models/new_feature.py)
# 3. Create service (backend/app/services/new_feature_service.py)
# 4. Create route (backend/app/api/v1/new_feature.py)
# 5. Register in router (backend/app/api/v1/__init__.py)
# 6. Write tests (backend/tests/unit/test_new_feature.py)
# 7. Update API docs (docs/API.md)
```

### 8.2 Add New Technical Indicator

```python
# backend/app/utils/indicators.py

def calculate_stoch_rsi(
    close_prices: pd.Series,
    rsi_period: int = 14,
    stoch_period: int = 14,
    k_period: int = 3,
    d_period: int = 3,
) -> tuple[pd.Series, pd.Series]:
    """Calculate Stochastic RSI.
    
    Args:
        close_prices: Series of closing prices
        rsi_period: RSI lookback period
        stoch_period: Stochastic lookback period
        k_period: %K smoothing period
        d_period: %D smoothing period
        
    Returns:
        Tuple of (%K, %D) Series
    """
    rsi = calculate_rsi(close_prices, rsi_period)
    
    stoch_rsi = (rsi - rsi.rolling(stoch_period).min()) / \
                (rsi.rolling(stoch_period).max() - rsi.rolling(stoch_period).min())
    
    k = stoch_rsi.rolling(k_period).mean() * 100
    d = k.rolling(d_period).mean()
    
    return k, d
```

### 8.3 Add Database Migration

```bash
# Create migration
docker-compose exec api alembic revision --autogenerate -m "add_new_column"

# Review generated migration
cat backend/alembic/versions/xxxx_add_new_column.py

# Apply migration
docker-compose exec api alembic upgrade head

# Rollback if needed
docker-compose exec api alembic downgrade -1
```

### 8.4 Add New UI Component

```bash
# 1. Add shadcn component
docker-compose exec frontend pnpm dlx shadcn-ui@latest add dialog

# 2. Create custom component
# frontend/src/components/my-component.tsx

# 3. Add to page
# frontend/src/app/page.tsx
```

---

## 9. Troubleshooting

### 9.1 Common Issues

**Docker containers won't start:**
```bash
# Check for port conflicts
netstat -an | grep -E ":(80|443|5432|6379|3000)"

# Remove all containers and volumes
docker-compose down -v

# Rebuild from scratch
docker-compose up -d --build
```

**Database connection refused:**
```bash
# Check if postgres is ready
docker-compose exec postgres pg_isready

# Check logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

**Celery tasks not executing:**
```bash
# Check Redis connectivity
docker-compose exec redis redis-cli ping

# Check worker status
docker-compose exec worker-backtest celery -A app.celery status

# Restart workers
docker-compose restart worker-backtest worker-strategy
```

**Frontend not updating:**
```bash
# Clear Next.js cache
docker-compose exec frontend rm -rf .next

# Rebuild
docker-compose up -d --build frontend
```

### 9.2 Performance Issues

**Slow API responses:**
```bash
# Check database query performance
docker-compose exec api python -c "
from app.core.database import engine
with engine.connect() as conn:
    result = conn.exec_driver_sql('EXPLAIN ANALYZE SELECT * FROM strategies LIMIT 100')
    print(result.fetchall())
"
```

**High memory usage:**
```bash
# Check container stats
docker stats

# Reduce worker concurrency
# Edit docker-compose.yml: -c 4 → -c 2
```

---

## 10. Contributing

### 10.1 Code Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No security vulnerabilities
- [ ] Performance considered
- [ ] Error handling complete
- [ ] Logging appropriate
- [ ] Backwards compatible

### 10.2 Pull Request Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guide
- [ ] Self-reviewed
- [ ] Documentation updated
- [ ] No new warnings
```

### 10.3 Release Process

```bash
# 1. Update version
# backend/app/__init__.py: __version__ = "1.1.0"
# frontend/package.json: "version": "1.1.0"

# 2. Update changelog
# CHANGELOG.md

# 3. Create tag
git tag -a v1.1.0 -m "Release 1.1.0"
git push origin v1.1.0

# 4. CI/CD will build and deploy
```

---

*Document End*
