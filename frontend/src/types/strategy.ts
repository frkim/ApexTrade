export type StrategyStatus = 'draft' | 'active' | 'paused' | 'stopped' | 'error'

export type ConditionOperator =
  | 'gt'
  | 'lt'
  | 'eq'
  | 'gte'
  | 'lte'
  | 'crosses_above'
  | 'crosses_below'

export type IndicatorType =
  | 'sma'
  | 'ema'
  | 'rsi'
  | 'macd'
  | 'bollinger_bands'
  | 'atr'
  | 'volume'
  | 'price'

export interface IndicatorConfig {
  name: string
  params?: Record<string, number | string>
}

export interface RuleCondition {
  indicator: string
  operator: ConditionOperator
  value: number | string
  timeframe?: string
}

export interface RuleDefinition {
  name?: string
  conditions: RuleCondition[]
  logic: 'and' | 'or'
  indicators?: IndicatorConfig[]
}

// Strategy type aligned with backend StrategyResponse schema
export interface Strategy {
  id: string
  name: string
  description?: string
  symbols: string[]
  timeframe: string
  rules: Record<string, unknown>
  entry_rules?: Record<string, unknown>[]
  exit_rules?: Record<string, unknown>[]
  is_active: boolean
  is_paper: boolean
  user_id: string
  created_at: string
  updated_at: string
}

export interface StrategyPerformance {
  strategyId: string
  totalTrades: number
  winRate: number
  profitFactor: number
  sharpeRatio: number
  maxDrawdown: number
  totalReturn: number
}
