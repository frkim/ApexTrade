'use client'

import { DollarSign, TrendingUp, Activity, Briefcase } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { MetricsCard } from '@/components/dashboard/metrics-card'
import { RecentTrades } from '@/components/dashboard/recent-trades'
import { EquityCurve } from '@/components/charts/equity-curve'
import { formatCurrency } from '@/lib/utils'

// Mock data for demonstration
const mockMetrics = {
  totalValue: 125420.50,
  totalValueChange: 3.24,
  todayPnl: 1250.00,
  todayPnlChange: 15.2,
  activeStrategies: 4,
  activeStrategiesChange: 0,
  winRate: 68.5,
  winRateChange: 2.1,
}

const mockEquityData = [
  { date: '2024-01-01', equity: 100000, drawdown: 0 },
  { date: '2024-01-08', equity: 102500, drawdown: 0 },
  { date: '2024-01-15', equity: 105200, drawdown: 0 },
  { date: '2024-01-22', equity: 103800, drawdown: -1400 },
  { date: '2024-01-29', equity: 108500, drawdown: 0 },
  { date: '2024-02-05', equity: 112300, drawdown: 0 },
  { date: '2024-02-12', equity: 115800, drawdown: 0 },
  { date: '2024-02-19', equity: 118200, drawdown: 0 },
  { date: '2024-02-26', equity: 121500, drawdown: 0 },
  { date: '2024-03-04', equity: 125420, drawdown: 0 },
]

const mockTrades = [
  {
    id: '1',
    portfolioId: 'p1',
    strategyId: 's1',
    symbol: 'BTCUSDT',
    side: 'buy' as const,
    type: 'market' as const,
    status: 'filled' as const,
    quantity: 0.5,
    filledQuantity: 0.5,
    filledPrice: 42500,
    commission: 21.25,
    pnl: 850,
    createdAt: '2024-03-04T10:30:00Z',
    filledAt: '2024-03-04T10:30:01Z',
  },
  {
    id: '2',
    portfolioId: 'p1',
    strategyId: 's1',
    symbol: 'ETHUSDT',
    side: 'sell' as const,
    type: 'limit' as const,
    status: 'filled' as const,
    quantity: 2,
    filledQuantity: 2,
    price: 2250,
    filledPrice: 2252,
    commission: 4.50,
    pnl: 124,
    createdAt: '2024-03-04T09:15:00Z',
    filledAt: '2024-03-04T09:20:00Z',
  },
  {
    id: '3',
    portfolioId: 'p1',
    symbol: 'SOLUSDT',
    side: 'buy' as const,
    type: 'market' as const,
    status: 'pending' as const,
    quantity: 10,
    filledQuantity: 0,
    commission: 0,
    createdAt: '2024-03-04T11:00:00Z',
  },
]

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">Welcome back! Here&apos;s your trading overview.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <MetricsCard
          title="Total Portfolio Value"
          value={formatCurrency(mockMetrics.totalValue)}
          change={mockMetrics.totalValueChange}
          icon={DollarSign}
        />
        <MetricsCard
          title="Today's P&L"
          value={formatCurrency(mockMetrics.todayPnl)}
          change={mockMetrics.todayPnlChange}
          icon={TrendingUp}
        />
        <MetricsCard
          title="Active Strategies"
          value={mockMetrics.activeStrategies}
          change={mockMetrics.activeStrategiesChange}
          icon={Activity}
        />
        <MetricsCard
          title="Win Rate"
          value={`${mockMetrics.winRate}%`}
          change={mockMetrics.winRateChange}
          icon={Briefcase}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Portfolio Performance</CardTitle>
          </CardHeader>
          <CardContent>
            <EquityCurve data={mockEquityData} height={350} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Quick Stats</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Total Trades</span>
              <span className="font-semibold">247</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Winning Trades</span>
              <span className="font-semibold text-success">169</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Losing Trades</span>
              <span className="font-semibold text-destructive">78</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Avg. Win</span>
              <span className="font-semibold text-success">$324.50</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Avg. Loss</span>
              <span className="font-semibold text-destructive">$142.30</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Profit Factor</span>
              <span className="font-semibold">2.28</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Sharpe Ratio</span>
              <span className="font-semibold">1.85</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Max Drawdown</span>
              <span className="font-semibold text-destructive">-8.4%</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Trades</CardTitle>
        </CardHeader>
        <CardContent>
          <RecentTrades trades={mockTrades} />
        </CardContent>
      </Card>
    </div>
  )
}
