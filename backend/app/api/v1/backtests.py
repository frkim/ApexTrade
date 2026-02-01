"""Backtest endpoints."""

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUser, DbSession
from app.models.backtest import Backtest, BacktestTrade
from app.models.strategy import Strategy
from app.schemas.backtest import BacktestCreate, BacktestResponse, BacktestResult
from app.tasks.backtest import run_backtest_task

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=list[BacktestResponse])
async def list_backtests(
    db: DbSession,
    current_user: CurrentUser,
    strategy_id: UUID | None = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[Backtest]:
    """List all backtests for current user."""
    query = (
        select(Backtest)
        .join(Strategy)
        .where(Strategy.user_id == current_user.id)
    )

    if strategy_id:
        query = query.where(Backtest.strategy_id == strategy_id)

    query = query.offset(skip).limit(limit).order_by(Backtest.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


@router.post("", response_model=BacktestResponse, status_code=status.HTTP_202_ACCEPTED)
async def run_backtest(
    request: BacktestCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> Backtest:
    """Run a new backtest."""
    result = await db.execute(
        select(Strategy).where(
            Strategy.id == request.strategy_id,
            Strategy.user_id == current_user.id,
        )
    )
    strategy = result.scalar_one_or_none()

    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found",
        )

    backtest = Backtest(
        strategy_id=request.strategy_id,
        start_date=request.start_date,
        end_date=request.end_date,
        initial_capital=request.initial_capital,
        symbols=request.symbols or strategy.symbols,
        timeframe=request.timeframe or strategy.timeframe,
        status="pending",
    )
    db.add(backtest)
    await db.flush()
    await db.refresh(backtest)

    run_backtest_task.delay(str(backtest.id))

    logger.info(f"Backtest queued: {backtest.id}")
    return backtest


@router.get("/{backtest_id}", response_model=BacktestResponse)
async def get_backtest(
    backtest_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> Backtest:
    """Get a specific backtest."""
    result = await db.execute(
        select(Backtest)
        .options(selectinload(Backtest.trades))
        .join(Strategy)
        .where(
            Backtest.id == backtest_id,
            Strategy.user_id == current_user.id,
        )
    )
    backtest = result.scalar_one_or_none()

    if not backtest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Backtest not found",
        )

    return backtest


@router.get("/{backtest_id}/results", response_model=BacktestResult)
async def get_backtest_results(
    backtest_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> dict:
    """Get backtest results and performance metrics."""
    result = await db.execute(
        select(Backtest)
        .options(selectinload(Backtest.trades))
        .join(Strategy)
        .where(
            Backtest.id == backtest_id,
            Strategy.user_id == current_user.id,
        )
    )
    backtest = result.scalar_one_or_none()

    if not backtest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Backtest not found",
        )

    if backtest.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Backtest is not completed. Current status: {backtest.status}",
        )

    return {
        "backtest_id": backtest.id,
        "status": backtest.status,
        "initial_capital": backtest.initial_capital,
        "final_capital": backtest.final_capital,
        "total_return": backtest.total_return,
        "total_trades": backtest.total_trades,
        "winning_trades": backtest.winning_trades,
        "losing_trades": backtest.losing_trades,
        "win_rate": backtest.win_rate,
        "max_drawdown": backtest.max_drawdown,
        "sharpe_ratio": backtest.sharpe_ratio,
        "profit_factor": backtest.profit_factor,
        "trades": backtest.trades,
        "equity_curve": backtest.equity_curve or [],
    }


@router.delete("/{backtest_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_backtest(
    backtest_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    """Delete a backtest."""
    result = await db.execute(
        select(Backtest)
        .join(Strategy)
        .where(
            Backtest.id == backtest_id,
            Strategy.user_id == current_user.id,
        )
    )
    backtest = result.scalar_one_or_none()

    if not backtest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Backtest not found",
        )

    await db.delete(backtest)
    logger.info(f"Backtest deleted: {backtest_id}")
