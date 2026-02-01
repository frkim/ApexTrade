"""Trade history endpoints."""

import logging
from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.portfolio import Portfolio
from app.models.trade import Trade
from app.schemas.trade import TradeResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=list[TradeResponse])
async def list_trades(
    db: DbSession,
    current_user: CurrentUser,
    portfolio_id: UUID | None = None,
    strategy_id: UUID | None = None,
    symbol: str | None = None,
    side: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
) -> list[Trade]:
    """List all trades for current user with optional filters."""
    query = select(Trade).join(Portfolio).where(Portfolio.user_id == current_user.id)

    if portfolio_id:
        query = query.where(Trade.portfolio_id == portfolio_id)
    if strategy_id:
        query = query.where(Trade.strategy_id == strategy_id)
    if symbol:
        query = query.where(Trade.symbol == symbol)
    if side:
        query = query.where(Trade.side == side)
    if start_date:
        query = query.where(Trade.executed_at >= start_date)
    if end_date:
        query = query.where(Trade.executed_at <= end_date)

    query = query.offset(skip).limit(limit).order_by(Trade.executed_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/summary")
async def get_trades_summary(
    db: DbSession,
    current_user: CurrentUser,
    portfolio_id: UUID | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
) -> dict:
    """Get trade summary statistics."""
    query = select(Trade).join(Portfolio).where(Portfolio.user_id == current_user.id)

    if portfolio_id:
        query = query.where(Trade.portfolio_id == portfolio_id)
    if start_date:
        query = query.where(Trade.executed_at >= start_date)
    if end_date:
        query = query.where(Trade.executed_at <= end_date)

    result = await db.execute(query)
    trades = list(result.scalars().all())

    if not trades:
        return {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0.0,
            "total_profit": 0.0,
            "total_loss": 0.0,
            "net_pnl": 0.0,
        }

    total_trades = len(trades)
    winning_trades = sum(1 for t in trades if t.pnl and t.pnl > 0)
    losing_trades = sum(1 for t in trades if t.pnl and t.pnl < 0)
    total_profit = sum(float(t.pnl) for t in trades if t.pnl and t.pnl > 0)
    total_loss = sum(float(t.pnl) for t in trades if t.pnl and t.pnl < 0)
    net_pnl = total_profit + total_loss

    return {
        "total_trades": total_trades,
        "winning_trades": winning_trades,
        "losing_trades": losing_trades,
        "win_rate": winning_trades / total_trades * 100 if total_trades > 0 else 0.0,
        "total_profit": total_profit,
        "total_loss": total_loss,
        "net_pnl": net_pnl,
    }


@router.get("/{trade_id}", response_model=TradeResponse)
async def get_trade(
    trade_id: UUID,
    db: DbSession,
    current_user: CurrentUser,
) -> Trade:
    """Get a specific trade."""
    result = await db.execute(
        select(Trade)
        .join(Portfolio)
        .where(
            Trade.id == trade_id,
            Portfolio.user_id == current_user.id,
        )
    )
    trade = result.scalar_one_or_none()

    if not trade:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade not found",
        )

    return trade
