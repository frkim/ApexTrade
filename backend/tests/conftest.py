"""Pytest fixtures for testing."""

import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any
from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import async_session_factory
from app.core.security import create_access_token, get_password_hash
from app.main import app
from app.models import Base
from app.models.user import User

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def async_engine():
    """Create async engine for tests."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create database session for tests."""
    async_session = sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        id=uuid4(),
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User",
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def auth_headers(test_user: User) -> dict[str, str]:
    """Create authentication headers for test user."""
    token = create_access_token(subject=str(test_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def client() -> Generator[TestClient, None, None]:
    """Create test client."""
    with TestClient(app) as c:
        yield c


@pytest_asyncio.fixture(scope="function")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create async test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.fixture
def sample_strategy_data() -> dict[str, Any]:
    """Sample strategy data for testing."""
    return {
        "name": "Test Strategy",
        "description": "A test trading strategy",
        "symbols": ["BTC/USDT", "ETH/USDT"],
        "timeframe": "1h",
        "rules": {
            "conditions": [
                {
                    "indicator": "rsi_14",
                    "operator": "lt",
                    "value": 30,
                }
            ],
            "logic": "and",
        },
    }


@pytest.fixture
def sample_portfolio_data() -> dict[str, Any]:
    """Sample portfolio data for testing."""
    return {
        "name": "Test Portfolio",
        "description": "A test portfolio",
        "initial_capital": "10000.00",
        "is_paper": True,
        "exchange": "binance",
    }


@pytest.fixture
def sample_ohlcv_data() -> list[dict[str, Any]]:
    """Sample OHLCV data for testing."""
    import pandas as pd
    from datetime import datetime, timedelta

    data = []
    base_time = datetime.now() - timedelta(days=100)
    price = 100.0

    for i in range(100):
        change = (i % 10 - 5) * 0.01
        price = price * (1 + change)

        data.append({
            "timestamp": base_time + timedelta(hours=i),
            "open": price * 0.99,
            "high": price * 1.02,
            "low": price * 0.98,
            "close": price,
            "volume": 1000 + i * 10,
        })

    return data
