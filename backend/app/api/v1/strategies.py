"""Strategies CRUD endpoints."""

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUser, DbSession
from app.models.strategy import Strategy
from app.schemas.strategy import StrategyCreate, StrategyResponse, StrategyUpdate

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=list[StrategyResponse])
async def list_strategies(
    db: DbSession,
    current_user: CurrentUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    is_active: bool | None = None,
) -> list[Strategy]:
    """List all strategies for current user."""
    query = select(Strategy).where(Strategy.user_id == current_user.id)

    if is_active is not None:
        query = query.where(Strategy.is_active == is_active)

    query = query.offset(skip).limit(limit).order_by(Strategy.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


@router.post("", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
async def create_strategy(
    request: StrategyCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> Strategy:
    """Create a new strategy."""
    strategy = Strategy(
        name=request.name,
        description=request.description,
        rules=request.rules.model_dump() if request.rules else {},
        entry_rules=request.entry_rules,
        exit_rules=request.exit_rules,
        symbols=request.symbols,
        timeframe=request.timeframe,
        user_id=current_user.id,
    )
    db.add(strategy)
    await db.flush()
    await db.refresh(strategy)

    logger.info(f"Strategy created: {strategy.name} by user {current_user.id}")
    return strategy


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> Strategy:
    """Get a specific strategy."""
    result = await db.execute(
        select(Strategy).where(
            Strategy.id == strategy_id,
            Strategy.user_id == current_user.id,
        )
    )
    strategy = result.scalar_one_or_none()

    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found",
        )

    return strategy


@router.put("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(
    strategy_id: UUID,
    request: StrategyUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> Strategy:
    """Update a strategy."""
    result = await db.execute(
        select(Strategy).where(
            Strategy.id == strategy_id,
            Strategy.user_id == current_user.id,
        )
    )
    strategy = result.scalar_one_or_none()

    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found",
        )

    update_data = request.model_dump(exclude_unset=True)
    if "rules" in update_data and update_data["rules"]:
        update_data["rules"] = update_data["rules"].model_dump()

    for field, value in update_data.items():
        setattr(strategy, field, value)

    await db.flush()
    await db.refresh(strategy)

    logger.info(f"Strategy updated: {strategy.name}")
    return strategy


@router.delete("/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_strategy(
    strategy_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    """Delete a strategy."""
    result = await db.execute(
        select(Strategy).where(
            Strategy.id == strategy_id,
            Strategy.user_id == current_user.id,
        )
    )
    strategy = result.scalar_one_or_none()

    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found",
        )

    await db.delete(strategy)
    logger.info(f"Strategy deleted: {strategy.name}")


@router.post("/{strategy_id}/activate", response_model=StrategyResponse)
async def activate_strategy(
    strategy_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> Strategy:
    """Activate a strategy for live trading."""
    result = await db.execute(
        select(Strategy).where(
            Strategy.id == strategy_id,
            Strategy.user_id == current_user.id,
        )
    )
    strategy = result.scalar_one_or_none()

    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found",
        )

    strategy.is_active = True
    await db.flush()
    await db.refresh(strategy)

    logger.info(f"Strategy activated: {strategy.name}")
    return strategy


@router.post("/{strategy_id}/deactivate", response_model=StrategyResponse)
async def deactivate_strategy(
    strategy_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> Strategy:
    """Deactivate a strategy."""
    result = await db.execute(
        select(Strategy).where(
            Strategy.id == strategy_id,
            Strategy.user_id == current_user.id,
        )
    )
    strategy = result.scalar_one_or_none()

    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found",
        )

    strategy.is_active = False
    await db.flush()
    await db.refresh(strategy)

    logger.info(f"Strategy deactivated: {strategy.name}")
    return strategy
