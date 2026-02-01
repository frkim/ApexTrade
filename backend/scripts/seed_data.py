"""Seed initial data into the database."""

import asyncio
import logging
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select

from app.core.database import async_session_factory
from app.core.security import get_password_hash
from app.models.portfolio import Portfolio
from app.models.strategy import Strategy
from app.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def seed_users() -> list[User]:
    """Seed demo users."""
    async with async_session_factory() as db:
        result = await db.execute(select(User).where(User.email == "demo@apextrade.io"))
        existing = result.scalar_one_or_none()

        if existing:
            logger.info("Demo user already exists")
            return [existing]

        users = [
            User(
                id=uuid4(),
                email="demo@apextrade.io",
                username="demo",
                hashed_password=get_password_hash("demo123456"),
                full_name="Demo User",
                is_active=True,
                is_verified=True,
            ),
            User(
                id=uuid4(),
                email="admin@apextrade.io",
                username="admin",
                hashed_password=get_password_hash("admin123456"),
                full_name="Admin User",
                is_active=True,
                is_verified=True,
                is_superuser=True,
            ),
        ]

        for user in users:
            db.add(user)

        await db.commit()
        logger.info(f"Created {len(users)} demo users")

        for user in users:
            await db.refresh(user)

        return users


async def seed_strategies(user: User) -> list[Strategy]:
    """Seed demo strategies."""
    async with async_session_factory() as db:
        strategies = [
            Strategy(
                name="RSI Oversold Strategy",
                description="Buy when RSI drops below 30, sell when RSI goes above 70",
                symbols=["BTC/USDT", "ETH/USDT"],
                timeframe="1h",
                rules={
                    "conditions": [
                        {"indicator": "rsi_14", "operator": "lt", "value": 30}
                    ],
                    "logic": "and",
                },
                entry_rules=[
                    {
                        "conditions": [
                            {"indicator": "rsi_14", "operator": "lt", "value": 30}
                        ],
                        "logic": "and",
                    }
                ],
                exit_rules=[
                    {
                        "conditions": [
                            {"indicator": "rsi_14", "operator": "gt", "value": 70}
                        ],
                        "logic": "and",
                    }
                ],
                user_id=user.id,
                is_active=False,
            ),
            Strategy(
                name="Golden Cross Strategy",
                description="Buy when 50 EMA crosses above 200 EMA",
                symbols=["BTC/USDT"],
                timeframe="4h",
                rules={
                    "conditions": [
                        {"indicator": "ema_50", "operator": "crosses_above", "value": "$ema_200"}
                    ],
                    "logic": "and",
                },
                user_id=user.id,
                is_active=False,
            ),
            Strategy(
                name="Bollinger Band Bounce",
                description="Buy when price touches lower Bollinger Band with RSI below 40",
                symbols=["ETH/USDT", "SOL/USDT"],
                timeframe="1h",
                rules={
                    "conditions": [
                        {"indicator": "close", "operator": "lte", "value": "$bb_lower"},
                        {"indicator": "rsi_14", "operator": "lt", "value": 40}
                    ],
                    "logic": "and",
                },
                user_id=user.id,
                is_active=False,
            ),
        ]

        for strategy in strategies:
            db.add(strategy)

        await db.commit()
        logger.info(f"Created {len(strategies)} demo strategies")

        return strategies


async def seed_portfolios(user: User) -> list[Portfolio]:
    """Seed demo portfolios."""
    async with async_session_factory() as db:
        portfolios = [
            Portfolio(
                name="Paper Trading Portfolio",
                description="Demo portfolio for paper trading",
                initial_capital=Decimal("10000"),
                cash_balance=Decimal("10000"),
                is_paper=True,
                exchange="binance",
                user_id=user.id,
            ),
            Portfolio(
                name="Crypto Long-Term",
                description="Long-term cryptocurrency holdings",
                initial_capital=Decimal("50000"),
                cash_balance=Decimal("50000"),
                is_paper=True,
                exchange="binance",
                user_id=user.id,
            ),
        ]

        for portfolio in portfolios:
            db.add(portfolio)

        await db.commit()
        logger.info(f"Created {len(portfolios)} demo portfolios")

        return portfolios


async def main() -> None:
    """Run all seed functions."""
    logger.info("Starting database seeding...")

    try:
        users = await seed_users()
        demo_user = users[0]

        await seed_strategies(demo_user)
        await seed_portfolios(demo_user)

        logger.info("Database seeding completed successfully!")
        logger.info("Demo credentials:")
        logger.info("  Email: demo@apextrade.io")
        logger.info("  Password: demo123456")

    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
