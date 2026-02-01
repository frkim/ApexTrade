"""Unit tests for rule engine."""

import pandas as pd
import pytest
from datetime import datetime, timedelta

from app.services.rule_engine import RuleEngine


@pytest.fixture
def rule_engine() -> RuleEngine:
    """Create rule engine instance."""
    return RuleEngine()


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Create sample OHLCV DataFrame."""
    data = []
    base_time = datetime.now() - timedelta(days=100)
    price = 100.0

    for i in range(100):
        change = (i % 10 - 5) * 0.005
        price = price * (1 + change)

        data.append(
            {
                "timestamp": base_time + timedelta(hours=i),
                "open": price * 0.99,
                "high": price * 1.02,
                "low": price * 0.98,
                "close": price,
                "volume": 1000 + i * 10,
            }
        )

    df = pd.DataFrame(data)
    df.set_index("timestamp", inplace=True)
    return df


class TestRuleEngine:
    """Test cases for RuleEngine."""

    def test_evaluate_empty_rules(self, rule_engine: RuleEngine, sample_df: pd.DataFrame):
        """Test evaluation with empty rules."""
        result = rule_engine.evaluate_rules({}, sample_df)
        assert result["signal"] is None
        assert result["details"] == []

    def test_evaluate_simple_condition_gt(self, rule_engine: RuleEngine, sample_df: pd.DataFrame):
        """Test greater than condition."""
        rules = {
            "conditions": [
                {"indicator": "close", "operator": "gt", "value": 50},
            ],
            "logic": "and",
        }
        result = rule_engine.evaluate_rules(rules, sample_df)
        assert "passed" in result
        assert len(result["details"]) == 1

    def test_evaluate_simple_condition_lt(self, rule_engine: RuleEngine, sample_df: pd.DataFrame):
        """Test less than condition."""
        rules = {
            "conditions": [
                {"indicator": "close", "operator": "lt", "value": 200},
            ],
            "logic": "and",
        }
        result = rule_engine.evaluate_rules(rules, sample_df)
        assert result["passed"] is True

    def test_evaluate_rsi_condition(self, rule_engine: RuleEngine, sample_df: pd.DataFrame):
        """Test RSI indicator condition."""
        rules = {
            "conditions": [
                {"indicator": "rsi_14", "operator": "lt", "value": 70},
            ],
            "logic": "and",
        }
        result = rule_engine.evaluate_rules(rules, sample_df)
        assert "passed" in result
        assert len(result["details"]) == 1
        assert "indicator_value" in result["details"][0]

    def test_evaluate_sma_condition(self, rule_engine: RuleEngine, sample_df: pd.DataFrame):
        """Test SMA indicator condition."""
        rules = {
            "conditions": [
                {"indicator": "sma_20", "operator": "gt", "value": 0},
            ],
            "logic": "and",
        }
        result = rule_engine.evaluate_rules(rules, sample_df)
        assert "passed" in result

    def test_evaluate_ema_condition(self, rule_engine: RuleEngine, sample_df: pd.DataFrame):
        """Test EMA indicator condition."""
        rules = {
            "conditions": [
                {"indicator": "ema_20", "operator": "gt", "value": 0},
            ],
            "logic": "and",
        }
        result = rule_engine.evaluate_rules(rules, sample_df)
        assert "passed" in result

    def test_evaluate_macd_condition(self, rule_engine: RuleEngine, sample_df: pd.DataFrame):
        """Test MACD indicator condition."""
        rules = {
            "conditions": [
                {"indicator": "macd_line", "operator": "gt", "value": -100},
            ],
            "logic": "and",
        }
        result = rule_engine.evaluate_rules(rules, sample_df)
        assert "passed" in result

    def test_evaluate_bollinger_condition(self, rule_engine: RuleEngine, sample_df: pd.DataFrame):
        """Test Bollinger Bands indicator condition."""
        rules = {
            "conditions": [
                {"indicator": "bb_middle", "operator": "gt", "value": 0},
            ],
            "logic": "and",
        }
        result = rule_engine.evaluate_rules(rules, sample_df)
        assert "passed" in result

    def test_evaluate_and_logic(self, rule_engine: RuleEngine, sample_df: pd.DataFrame):
        """Test AND logic with multiple conditions."""
        rules = {
            "conditions": [
                {"indicator": "close", "operator": "gt", "value": 50},
                {"indicator": "close", "operator": "lt", "value": 200},
            ],
            "logic": "and",
        }
        result = rule_engine.evaluate_rules(rules, sample_df)
        assert "passed" in result

    def test_evaluate_or_logic(self, rule_engine: RuleEngine, sample_df: pd.DataFrame):
        """Test OR logic with multiple conditions."""
        rules = {
            "conditions": [
                {"indicator": "close", "operator": "gt", "value": 1000},
                {"indicator": "close", "operator": "lt", "value": 200},
            ],
            "logic": "or",
        }
        result = rule_engine.evaluate_rules(rules, sample_df)
        assert result["passed"] is True

    def test_evaluate_indicator_comparison(self, rule_engine: RuleEngine, sample_df: pd.DataFrame):
        """Test comparing two indicators."""
        rules = {
            "conditions": [
                {"indicator": "close", "operator": "gt", "value": "$sma_20"},
            ],
            "logic": "and",
        }
        result = rule_engine.evaluate_rules(rules, sample_df)
        assert "passed" in result

    def test_evaluate_unknown_indicator(self, rule_engine: RuleEngine, sample_df: pd.DataFrame):
        """Test handling of unknown indicator."""
        rules = {
            "conditions": [
                {"indicator": "unknown_indicator", "operator": "gt", "value": 50},
            ],
            "logic": "and",
        }
        result = rule_engine.evaluate_rules(rules, sample_df)
        assert result["passed"] is False
        assert "error" in result["details"][0]

    def test_clear_cache(self, rule_engine: RuleEngine, sample_df: pd.DataFrame):
        """Test cache clearing."""
        rules = {
            "conditions": [
                {"indicator": "sma_20", "operator": "gt", "value": 0},
            ],
            "logic": "and",
        }
        rule_engine.evaluate_rules(rules, sample_df)
        assert len(rule_engine._indicators_cache) > 0

        rule_engine.clear_cache()
        assert len(rule_engine._indicators_cache) == 0

    def test_evaluate_entry_rules(self, rule_engine: RuleEngine, sample_df: pd.DataFrame):
        """Test entry rules evaluation."""
        entry_rules = [
            {
                "conditions": [
                    {"indicator": "rsi_14", "operator": "lt", "value": 30},
                ],
                "logic": "and",
            },
        ]
        result = rule_engine.evaluate_entry_rules(entry_rules, sample_df)
        assert "signal" in result

    def test_evaluate_exit_rules(self, rule_engine: RuleEngine, sample_df: pd.DataFrame):
        """Test exit rules evaluation."""
        exit_rules = [
            {
                "conditions": [
                    {"indicator": "rsi_14", "operator": "gt", "value": 70},
                ],
                "logic": "and",
            },
        ]
        result = rule_engine.evaluate_exit_rules(exit_rules, sample_df)
        assert "signal" in result
