"""Strategy evaluation Celery tasks."""

import logging
from typing import Any

from app.celery_app import celery_app
from app.core.database import async_session_factory
from app.core.events import EventTypes, event_bus
from app.services.market_data_service import MarketDataService
from app.services.rule_engine import RuleEngine
from app.services.strategy_service import StrategyService

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def evaluate_strategy_task(self, strategy_id: str) -> dict[str, Any]:
    """Evaluate a single strategy against current market data."""
    import asyncio

    import pandas as pd

    async def _evaluate():
        async with async_session_factory() as db:
            from sqlalchemy import select

            from app.models.strategy import Strategy

            result = await db.execute(
                select(Strategy).where(Strategy.id == strategy_id)
            )
            strategy = result.scalar_one_or_none()

            if not strategy or not strategy.is_active:
                return {"status": "skipped", "reason": "Strategy inactive or not found"}

            market_service = MarketDataService()
            rule_engine = RuleEngine()
            signals = []

            try:
                for symbol in strategy.symbols:
                    data = await market_service.get_ohlcv(
                        symbol=symbol,
                        timeframe=strategy.timeframe,
                        limit=100,
                    )

                    if not data:
                        continue

                    df = pd.DataFrame(data)
                    df["timestamp"] = pd.to_datetime(df["timestamp"])
                    df.set_index("timestamp", inplace=True)

                    entry_result = rule_engine.evaluate_rules(strategy.rules, df, -1)

                    if entry_result.get("passed"):
                        signal = {
                            "strategy_id": str(strategy.id),
                            "symbol": symbol,
                            "signal": "entry",
                            "details": entry_result.get("details", []),
                        }
                        signals.append(signal)

                        await event_bus.publish(EventTypes.STRATEGY_SIGNAL, signal)

                return {
                    "status": "completed",
                    "strategy_id": strategy_id,
                    "signals": signals,
                }

            finally:
                await market_service.close_all()

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(_evaluate())


@celery_app.task
def evaluate_active_strategies_task() -> dict[str, Any]:
    """Periodic task to evaluate all active strategies."""
    import asyncio

    async def _evaluate_all():
        async with async_session_factory() as db:
            service = StrategyService(db)
            strategies = await service.list_active_strategies()

            results = []
            for strategy in strategies:
                try:
                    result = evaluate_strategy_task.delay(str(strategy.id))
                    results.append({
                        "strategy_id": str(strategy.id),
                        "task_id": result.id,
                    })
                except Exception as e:
                    logger.error(f"Failed to queue strategy {strategy.id}: {e}")
                    results.append({
                        "strategy_id": str(strategy.id),
                        "error": str(e),
                    })

            return {
                "status": "queued",
                "strategies_count": len(strategies),
                "results": results,
            }

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(_evaluate_all())
