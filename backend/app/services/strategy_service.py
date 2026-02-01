"""Strategy service for CRUD and activation."""

import logging
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.strategy import Strategy
from app.models.user import User

logger = logging.getLogger(__name__)


class StrategyService:
    """Service for managing trading strategies."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, strategy_id: UUID, user_id: UUID) -> Strategy | None:
        """Get strategy by ID for a specific user."""
        result = await self.db.execute(
            select(Strategy).where(
                Strategy.id == strategy_id,
                Strategy.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_strategies(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20,
        is_active: bool | None = None,
    ) -> list[Strategy]:
        """List strategies for a user."""
        query = select(Strategy).where(Strategy.user_id == user_id)

        if is_active is not None:
            query = query.where(Strategy.is_active == is_active)

        query = query.offset(skip).limit(limit).order_by(Strategy.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def list_active_strategies(self) -> list[Strategy]:
        """List all active strategies."""
        result = await self.db.execute(
            select(Strategy).where(Strategy.is_active.is_(True))
        )
        return list(result.scalars().all())

    async def create_strategy(
        self,
        user: User,
        name: str,
        description: str | None = None,
        rules: dict[str, Any] | None = None,
        symbols: list[str] | None = None,
        timeframe: str = "1h",
    ) -> Strategy:
        """Create a new strategy."""
        strategy = Strategy(
            name=name,
            description=description,
            rules=rules or {},
            symbols=symbols or [],
            timeframe=timeframe,
            user_id=user.id,
        )
        self.db.add(strategy)
        await self.db.flush()
        await self.db.refresh(strategy)

        logger.info(f"Strategy created: {strategy.name} by user {user.id}")
        return strategy

    async def update_strategy(
        self,
        strategy: Strategy,
        **kwargs: Any,
    ) -> Strategy:
        """Update a strategy."""
        for field, value in kwargs.items():
            if hasattr(strategy, field):
                setattr(strategy, field, value)

        await self.db.flush()
        await self.db.refresh(strategy)

        logger.info(f"Strategy updated: {strategy.name}")
        return strategy

    async def delete_strategy(self, strategy: Strategy) -> None:
        """Delete a strategy."""
        await self.db.delete(strategy)
        logger.info(f"Strategy deleted: {strategy.name}")

    async def activate_strategy(self, strategy: Strategy) -> Strategy:
        """Activate a strategy for live trading."""
        strategy.is_active = True
        await self.db.flush()
        await self.db.refresh(strategy)

        logger.info(f"Strategy activated: {strategy.name}")
        return strategy

    async def deactivate_strategy(self, strategy: Strategy) -> Strategy:
        """Deactivate a strategy."""
        strategy.is_active = False
        await self.db.flush()
        await self.db.refresh(strategy)

        logger.info(f"Strategy deactivated: {strategy.name}")
        return strategy

    async def clone_strategy(
        self,
        strategy: Strategy,
        new_name: str | None = None,
    ) -> Strategy:
        """Clone an existing strategy."""
        cloned = Strategy(
            name=new_name or f"{strategy.name} (Copy)",
            description=strategy.description,
            rules=strategy.rules.copy() if strategy.rules else {},
            entry_rules=strategy.entry_rules.copy() if strategy.entry_rules else None,
            exit_rules=strategy.exit_rules.copy() if strategy.exit_rules else None,
            symbols=strategy.symbols.copy() if strategy.symbols else [],
            timeframe=strategy.timeframe,
            user_id=strategy.user_id,
            is_active=False,
        )
        self.db.add(cloned)
        await self.db.flush()
        await self.db.refresh(cloned)

        logger.info(f"Strategy cloned: {strategy.name} -> {cloned.name}")
        return cloned
