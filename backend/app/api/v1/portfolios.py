"""Portfolio endpoints."""

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUser, DbSession
from app.models.portfolio import Portfolio, Position
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioResponse,
    PortfolioUpdate,
    PositionCreate,
    PositionResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=list[PortfolioResponse])
async def list_portfolios(
    db: DbSession,
    current_user: CurrentUser,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[Portfolio]:
    """List all portfolios for current user."""
    query = (
        select(Portfolio)
        .options(selectinload(Portfolio.positions))
        .where(Portfolio.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .order_by(Portfolio.created_at.desc())
    )
    result = await db.execute(query)
    return list(result.scalars().all())


@router.post("", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    request: PortfolioCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> Portfolio:
    """Create a new portfolio."""
    portfolio = Portfolio(
        name=request.name,
        description=request.description,
        initial_capital=request.initial_capital,
        cash_balance=request.initial_capital,
        is_paper=request.is_paper,
        exchange=request.exchange,
        user_id=current_user.id,
    )
    db.add(portfolio)
    await db.flush()
    await db.refresh(portfolio)

    logger.info(f"Portfolio created: {portfolio.name} by user {current_user.id}")
    return portfolio


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(
    portfolio_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> Portfolio:
    """Get a specific portfolio with positions."""
    result = await db.execute(
        select(Portfolio)
        .options(selectinload(Portfolio.positions))
        .where(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id,
        )
    )
    portfolio = result.scalar_one_or_none()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )

    return portfolio


@router.put("/{portfolio_id}", response_model=PortfolioResponse)
async def update_portfolio(
    portfolio_id: UUID,
    request: PortfolioUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> Portfolio:
    """Update a portfolio."""
    result = await db.execute(
        select(Portfolio).where(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id,
        )
    )
    portfolio = result.scalar_one_or_none()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(portfolio, field, value)

    await db.flush()
    await db.refresh(portfolio)

    logger.info(f"Portfolio updated: {portfolio.name}")
    return portfolio


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio(
    portfolio_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    """Delete a portfolio."""
    result = await db.execute(
        select(Portfolio).where(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id,
        )
    )
    portfolio = result.scalar_one_or_none()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )

    await db.delete(portfolio)
    logger.info(f"Portfolio deleted: {portfolio.name}")


@router.get("/{portfolio_id}/positions", response_model=list[PositionResponse])
async def list_positions(
    portfolio_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> list[Position]:
    """List all positions in a portfolio."""
    result = await db.execute(
        select(Portfolio).where(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id,
        )
    )
    portfolio = result.scalar_one_or_none()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )

    result = await db.execute(select(Position).where(Position.portfolio_id == portfolio_id))
    return list(result.scalars().all())


@router.post(
    "/{portfolio_id}/positions",
    response_model=PositionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_position(
    portfolio_id: UUID,
    request: PositionCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> Position:
    """Create a new position in a portfolio."""
    result = await db.execute(
        select(Portfolio).where(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id,
        )
    )
    portfolio = result.scalar_one_or_none()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )

    position = Position(
        portfolio_id=portfolio_id,
        symbol=request.symbol,
        quantity=request.quantity,
        average_entry_price=request.average_entry_price,
        current_price=request.current_price or request.average_entry_price,
        side=request.side,
    )
    db.add(position)
    await db.flush()
    await db.refresh(position)

    logger.info(f"Position created: {position.symbol} in portfolio {portfolio.name}")
    return position


@router.delete("/{portfolio_id}/positions/{position_id}", status_code=status.HTTP_204_NO_CONTENT)
async def close_position(
    portfolio_id: UUID,
    position_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    """Close/delete a position."""
    result = await db.execute(
        select(Portfolio).where(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == current_user.id,
        )
    )
    portfolio = result.scalar_one_or_none()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )

    result = await db.execute(
        select(Position).where(
            Position.id == position_id,
            Position.portfolio_id == portfolio_id,
        )
    )
    position = result.scalar_one_or_none()

    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Position not found",
        )

    await db.delete(position)
    logger.info(f"Position closed: {position.symbol}")
