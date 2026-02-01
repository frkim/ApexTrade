"""Backtest service for running backtests."""

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.backtest import Backtest, BacktestTrade
from app.models.strategy import Strategy
from app.services.market_data_service import MarketDataService
from app.services.rule_engine import RuleEngine

logger = logging.getLogger(__name__)


class BacktestService:
    """Service for running backtests on trading strategies."""

    def __init__(self, db: AsyncSession | None = None) -> None:
        self.db = db
        self.rule_engine = RuleEngine()
        self.market_data_service = MarketDataService()

    async def run_backtest(self, backtest_id: str) -> dict[str, Any]:
        """Run a backtest and return results."""
        if not self.db:
            raise RuntimeError("Database session required")

        result = await self.db.execute(
            select(Backtest).where(Backtest.id == backtest_id)
        )
        backtest = result.scalar_one_or_none()

        if not backtest:
            raise ValueError(f"Backtest not found: {backtest_id}")

        result = await self.db.execute(
            select(Strategy).where(Strategy.id == backtest.strategy_id)
        )
        strategy = result.scalar_one_or_none()

        if not strategy:
            raise ValueError(f"Strategy not found: {backtest.strategy_id}")

        try:
            backtest.status = "running"
            await self.db.flush()

            results = await self._execute_backtest(backtest, strategy)

            backtest.status = "completed"
            backtest.completed_at = datetime.now(timezone.utc)
            backtest.final_capital = Decimal(str(results["final_capital"]))
            backtest.total_return = Decimal(str(results["total_return"]))
            backtest.total_trades = results["total_trades"]
            backtest.winning_trades = results["winning_trades"]
            backtest.losing_trades = results["losing_trades"]
            backtest.win_rate = Decimal(str(results["win_rate"]))
            backtest.max_drawdown = Decimal(str(results["max_drawdown"]))
            backtest.sharpe_ratio = Decimal(str(results["sharpe_ratio"]))
            backtest.profit_factor = Decimal(str(results["profit_factor"]))
            backtest.equity_curve = results["equity_curve"]

            await self.db.flush()

            logger.info(f"Backtest completed: {backtest_id}")
            return results

        except Exception as e:
            backtest.status = "failed"
            backtest.error_message = str(e)
            await self.db.flush()
            logger.error(f"Backtest failed: {backtest_id} - {e}")
            raise

    async def _execute_backtest(
        self,
        backtest: Backtest,
        strategy: Strategy,
    ) -> dict[str, Any]:
        """Execute the backtest logic."""
        trades: list[BacktestTrade] = []
        equity_curve: list[dict[str, Any]] = []
        capital = float(backtest.initial_capital)
        position: dict[str, Any] | None = None

        for symbol in backtest.symbols:
            df = await self._get_market_data(
                symbol=symbol,
                start_date=backtest.start_date,
                end_date=backtest.end_date,
                timeframe=backtest.timeframe,
            )

            if df.empty:
                logger.warning(f"No data for {symbol}")
                continue

            self.rule_engine.clear_cache()

            for i in range(20, len(df)):
                timestamp = df.index[i]
                close_price = float(df["close"].iloc[i])

                equity_curve.append({
                    "timestamp": timestamp.isoformat() if hasattr(timestamp, 'isoformat') else str(timestamp),
                    "equity": capital + (position["quantity"] * close_price if position else 0),
                })

                if position is None:
                    entry_signal = self.rule_engine.evaluate_rules(
                        strategy.rules,
                        df.iloc[:i+1],
                        -1,
                    )

                    if entry_signal.get("passed"):
                        quantity = capital * 0.95 / close_price
                        position = {
                            "symbol": symbol,
                            "entry_price": close_price,
                            "quantity": quantity,
                            "entry_time": timestamp,
                        }
                        capital -= quantity * close_price

                else:
                    exit_rules = strategy.exit_rules or []
                    exit_signal = {"signal": None}

                    if exit_rules:
                        exit_signal = self.rule_engine.evaluate_exit_rules(
                            exit_rules,
                            df.iloc[:i+1],
                            -1,
                        )

                    pnl_percent = (close_price - position["entry_price"]) / position["entry_price"]
                    should_exit = (
                        exit_signal.get("signal") == "exit"
                        or pnl_percent >= 0.05
                        or pnl_percent <= -0.02
                    )

                    if should_exit:
                        pnl = (close_price - position["entry_price"]) * position["quantity"]
                        capital += position["quantity"] * close_price

                        trade = BacktestTrade(
                            backtest_id=backtest.id,
                            symbol=symbol,
                            side="long",
                            entry_price=Decimal(str(position["entry_price"])),
                            exit_price=Decimal(str(close_price)),
                            quantity=Decimal(str(position["quantity"])),
                            entry_time=position["entry_time"],
                            exit_time=timestamp,
                            pnl=Decimal(str(pnl)),
                            pnl_percent=Decimal(str(pnl_percent * 100)),
                        )
                        trades.append(trade)
                        self.db.add(trade)

                        position = None

        if position:
            close_price = float(df["close"].iloc[-1])
            pnl = (close_price - position["entry_price"]) * position["quantity"]
            capital += position["quantity"] * close_price

        winning_trades = [t for t in trades if t.pnl and t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl and t.pnl < 0]

        total_profit = sum(float(t.pnl) for t in winning_trades)
        total_loss = abs(sum(float(t.pnl) for t in losing_trades))

        initial_capital = float(backtest.initial_capital)
        total_return = ((capital - initial_capital) / initial_capital) * 100

        equities = [e["equity"] for e in equity_curve]
        max_drawdown = self._calculate_max_drawdown(equities)
        sharpe_ratio = self._calculate_sharpe_ratio(equities)

        return {
            "final_capital": capital,
            "total_return": total_return,
            "total_trades": len(trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": (len(winning_trades) / len(trades) * 100) if trades else 0,
            "max_drawdown": max_drawdown,
            "sharpe_ratio": sharpe_ratio,
            "profit_factor": total_profit / total_loss if total_loss > 0 else 0,
            "equity_curve": equity_curve,
            "trades": trades,
        }

    async def _get_market_data(
        self,
        symbol: str,
        start_date: Any,
        end_date: Any,
        timeframe: str,
    ) -> pd.DataFrame:
        """Fetch historical market data."""
        try:
            data = await self.market_data_service.get_ohlcv(
                symbol=symbol,
                exchange="binance",
                timeframe=timeframe,
                start_date=datetime.combine(start_date, datetime.min.time()),
                end_date=datetime.combine(end_date, datetime.max.time()),
                limit=10000,
            )

            if not data:
                return pd.DataFrame()

            df = pd.DataFrame(data)
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df.set_index("timestamp", inplace=True)
            return df

        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return pd.DataFrame()

    def _calculate_max_drawdown(self, equities: list[float]) -> float:
        """Calculate maximum drawdown."""
        if not equities:
            return 0.0

        peak = equities[0]
        max_dd = 0.0

        for equity in equities:
            if equity > peak:
                peak = equity
            dd = (peak - equity) / peak * 100
            if dd > max_dd:
                max_dd = dd

        return max_dd

    def _calculate_sharpe_ratio(
        self,
        equities: list[float],
        risk_free_rate: float = 0.02,
    ) -> float:
        """Calculate Sharpe ratio."""
        if len(equities) < 2:
            return 0.0

        returns = []
        for i in range(1, len(equities)):
            if equities[i-1] > 0:
                ret = (equities[i] - equities[i-1]) / equities[i-1]
                returns.append(ret)

        if not returns:
            return 0.0

        import numpy as np
        mean_return = np.mean(returns)
        std_return = np.std(returns)

        if std_return == 0:
            return 0.0

        annualized_return = mean_return * 252
        annualized_std = std_return * np.sqrt(252)

        return (annualized_return - risk_free_rate) / annualized_std
