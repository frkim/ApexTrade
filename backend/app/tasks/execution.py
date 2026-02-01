"""Trade execution Celery tasks."""

import logging
from decimal import Decimal
from typing import Any

from app.core.celery_app import celery_app
from app.core.database import async_session_factory
from app.core.events import EventTypes, event_bus
from app.services.execution_service import ExecutionService

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def execute_trade_task(
    self,
    portfolio_id: str,
    symbol: str,
    side: str,
    quantity: str,
    strategy_id: str | None = None,
) -> dict[str, Any]:
    """Execute a trade asynchronously."""
    import asyncio

    async def _execute():
        async with async_session_factory() as db:
            service = ExecutionService(db)

            try:
                trade = await service.execute_market_order(
                    portfolio_id=portfolio_id,
                    symbol=symbol,
                    side=side,
                    quantity=Decimal(quantity),
                    strategy_id=strategy_id,
                )

                await event_bus.publish(
                    EventTypes.TRADE_OPENED if side == "buy" else EventTypes.TRADE_CLOSED,
                    {
                        "trade_id": str(trade.id),
                        "portfolio_id": portfolio_id,
                        "symbol": symbol,
                        "side": side,
                        "quantity": quantity,
                        "price": str(trade.filled_price),
                    },
                )

                return {
                    "status": "executed",
                    "trade_id": str(trade.id),
                    "filled_price": str(trade.filled_price),
                    "filled_quantity": str(trade.filled_quantity),
                }

            except Exception as e:
                logger.error(f"Trade execution failed: {e}")
                raise

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        return loop.run_until_complete(_execute())
    except Exception as e:
        raise self.retry(exc=e, countdown=30)


@celery_app.task(bind=True, max_retries=3)
def execute_limit_order_task(
    self,
    portfolio_id: str,
    symbol: str,
    side: str,
    quantity: str,
    limit_price: str,
    strategy_id: str | None = None,
) -> dict[str, Any]:
    """Execute a limit order asynchronously."""
    import asyncio

    async def _execute():
        async with async_session_factory() as db:
            service = ExecutionService(db)

            trade = await service.execute_limit_order(
                portfolio_id=portfolio_id,
                symbol=symbol,
                side=side,
                quantity=Decimal(quantity),
                limit_price=Decimal(limit_price),
                strategy_id=strategy_id,
            )

            return {
                "status": "pending",
                "trade_id": str(trade.id),
                "limit_price": limit_price,
            }

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        return loop.run_until_complete(_execute())
    except Exception as e:
        raise self.retry(exc=e, countdown=30)


@celery_app.task
def cancel_order_task(trade_id: str) -> dict[str, Any]:
    """Cancel a pending order."""
    import asyncio

    async def _cancel():
        async with async_session_factory() as db:
            service = ExecutionService(db)
            trade = await service.cancel_order(trade_id)

            return {
                "status": "cancelled",
                "trade_id": str(trade.id),
            }

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(_cancel())
