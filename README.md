# ApexTrade

A comprehensive algorithmic trading platform designed for retail and semi-professional traders. The platform enables users to create, test, and execute automated trading strategies across multiple asset classes including stocks, cryptocurrencies, and forex.

## Features

- **Visual Rule Engine**: Create trading strategies using a visual builder without coding
- **Backtesting Engine**: Test strategies against historical data with detailed performance metrics
- **Paper Trading**: Simulate trading with real-time market data before risking real money
- **Live Trading**: Execute trades automatically via broker integrations (Binance, Alpaca)
- **Portfolio Dashboard**: Monitor your investments with professional-grade analytics
- **Technical Indicators**: Built-in RSI, MACD, SMA, EMA, Bollinger Bands, and more

## Tech Stack

### Backend
- **Python 3.12+** with **FastAPI** for REST API
- **SQLAlchemy 2.0** with async support
- **PostgreSQL** for relational data
- **TimescaleDB** for time-series data (OHLCV)
- **Redis** for caching and message broker
- **Celery** for background task processing
- **CCXT** for exchange integrations

### Frontend
- **Next.js 16** with React and TypeScript
- **Tailwind CSS** for styling
- **Zustand** for state management
- **TanStack Query** for server state
- **Recharts** for data visualization

### Infrastructure
- **Docker** & **Docker Compose** for containerization
- **Nginx** for reverse proxy
- **Prometheus** & **Grafana** for monitoring

## Quick Start

### Prerequisites

- Docker Desktop 24.0+
- Docker Compose 2.23+
- Git 2.40+

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/frkim/ApexTrade.git
   cd ApexTrade
   ```

2. **Set up environment:**
   ```bash
   # Linux/macOS
   ./scripts/setup.sh

   # Windows (PowerShell)
   .\scripts\setup.ps1
   ```

3. **Start development environment:**
   ```bash
   # Using Make
   make dev

   # Or using Docker Compose
   docker compose up -d
   ```

4. **Access the application:**
   - **Frontend**: http://localhost
   - **API Documentation**: http://localhost/api/docs
   - **Grafana Dashboard**: http://localhost:3001

### Using Make Commands

```bash
make dev        # Start development environment
make prod       # Start production environment
make down       # Stop all containers
make logs       # View logs
make migrate    # Run database migrations
make test       # Run all tests
make lint       # Run linters
make build      # Build all containers
```

## Project Structure

```
ApexTrade/
├── backend/                # Python FastAPI backend
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── core/          # Core utilities
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   ├── tasks/         # Celery tasks
│   │   └── integrations/  # Exchange integrations
│   ├── alembic/           # Database migrations
│   └── tests/             # Backend tests
│
├── frontend/              # Next.js frontend
│   ├── src/
│   │   ├── app/          # Next.js App Router pages
│   │   ├── components/   # React components
│   │   ├── lib/          # Utilities
│   │   ├── hooks/        # Custom hooks
│   │   ├── stores/       # Zustand stores
│   │   └── types/        # TypeScript types
│
├── docs/                  # Documentation
│   ├── PRD.md            # Product Requirements
│   ├── TECHNICAL_SPEC.md # Technical Specification
│   ├── ARCHITECTURE.md   # System Architecture
│   ├── API.md            # API Reference
│   └── DEVELOPMENT.md    # Development Guide
│
├── monitoring/            # Monitoring configs
├── nginx/                 # Nginx configuration
├── scripts/              # Build & deployment scripts
└── docker-compose.yml    # Docker Compose configuration
```

## Development

### Backend Development

```bash
# Install dependencies
cd backend
pip install -e ".[dev]"

# Run tests
pytest

# Run linters
ruff check app/
black app/

# Create database migration
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Frontend Development

```bash
# Install dependencies
cd frontend
npm install

# Run development server
npm run dev

# Run linter
npm run lint

# Build for production
npm run build
```

## API Documentation

Once the application is running, access the interactive API documentation at:
- **Swagger UI**: http://localhost/api/docs
- **ReDoc**: http://localhost/api/redoc

## Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Security
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
TIMESCALE_DATABASE_URL=postgresql+asyncpg://user:pass@host:5433/db

# Redis
REDIS_URL=redis://localhost:6379/0

# Exchange API Keys (optional)
BINANCE_API_KEY=your-api-key
BINANCE_API_SECRET=your-api-secret
```

## Documentation

- [Product Requirements (PRD)](docs/PRD.md)
- [Technical Specification](docs/TECHNICAL_SPEC.md)
- [System Architecture](docs/ARCHITECTURE.md)
- [API Reference](docs/API.md)
- [Development Guide](docs/DEVELOPMENT.md)
- [Database Schema](docs/DATABASE_SCHEMA.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
