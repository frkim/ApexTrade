"""Strategy schemas."""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class IndicatorConfig(BaseModel):
    """Indicator configuration."""

    name: str
    params: dict[str, Any] = {}


class RuleCondition(BaseModel):
    """Single rule condition."""

    indicator: str
    operator: Literal["gt", "lt", "eq", "gte", "lte", "crosses_above", "crosses_below"]
    value: float | str
    timeframe: str | None = None


class RuleDefinition(BaseModel):
    """Trading rule definition."""

    name: str | None = None
    conditions: list[RuleCondition] = []
    logic: Literal["and", "or"] = "and"
    indicators: list[IndicatorConfig] = []


class StrategyBase(BaseModel):
    """Base strategy schema."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    symbols: list[str] = Field(default_factory=list)
    timeframe: str = "1h"


class StrategyCreate(StrategyBase):
    """Strategy creation schema."""

    rules: RuleDefinition | None = None
    entry_rules: list[dict[str, Any]] | None = None
    exit_rules: list[dict[str, Any]] | None = None


class StrategyUpdate(BaseModel):
    """Strategy update schema."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    rules: RuleDefinition | None = None
    entry_rules: list[dict[str, Any]] | None = None
    exit_rules: list[dict[str, Any]] | None = None
    symbols: list[str] | None = None
    timeframe: str | None = None
    is_active: bool | None = None


class StrategyResponse(StrategyBase):
    """Strategy response schema."""

    id: UUID
    rules: dict[str, Any]
    entry_rules: list[dict[str, Any]] | None = None
    exit_rules: list[dict[str, Any]] | None = None
    is_active: bool
    is_paper: bool
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
