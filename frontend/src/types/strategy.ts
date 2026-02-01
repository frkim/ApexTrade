export type StrategyStatus = 'draft' | 'active' | 'paused' | 'stopped' | 'error'

export type ConditionOperator =
  | 'greater_than'
  | 'less_than'
  | 'equals'
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
  type: IndicatorType
  period?: number
  source?: 'open' | 'high' | 'low' | 'close'
  params?: Record<string, number | string>
}

export interface RuleCondition {
  id: string
  indicator: IndicatorConfig
  operator: ConditionOperator
  value: number | IndicatorConfig
}

export interface Rule {
  id: string
  name: string
  action: 'buy' | 'sell'
  conditions: RuleCondition[]
  conditionLogic: 'and' | 'or'
  positionSize: number
  positionSizeType: 'percent' | 'fixed'
}

export interface Strategy {
  id: string
  name: string
  description?: string
  symbol: string
  timeframe: string
  status: StrategyStatus
  rules: Rule[]
  createdAt: string
  updatedAt: string
  portfolioId?: string
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
