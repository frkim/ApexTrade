"""Fetch historical market data and store it."""

import argparse
import asyncio
import logging
from datetime import datetime, timedelta

import pandas as pd

from app.services.market_data_service import MarketDataService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def fetch_and_save_data(
    symbol: str,
    exchange: str,
    timeframe: str,
    start_date: datetime,
    end_date: datetime,
    output_dir: str,
) -> None:
    """Fetch historical data and save to CSV."""
    service = MarketDataService()

    try:
        logger.info(f"Fetching data for {symbol} from {exchange}")
        logger.info(f"Period: {start_date} to {end_date}")
        logger.info(f"Timeframe: {timeframe}")

        data = await service.get_ohlcv(
            symbol=symbol,
            exchange=exchange,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            limit=10000,
        )

        if not data:
            logger.warning(f"No data returned for {symbol}")
            return

        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.set_index("timestamp", inplace=True)

        symbol_clean = symbol.replace("/", "_").replace(":", "_")
        filename = f"{output_dir}/{symbol_clean}_{timeframe}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"

        df.to_csv(filename)
        logger.info(f"Saved {len(df)} records to {filename}")

    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {e}")
        raise

    finally:
        await service.close_all()


async def fetch_multiple_symbols(
    symbols: list[str],
    exchange: str,
    timeframe: str,
    days: int,
    output_dir: str,
) -> None:
    """Fetch data for multiple symbols."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    for symbol in symbols:
        try:
            await fetch_and_save_data(
                symbol=symbol,
                exchange=exchange,
                timeframe=timeframe,
                start_date=start_date,
                end_date=end_date,
                output_dir=output_dir,
            )
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Failed to fetch {symbol}: {e}")
            continue


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Fetch historical market data",
    )

    parser.add_argument(
        "--symbols",
        type=str,
        nargs="+",
        default=["BTC/USDT", "ETH/USDT"],
        help="Trading symbols to fetch (e.g., BTC/USDT ETH/USDT)",
    )

    parser.add_argument(
        "--exchange",
        type=str,
        default="binance",
        help="Exchange to fetch from (default: binance)",
    )

    parser.add_argument(
        "--timeframe",
        type=str,
        default="1h",
        help="Candlestick timeframe (default: 1h)",
    )

    parser.add_argument(
        "--days",
        type=int,
        default=365,
        help="Number of days of history to fetch (default: 365)",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="./data",
        help="Output directory for CSV files (default: ./data)",
    )

    return parser.parse_args()


async def main() -> None:
    """Main entry point."""
    args = parse_args()

    import os
    os.makedirs(args.output, exist_ok=True)

    logger.info("Starting historical data fetch")
    logger.info(f"Symbols: {args.symbols}")
    logger.info(f"Exchange: {args.exchange}")
    logger.info(f"Timeframe: {args.timeframe}")
    logger.info(f"Days: {args.days}")
    logger.info(f"Output: {args.output}")

    await fetch_multiple_symbols(
        symbols=args.symbols,
        exchange=args.exchange,
        timeframe=args.timeframe,
        days=args.days,
        output_dir=args.output,
    )

    logger.info("Data fetch completed")


if __name__ == "__main__":
    asyncio.run(main())
