'use client'

import { useParams } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, Download } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { EquityCurve } from '@/components/charts/equity-curve'
import { RecentTrades } from '@/components/dashboard/recent-trades'
import { MetricsCard } from '@/components/dashboard/metrics-card'
import { formatCurrency, formatPercent, formatDate } from '@/lib/utils'

// Mock data
const mockBacktest = {
  id: '1',
  strategyId: '1',
  strategyName: 'BTC Momentum',
  startDate: '2023-01-01',
  endDate: '2024-01-01',
  initialCapital: 10000,
  finalCapital: 15420,
  totalReturn: 5420,
  totalReturnPercent: 54.2,
  maxDrawdown: 1250,
  maxDrawdownPercent: 8.4,
  sharpeRatio: 1.85,
  sortinoRatio: 2.12,
  winRate: 68.5,
  profitFactor: 2.15,
  totalTrades: 156,
  winningTrades: 107,
  losingTrades: 49,
  averageWin: 324.5,
  averageLoss: 142.3,
  createdAt: '2024-03-01T10:30:00Z',
}

const mockEquityData = [
  { date: '2023-01-01', equity: 10000, drawdown: 0 },
  { date: '2023-02-01', equity: 10850, drawdown: 0 },
  { date: '2023-03-01', equity: 11200, drawdown: 0 },
  { date: '2023-04-01', equity: 10650, drawdown: -550 },
  { date: '2023-05-01', equity: 11800, drawdown: 0 },
  { date: '2023-06-01', equity: 12450, drawdown: 0 },
  { date: '2023-07-01', equity: 11950, drawdown: -500 },
  { date: '2023-08-01', equity: 13200, drawdown: 0 },
  { date: '2023-09-01', equity: 13850, drawdown: 0 },
  { date: '2023-10-01', equity: 12600, drawdown: -1250 },
  { date: '2023-11-01', equity: 14200, drawdown: 0 },
  { date: '2023-12-01', equity: 15420, drawdown: 0 },
]

const mockTrades = [
  {
    id: '1',
    portfolioId: 'p1',
    strategyId: '1',
    symbol: 'BTCUSDT',
    side: 'buy' as const,
    type: 'market' as const,
    status: 'filled' as const,
    quantity: 0.5,
    filledQuantity: 0.5,
    filledPrice: 42500,
    commission: 21.25,
    pnl: 850,
    createdAt: '2023-12-15T10:30:00Z',
    filledAt: '2023-12-15T10:30:01Z',
  },
  {
    id: '2',
    portfolioId: 'p1',
    strategyId: '1',
    symbol: 'BTCUSDT',
    side: 'sell' as const,
    type: 'market' as const,
    status: 'filled' as const,
    quantity: 0.5,
    filledQuantity: 0.5,
    filledPrice: 44200,
    commission: 22.10,
    pnl: 850,
    createdAt: '2023-12-20T14:15:00Z',
    filledAt: '2023-12-20T14:15:01Z',
  },
]

export default function BacktestDetailPage() {
  const params = useParams()
  const id = params.id as string

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/dashboard/backtests">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div className="flex-1">
          <h1 className="text-3xl font-bold">{mockBacktest.strategyName} Backtest</h1>
          <p className="text-muted-foreground">
            {mockBacktest.startDate} to {mockBacktest.endDate} • Created{' '}
            {formatDate(mockBacktest.createdAt)}
          </p>
        </div>
        <Button variant="outline">
          <Download className="mr-2 h-4 w-4" />
          Export Report
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <MetricsCard
          title="Total Return"
          value={formatPercent(mockBacktest.totalReturnPercent)}
          className={mockBacktest.totalReturnPercent >= 0 ? 'border-success/50' : 'border-destructive/50'}
        />
        <MetricsCard
          title="Final Capital"
          value={formatCurrency(mockBacktest.finalCapital)}
        />
        <MetricsCard
          title="Win Rate"
          value={`${mockBacktest.winRate}%`}
        />
        <MetricsCard
          title="Max Drawdown"
          value={formatPercent(-mockBacktest.maxDrawdownPercent)}
          className="border-destructive/50"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Equity Curve</CardTitle>
          </CardHeader>
          <CardContent>
            <EquityCurve data={mockEquityData} height={350} showDrawdown />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Performance Metrics</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Initial Capital</span>
              <span className="font-semibold">{formatCurrency(mockBacktest.initialCapital)}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Net Profit</span>
              <span className="font-semibold text-success">
                {formatCurrency(mockBacktest.totalReturn)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Total Trades</span>
              <span className="font-semibold">{mockBacktest.totalTrades}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Winning Trades</span>
              <span className="font-semibold text-success">{mockBacktest.winningTrades}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Losing Trades</span>
              <span className="font-semibold text-destructive">{mockBacktest.losingTrades}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Avg. Win</span>
              <span className="font-semibold text-success">
                {formatCurrency(mockBacktest.averageWin)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Avg. Loss</span>
              <span className="font-semibold text-destructive">
                {formatCurrency(mockBacktest.averageLoss)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Profit Factor</span>
              <span className="font-semibold">{mockBacktest.profitFactor}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Sharpe Ratio</span>
              <span className="font-semibold">{mockBacktest.sharpeRatio}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Sortino Ratio</span>
              <span className="font-semibold">{mockBacktest.sortinoRatio}</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Trade History</CardTitle>
        </CardHeader>
        <CardContent>
          <RecentTrades trades={mockTrades} />
        </CardContent>
      </Card>
    </div>
  )
}
