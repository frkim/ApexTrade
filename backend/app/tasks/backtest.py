"""Backtest Celery tasks."""

import logging
from typing import Any

from app.celery_app import celery_app
from app.core.database import async_session_factory
from app.core.events import EventTypes, event_bus
from app.services.backtest_service import BacktestService

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def run_backtest_task(self, backtest_id: str) -> dict[str, Any]:
    """Celery task to run a backtest asynchronously."""
    import asyncio

    async def _run():
        async with async_session_factory() as db:
            service = BacktestService(db)

            await event_bus.publish(
                EventTypes.BACKTEST_STARTED,
                {"backtest_id": backtest_id},
            )

            try:
                result = await service.run_backtest(backtest_id)

                await event_bus.publish(
                    EventTypes.BACKTEST_COMPLETED,
                    {
                        "backtest_id": backtest_id,
                        "total_return": result["total_return"],
                        "total_trades": result["total_trades"],
                    },
                )

                return {
                    "status": "completed",
                    "backtest_id": backtest_id,
                    "total_return": result["total_return"],
                    "total_trades": result["total_trades"],
                }

            except Exception as e:
                await event_bus.publish(
                    EventTypes.BACKTEST_FAILED,
                    {"backtest_id": backtest_id, "error": str(e)},
                )
                raise

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        return loop.run_until_complete(_run())
    except Exception as e:
        logger.error(f"Backtest task failed: {e}")
        raise self.retry(exc=e, countdown=60)
