"""Rule engine for evaluating trading conditions."""

import logging
from decimal import Decimal
from typing import Any

import pandas as pd

from app.utils.indicators import (
    calculate_bollinger_bands,
    calculate_ema,
    calculate_macd,
    calculate_rsi,
    calculate_sma,
)

logger = logging.getLogger(__name__)


class RuleEngine:
    """Engine for evaluating trading rules against market data."""

    OPERATORS = {
        "gt": lambda a, b: a > b,
        "lt": lambda a, b: a < b,
        "eq": lambda a, b: a == b,
        "gte": lambda a, b: a >= b,
        "lte": lambda a, b: a <= b,
        "crosses_above": lambda current, prev, threshold: prev <= threshold < current,
        "crosses_below": lambda current, prev, threshold: prev >= threshold > current,
    }

    INDICATOR_FUNCTIONS = {
        "sma": calculate_sma,
        "ema": calculate_ema,
        "rsi": calculate_rsi,
        "macd": calculate_macd,
        "bollinger_bands": calculate_bollinger_bands,
    }

    def __init__(self) -> None:
        self._indicators_cache: dict[str, pd.Series] = {}

    def evaluate_rules(
        self,
        rules: dict[str, Any],
        df: pd.DataFrame,
        index: int = -1,
    ) -> dict[str, Any]:
        """Evaluate trading rules against market data.

        Args:
            rules: Rule definition containing conditions and logic
            df: DataFrame with OHLCV data
            index: Index to evaluate at (-1 for latest)

        Returns:
            Dictionary with signal type and details
        """
        if not rules or "conditions" not in rules:
            return {"signal": None, "details": []}

        conditions = rules.get("conditions", [])
        logic = rules.get("logic", "and")

        results = []
        for condition in conditions:
            result = self._evaluate_condition(condition, df, index)
            results.append(result)

        if logic == "and":
            signal = all(r["passed"] for r in results)
        else:  # or
            signal = any(r["passed"] for r in results)

        return {
            "signal": "entry" if signal else None,
            "passed": signal,
            "details": results,
        }

    def _evaluate_condition(
        self,
        condition: dict[str, Any],
        df: pd.DataFrame,
        index: int,
    ) -> dict[str, Any]:
        """Evaluate a single condition."""
        indicator_name = condition.get("indicator", "").lower()
        operator = condition.get("operator", "")
        value = condition.get("value")

        try:
            indicator_value = self._get_indicator_value(indicator_name, df, index)

            if operator in ("crosses_above", "crosses_below"):
                prev_value = self._get_indicator_value(indicator_name, df, index - 1)
                threshold = float(value) if isinstance(value, (int, float, str)) else value
                passed = self.OPERATORS[operator](indicator_value, prev_value, threshold)
            else:
                if isinstance(value, str) and value.startswith("$"):
                    compare_value = self._get_indicator_value(value[1:], df, index)
                else:
                    compare_value = float(value)
                passed = self.OPERATORS[operator](indicator_value, compare_value)

            return {
                "condition": condition,
                "indicator_value": indicator_value,
                "passed": passed,
            }
        except Exception as e:
            logger.error(f"Error evaluating condition: {e}")
            return {
                "condition": condition,
                "error": str(e),
                "passed": False,
            }

    def _get_indicator_value(
        self,
        indicator_name: str,
        df: pd.DataFrame,
        index: int,
    ) -> float:
        """Get indicator value at specified index."""
        parts = indicator_name.split("_")
        base_indicator = parts[0]

        if base_indicator == "close":
            return float(df["close"].iloc[index])
        elif base_indicator == "open":
            return float(df["open"].iloc[index])
        elif base_indicator == "high":
            return float(df["high"].iloc[index])
        elif base_indicator == "low":
            return float(df["low"].iloc[index])
        elif base_indicator == "volume":
            return float(df["volume"].iloc[index])
        elif base_indicator == "sma":
            period = int(parts[1]) if len(parts) > 1 else 20
            cache_key = f"sma_{period}"
            if cache_key not in self._indicators_cache:
                self._indicators_cache[cache_key] = calculate_sma(df["close"], period)
            return float(self._indicators_cache[cache_key].iloc[index])
        elif base_indicator == "ema":
            period = int(parts[1]) if len(parts) > 1 else 20
            cache_key = f"ema_{period}"
            if cache_key not in self._indicators_cache:
                self._indicators_cache[cache_key] = calculate_ema(df["close"], period)
            return float(self._indicators_cache[cache_key].iloc[index])
        elif base_indicator == "rsi":
            period = int(parts[1]) if len(parts) > 1 else 14
            cache_key = f"rsi_{period}"
            if cache_key not in self._indicators_cache:
                self._indicators_cache[cache_key] = calculate_rsi(df["close"], period)
            return float(self._indicators_cache[cache_key].iloc[index])
        elif base_indicator == "macd":
            component = parts[1] if len(parts) > 1 else "line"
            cache_key = "macd"
            if cache_key not in self._indicators_cache:
                result = calculate_macd(df["close"])
                self._indicators_cache["macd_line"] = result["macd"]
                self._indicators_cache["macd_signal"] = result["signal"]
                self._indicators_cache["macd_histogram"] = result["histogram"]
            return float(self._indicators_cache[f"macd_{component}"].iloc[index])
        elif base_indicator == "bb":
            component = parts[1] if len(parts) > 1 else "middle"
            cache_key = "bb"
            if cache_key not in self._indicators_cache:
                result = calculate_bollinger_bands(df["close"])
                self._indicators_cache["bb_upper"] = result["upper"]
                self._indicators_cache["bb_middle"] = result["middle"]
                self._indicators_cache["bb_lower"] = result["lower"]
            return float(self._indicators_cache[f"bb_{component}"].iloc[index])
        else:
            raise ValueError(f"Unknown indicator: {indicator_name}")

    def clear_cache(self) -> None:
        """Clear indicator cache."""
        self._indicators_cache.clear()

    def evaluate_entry_rules(
        self,
        entry_rules: list[dict[str, Any]],
        df: pd.DataFrame,
        index: int = -1,
    ) -> dict[str, Any]:
        """Evaluate entry rules."""
        for rule in entry_rules:
            result = self.evaluate_rules(rule, df, index)
            if result.get("passed"):
                return {
                    "signal": "entry",
                    "rule": rule,
                    "details": result["details"],
                }
        return {"signal": None}

    def evaluate_exit_rules(
        self,
        exit_rules: list[dict[str, Any]],
        df: pd.DataFrame,
        index: int = -1,
    ) -> dict[str, Any]:
        """Evaluate exit rules."""
        for rule in exit_rules:
            result = self.evaluate_rules(rule, df, index)
            if result.get("passed"):
                return {
                    "signal": "exit",
                    "rule": rule,
                    "details": result["details"],
                }
        return {"signal": None}
