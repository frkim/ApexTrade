"""Execution service for order execution."""

import logging
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.portfolio import Portfolio, Position
from app.models.trade import Trade

logger = logging.getLogger(__name__)


class ExecutionService:
    """Service for executing trades."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def execute_market_order(
        self,
        portfolio_id: UUID,
        symbol: str,
        side: str,
        quantity: Decimal,
        strategy_id: UUID | None = None,
    ) -> Trade:
        """Execute a market order."""
        result = await self.db.execute(select(Portfolio).where(Portfolio.id == portfolio_id))
        portfolio = result.scalar_one_or_none()

        if not portfolio:
            raise ValueError(f"Portfolio not found: {portfolio_id}")

        current_price = await self._get_current_price(symbol, portfolio.exchange)

        trade = Trade(
            portfolio_id=portfolio_id,
            strategy_id=strategy_id,
            symbol=symbol,
            side=side,
            order_type="market",
            quantity=quantity,
            price=current_price,
            status="pending",
        )
        self.db.add(trade)
        await self.db.flush()

        try:
            # Execute trade - methods modify portfolio/positions directly
            if portfolio.is_paper:
                await self._execute_paper_trade(trade, portfolio, current_price)
            else:
                await self._execute_live_trade(trade, portfolio)

            trade.status = "filled"
            trade.filled_quantity = trade.quantity
            trade.filled_price = current_price
            trade.executed_at = datetime.now(UTC)

            await self._update_position(portfolio, trade)

            await self.db.flush()
            await self.db.refresh(trade)

            logger.info(f"Trade executed: {trade.symbol} {trade.side} {trade.quantity}")
            return trade

        except Exception as e:
            trade.status = "failed"
            trade.notes = str(e)
            await self.db.flush()
            logger.error(f"Trade execution failed: {e}")
            raise

    async def execute_limit_order(
        self,
        portfolio_id: UUID,
        symbol: str,
        side: str,
        quantity: Decimal,
        limit_price: Decimal,
        strategy_id: UUID | None = None,
    ) -> Trade:
        """Execute a limit order."""
        trade = Trade(
            portfolio_id=portfolio_id,
            strategy_id=strategy_id,
            symbol=symbol,
            side=side,
            order_type="limit",
            quantity=quantity,
            price=limit_price,
            status="pending",
        )
        self.db.add(trade)
        await self.db.flush()
        await self.db.refresh(trade)

        logger.info(f"Limit order placed: {trade.symbol} {trade.side} @ {limit_price}")
        return trade

    async def cancel_order(self, trade_id: UUID) -> Trade:
        """Cancel a pending order."""
        result = await self.db.execute(select(Trade).where(Trade.id == trade_id))
        trade = result.scalar_one_or_none()

        if not trade:
            raise ValueError(f"Trade not found: {trade_id}")

        if trade.status != "pending":
            raise ValueError(f"Cannot cancel trade with status: {trade.status}")

        trade.status = "cancelled"
        await self.db.flush()
        await self.db.refresh(trade)

        logger.info(f"Order cancelled: {trade_id}")
        return trade

    async def _execute_paper_trade(
        self,
        trade: Trade,
        portfolio: Portfolio,
        price: Decimal,
    ) -> dict[str, Any]:
        """Execute a paper trade (simulated)."""
        total_value = trade.quantity * price
        commission = total_value * Decimal("0.001")  # 0.1% commission

        if trade.side == "buy":
            if portfolio.cash_balance < total_value + commission:
                raise ValueError("Insufficient funds")
            portfolio.cash_balance -= total_value + commission
        else:
            portfolio.cash_balance += total_value - commission

        trade.commission = commission
        await self.db.flush()

        return {
            "filled_price": price,
            "filled_quantity": trade.quantity,
            "commission": commission,
        }

    async def _execute_live_trade(
        self,
        trade: Trade,
        portfolio: Portfolio,
    ) -> dict[str, Any]:
        """Execute a live trade through exchange."""
        from app.integrations.binance import BinanceExchange

        exchange = BinanceExchange()
        result = await exchange.create_order(
            symbol=trade.symbol,
            side=trade.side,
            order_type=trade.order_type,
            quantity=float(trade.quantity),
        )

        trade.exchange_order_id = result.get("order_id")
        return result

    async def _update_position(
        self,
        portfolio: Portfolio,
        trade: Trade,
    ) -> None:
        """Update portfolio position after trade."""
        result = await self.db.execute(
            select(Position).where(
                Position.portfolio_id == portfolio.id,
                Position.symbol == trade.symbol,
            )
        )
        position = result.scalar_one_or_none()

        if trade.side == "buy":
            if position:
                total_quantity = position.quantity + trade.quantity
                total_cost = (
                    position.quantity * position.average_entry_price
                    + trade.quantity * trade.filled_price
                )
                position.average_entry_price = total_cost / total_quantity
                position.quantity = total_quantity
                position.current_price = trade.filled_price
            else:
                position = Position(
                    portfolio_id=portfolio.id,
                    symbol=trade.symbol,
                    quantity=trade.quantity,
                    average_entry_price=trade.filled_price,
                    current_price=trade.filled_price,
                    side="long",
                )
                self.db.add(position)
        else:
            if position:
                if position.quantity <= trade.quantity:
                    pnl = (trade.filled_price - position.average_entry_price) * position.quantity
                    trade.pnl = pnl
                    await self.db.delete(position)
                else:
                    pnl = (trade.filled_price - position.average_entry_price) * trade.quantity
                    trade.pnl = pnl
                    position.quantity -= trade.quantity
                    position.current_price = trade.filled_price

        await self.db.flush()

    async def _get_current_price(
        self,
        symbol: str,
        exchange: str | None = None,
    ) -> Decimal:
        """Get current market price for a symbol."""
        from app.services.market_data_service import MarketDataService

        service = MarketDataService()
        ticker = await service.get_ticker(symbol, exchange or "binance")
        return Decimal(str(ticker.get("last", 0)))
