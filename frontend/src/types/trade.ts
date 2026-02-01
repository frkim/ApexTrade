export type TradeType = 'market' | 'limit' | 'stop' | 'stop_limit'
export type TradeSide = 'buy' | 'sell'
export type TradeStatus = 'pending' | 'filled' | 'partial' | 'cancelled' | 'rejected'

export interface Trade {
  id: string
  portfolioId: string
  strategyId?: string
  symbol: string
  side: TradeSide
  type: TradeType
  status: TradeStatus
  quantity: number
  filledQuantity: number
  price?: number
  filledPrice?: number
  stopPrice?: number
  commission: number
  pnl?: number
  createdAt: string
  filledAt?: string
}

export interface TradeHistory {
  trades: Trade[]
  totalPnl: number
  winCount: number
  lossCount: number
  winRate: number
}

export interface BacktestResult {
  id: string
  strategyId: string
  startDate: string
  endDate: string
  initialCapital: number
  finalCapital: number
  totalReturn: number
  totalReturnPercent: number
  maxDrawdown: number
  maxDrawdownPercent: number
  sharpeRatio: number
  sortinoRatio: number
  winRate: number
  profitFactor: number
  totalTrades: number
  winningTrades: number
  losingTrades: number
  averageWin: number
  averageLoss: number
  equityCurve: EquityPoint[]
  trades: Trade[]
  createdAt: string
}

export interface EquityPoint {
  date: string
  equity: number
  drawdown: number
}
