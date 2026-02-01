"""Market data endpoints."""

import logging
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DbSession
from app.schemas.market_data import OHLCVResponse, SymbolResponse
from app.services.market_data_service import MarketDataService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/symbols", response_model=list[SymbolResponse])
async def list_symbols(
    current_user: CurrentUser,
    exchange: str = "binance",
    quote_currency: str | None = None,
    search: str | None = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> list[dict]:
    """List available trading symbols."""
    service = MarketDataService()

    try:
        symbols = await service.get_symbols(
            exchange=exchange,
            quote_currency=quote_currency,
            search=search,
            limit=limit,
        )
        return symbols
    except Exception as e:
        logger.error(f"Error fetching symbols: {e}")
        return []


@router.get("/ohlcv/{symbol}", response_model=OHLCVResponse)
async def get_ohlcv(
    symbol: str,
    current_user: CurrentUser,
    exchange: str = "binance",
    timeframe: str = "1h",
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 500,
) -> dict:
    """Get OHLCV candlestick data for a symbol."""
    service = MarketDataService()

    try:
        data = await service.get_ohlcv(
            symbol=symbol,
            exchange=exchange,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )
        return {
            "symbol": symbol,
            "exchange": exchange,
            "timeframe": timeframe,
            "data": data,
        }
    except Exception as e:
        logger.error(f"Error fetching OHLCV data: {e}")
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch market data: {str(e)}",
        )


@router.get("/ticker/{symbol}")
async def get_ticker(
    symbol: str,
    current_user: CurrentUser,
    exchange: str = "binance",
) -> dict:
    """Get current ticker data for a symbol."""
    service = MarketDataService()

    try:
        ticker = await service.get_ticker(symbol=symbol, exchange=exchange)
        return ticker
    except Exception as e:
        logger.error(f"Error fetching ticker: {e}")
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch ticker: {str(e)}",
        )


@router.get("/orderbook/{symbol}")
async def get_orderbook(
    symbol: str,
    current_user: CurrentUser,
    exchange: str = "binance",
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> dict:
    """Get order book for a symbol."""
    service = MarketDataService()

    try:
        orderbook = await service.get_orderbook(
            symbol=symbol,
            exchange=exchange,
            limit=limit,
        )
        return orderbook
    except Exception as e:
        logger.error(f"Error fetching orderbook: {e}")
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch orderbook: {str(e)}",
        )
