"""Market data Celery tasks."""

import logging
from datetime import datetime
from typing import Any

from app.celery_app import celery_app
from app.core.events import EventTypes, event_bus
from app.services.market_data_service import MarketDataService

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def fetch_historical_data_task(
    self,
    symbol: str,
    exchange: str = "binance",
    timeframe: str = "1h",
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 1000,
) -> dict[str, Any]:
    """Fetch historical market data and cache it."""
    import asyncio

    async def _fetch():
        service = MarketDataService()

        try:
            start = datetime.fromisoformat(start_date) if start_date else None
            end = datetime.fromisoformat(end_date) if end_date else None

            data = await service.get_ohlcv(
                symbol=symbol,
                exchange=exchange,
                timeframe=timeframe,
                start_date=start,
                end_date=end,
                limit=limit,
            )

            await event_bus.publish(
                EventTypes.MARKET_DATA_UPDATED,
                {
                    "symbol": symbol,
                    "exchange": exchange,
                    "timeframe": timeframe,
                    "count": len(data),
                },
            )

            return {
                "status": "completed",
                "symbol": symbol,
                "exchange": exchange,
                "timeframe": timeframe,
                "count": len(data),
            }

        finally:
            await service.close_all()

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        return loop.run_until_complete(_fetch())
    except Exception as e:
        logger.error(f"Failed to fetch historical data: {e}")
        raise self.retry(exc=e, countdown=60)


@celery_app.task
def update_ticker_cache_task(
    symbols: list[str],
    exchange: str = "binance",
) -> dict[str, Any]:
    """Update ticker cache for multiple symbols."""
    import asyncio

    async def _update():
        service = MarketDataService()
        results = {}

        try:
            for symbol in symbols:
                try:
                    ticker = await service.get_ticker(symbol, exchange)
                    results[symbol] = {
                        "last": ticker.get("last"),
                        "bid": ticker.get("bid"),
                        "ask": ticker.get("ask"),
                    }
                except Exception as e:
                    logger.error(f"Failed to fetch ticker for {symbol}: {e}")
                    results[symbol] = {"error": str(e)}

            return {
                "status": "completed",
                "exchange": exchange,
                "results": results,
            }

        finally:
            await service.close_all()

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(_update())


@celery_app.task
def fetch_symbols_task(
    exchange: str = "binance",
    quote_currency: str | None = None,
) -> dict[str, Any]:
    """Fetch available trading symbols from an exchange."""
    import asyncio

    async def _fetch():
        service = MarketDataService()

        try:
            symbols = await service.get_symbols(
                exchange=exchange,
                quote_currency=quote_currency,
                limit=1000,
            )

            return {
                "status": "completed",
                "exchange": exchange,
                "count": len(symbols),
                "symbols": [s["symbol"] for s in symbols],
            }

        finally:
            await service.close_all()

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(_fetch())
