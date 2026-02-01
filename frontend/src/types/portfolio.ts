export interface Position {
  id: string
  portfolioId: string
  symbol: string
  quantity: number
  averagePrice: number
  currentPrice: number
  marketValue: number
  unrealizedPnl: number
  unrealizedPnlPercent: number
  side: 'long' | 'short'
  openedAt: string
}

export interface Portfolio {
  id: string
  name: string
  description?: string
  totalValue: number
  cashBalance: number
  investedValue: number
  unrealizedPnl: number
  realizedPnl: number
  dayChange: number
  dayChangePercent: number
  positions: Position[]
  createdAt: string
  updatedAt: string
}

export interface PortfolioSummary {
  id: string
  name: string
  totalValue: number
  dayChange: number
  dayChangePercent: number
  positionCount: number
}

export interface Allocation {
  symbol: string
  name: string
  value: number
  percentage: number
  color: string
}
