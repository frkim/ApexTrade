'use client'

import { useParams } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, Play, Pause, Trash2, BarChart2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { StrategyForm } from '@/components/forms/strategy-form'
import { EquityCurve } from '@/components/charts/equity-curve'
import { formatPercent, formatDate } from '@/lib/utils'
import { Strategy, StrategyStatus } from '@/types/strategy'

const statusConfig: Record<StrategyStatus, { label: string; variant: 'default' | 'success' | 'warning' | 'destructive' | 'secondary' }> = {
  draft: { label: 'Draft', variant: 'secondary' },
  active: { label: 'Active', variant: 'success' },
  paused: { label: 'Paused', variant: 'warning' },
  stopped: { label: 'Stopped', variant: 'secondary' },
  error: { label: 'Error', variant: 'destructive' },
}

// Mock data
const mockStrategy: Strategy = {
  id: '1',
  name: 'BTC Momentum',
  description: 'RSI-based momentum strategy for Bitcoin',
  symbol: 'BTCUSDT',
  timeframe: '4h',
  status: 'active',
  rules: [
    {
      id: 'r1',
      name: 'Buy Signal',
      action: 'buy',
      conditions: [
        {
          id: 'c1',
          indicator: { type: 'rsi', period: 14 },
          operator: 'less_than',
          value: 30,
        },
      ],
      conditionLogic: 'and',
      positionSize: 10,
      positionSizeType: 'percent',
    },
  ],
  createdAt: '2024-01-15T00:00:00Z',
  updatedAt: '2024-03-01T00:00:00Z',
}

const mockPerformance = {
  totalReturn: 24.5,
  winRate: 72,
  totalTrades: 156,
  profitFactor: 2.15,
  sharpeRatio: 1.82,
  maxDrawdown: -8.4,
}

const mockEquityData = [
  { date: '2024-01-15', equity: 10000, drawdown: 0 },
  { date: '2024-01-22', equity: 10250, drawdown: 0 },
  { date: '2024-01-29', equity: 10520, drawdown: 0 },
  { date: '2024-02-05', equity: 10380, drawdown: -140 },
  { date: '2024-02-12', equity: 10850, drawdown: 0 },
  { date: '2024-02-19', equity: 11230, drawdown: 0 },
  { date: '2024-02-26', equity: 11580, drawdown: 0 },
  { date: '2024-03-04', equity: 12450, drawdown: 0 },
]

export default function StrategyDetailPage() {
  const params = useParams()
  const id = params.id as string
  const strategy = mockStrategy
  const status = statusConfig[strategy.status]

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/dashboard/strategies">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h1 className="text-3xl font-bold">{strategy.name}</h1>
            <Badge variant={status.variant}>{status.label}</Badge>
          </div>
          <p className="text-muted-foreground">
            {strategy.symbol} • {strategy.timeframe} • Created {formatDate(strategy.createdAt)}
          </p>
        </div>
        <div className="flex gap-2">
          {strategy.status === 'active' && (
            <Button variant="outline">
              <Pause className="mr-2 h-4 w-4" />
              Pause
            </Button>
          )}
          {(strategy.status === 'draft' || strategy.status === 'paused') && (
            <Button variant="outline">
              <Play className="mr-2 h-4 w-4" />
              Activate
            </Button>
          )}
          <Link href={`/dashboard/backtests?strategy=${strategy.id}`}>
            <Button variant="outline">
              <BarChart2 className="mr-2 h-4 w-4" />
              Backtest
            </Button>
          </Link>
          <Button variant="destructive">
            <Trash2 className="mr-2 h-4 w-4" />
            Delete
          </Button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Performance</CardTitle>
          </CardHeader>
          <CardContent>
            <EquityCurve data={mockEquityData} height={300} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Statistics</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Total Return</span>
              <span
                className={`font-semibold ${
                  mockPerformance.totalReturn >= 0 ? 'text-success' : 'text-destructive'
                }`}
              >
                {formatPercent(mockPerformance.totalReturn)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Win Rate</span>
              <span className="font-semibold">{mockPerformance.winRate}%</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Total Trades</span>
              <span className="font-semibold">{mockPerformance.totalTrades}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Profit Factor</span>
              <span className="font-semibold">{mockPerformance.profitFactor}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Sharpe Ratio</span>
              <span className="font-semibold">{mockPerformance.sharpeRatio}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Max Drawdown</span>
              <span className="font-semibold text-destructive">
                {formatPercent(mockPerformance.maxDrawdown)}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Strategy Configuration</CardTitle>
        </CardHeader>
        <CardContent>
          <StrategyForm strategy={strategy} />
        </CardContent>
      </Card>
    </div>
  )
}
