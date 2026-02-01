'use client'

import { useParams } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, ArrowUpRight, ArrowDownRight, Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { AllocationPieChart } from '@/components/charts/pie-chart'
import { EquityCurve } from '@/components/charts/equity-curve'
import { MetricsCard } from '@/components/dashboard/metrics-card'
import { formatCurrency, formatPercent } from '@/lib/utils'
import { Portfolio, Position, Allocation } from '@/types/portfolio'

// Mock data
const mockPortfolio: Portfolio = {
  id: '1',
  name: 'Main Portfolio',
  description: 'My primary trading portfolio',
  totalValue: 125420.50,
  cashBalance: 15420.50,
  investedValue: 110000.00,
  unrealizedPnl: 8540.25,
  realizedPnl: 12350.00,
  dayChange: 1250.00,
  dayChangePercent: 1.01,
  positions: [
    {
      id: 'p1',
      portfolioId: '1',
      symbol: 'BTCUSDT',
      quantity: 1.5,
      averagePrice: 42000,
      currentPrice: 44500,
      marketValue: 66750,
      unrealizedPnl: 3750,
      unrealizedPnlPercent: 5.95,
      side: 'long',
      openedAt: '2024-02-15T00:00:00Z',
    },
    {
      id: 'p2',
      portfolioId: '1',
      symbol: 'ETHUSDT',
      quantity: 10,
      averagePrice: 2200,
      currentPrice: 2350,
      marketValue: 23500,
      unrealizedPnl: 1500,
      unrealizedPnlPercent: 6.82,
      side: 'long',
      openedAt: '2024-02-20T00:00:00Z',
    },
    {
      id: 'p3',
      portfolioId: '1',
      symbol: 'SOLUSDT',
      quantity: 100,
      averagePrice: 120,
      currentPrice: 115,
      marketValue: 11500,
      unrealizedPnl: -500,
      unrealizedPnlPercent: -4.17,
      side: 'long',
      openedAt: '2024-03-01T00:00:00Z',
    },
    {
      id: 'p4',
      portfolioId: '1',
      symbol: 'AVAXUSDT',
      quantity: 50,
      averagePrice: 85,
      currentPrice: 92,
      marketValue: 4600,
      unrealizedPnl: 350,
      unrealizedPnlPercent: 8.24,
      side: 'long',
      openedAt: '2024-03-02T00:00:00Z',
    },
    {
      id: 'p5',
      portfolioId: '1',
      symbol: 'DOTUSDT',
      quantity: 200,
      averagePrice: 18,
      currentPrice: 18.25,
      marketValue: 3650,
      unrealizedPnl: 50,
      unrealizedPnlPercent: 1.39,
      side: 'long',
      openedAt: '2024-03-03T00:00:00Z',
    },
  ],
  createdAt: '2024-01-01T00:00:00Z',
  updatedAt: '2024-03-04T00:00:00Z',
}

const mockAllocation: Allocation[] = [
  { symbol: 'BTCUSDT', name: 'Bitcoin', value: 66750, percentage: 53.2, color: 'hsl(38 92% 50%)' },
  { symbol: 'ETHUSDT', name: 'Ethereum', value: 23500, percentage: 18.7, color: 'hsl(217.2 91.2% 59.8%)' },
  { symbol: 'Cash', name: 'Cash', value: 15420.50, percentage: 12.3, color: 'hsl(142 70% 45%)' },
  { symbol: 'SOLUSDT', name: 'Solana', value: 11500, percentage: 9.2, color: 'hsl(280 65% 60%)' },
  { symbol: 'Other', name: 'Other', value: 8250, percentage: 6.6, color: 'hsl(340 75% 55%)' },
]

const mockEquityData = [
  { date: '2024-01-01', equity: 100000, drawdown: 0 },
  { date: '2024-01-15', equity: 105000, drawdown: 0 },
  { date: '2024-02-01', equity: 108500, drawdown: 0 },
  { date: '2024-02-15', equity: 112000, drawdown: 0 },
  { date: '2024-03-01', equity: 118500, drawdown: 0 },
  { date: '2024-03-04', equity: 125420, drawdown: 0 },
]

export default function PortfolioDetailPage() {
  const params = useParams()
  const id = params.id as string
  const portfolio = mockPortfolio

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/dashboard/portfolios">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div className="flex-1">
          <h1 className="text-3xl font-bold">{portfolio.name}</h1>
          <p className="text-muted-foreground">{portfolio.description}</p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Add Position
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <MetricsCard
          title="Total Value"
          value={formatCurrency(portfolio.totalValue)}
          change={portfolio.dayChangePercent}
        />
        <MetricsCard
          title="Cash Balance"
          value={formatCurrency(portfolio.cashBalance)}
        />
        <MetricsCard
          title="Unrealized P&L"
          value={formatCurrency(portfolio.unrealizedPnl)}
          className={portfolio.unrealizedPnl >= 0 ? 'border-success/50' : 'border-destructive/50'}
        />
        <MetricsCard
          title="Realized P&L"
          value={formatCurrency(portfolio.realizedPnl)}
          className={portfolio.realizedPnl >= 0 ? 'border-success/50' : 'border-destructive/50'}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Portfolio Performance</CardTitle>
          </CardHeader>
          <CardContent>
            <EquityCurve data={mockEquityData} height={300} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Allocation</CardTitle>
          </CardHeader>
          <CardContent>
            <AllocationPieChart data={mockAllocation} height={280} showLegend={false} />
            <div className="mt-4 space-y-2">
              {mockAllocation.map((item) => (
                <div key={item.symbol} className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <div
                      className="h-3 w-3 rounded-full"
                      style={{ backgroundColor: item.color }}
                    />
                    <span>{item.name}</span>
                  </div>
                  <span className="text-muted-foreground">{item.percentage.toFixed(1)}%</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Positions</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Symbol</TableHead>
                <TableHead>Side</TableHead>
                <TableHead className="text-right">Quantity</TableHead>
                <TableHead className="text-right">Avg. Price</TableHead>
                <TableHead className="text-right">Current Price</TableHead>
                <TableHead className="text-right">Market Value</TableHead>
                <TableHead className="text-right">P&L</TableHead>
                <TableHead className="text-right">P&L %</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {portfolio.positions.map((position) => (
                <TableRow key={position.id}>
                  <TableCell className="font-medium">{position.symbol}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1">
                      {position.side === 'long' ? (
                        <ArrowUpRight className="h-4 w-4 text-success" />
                      ) : (
                        <ArrowDownRight className="h-4 w-4 text-destructive" />
                      )}
                      <span className="capitalize">{position.side}</span>
                    </div>
                  </TableCell>
                  <TableCell className="text-right">{position.quantity}</TableCell>
                  <TableCell className="text-right">
                    {formatCurrency(position.averagePrice)}
                  </TableCell>
                  <TableCell className="text-right">
                    {formatCurrency(position.currentPrice)}
                  </TableCell>
                  <TableCell className="text-right">
                    {formatCurrency(position.marketValue)}
                  </TableCell>
                  <TableCell className="text-right">
                    <span
                      className={position.unrealizedPnl >= 0 ? 'text-success' : 'text-destructive'}
                    >
                      {formatCurrency(position.unrealizedPnl)}
                    </span>
                  </TableCell>
                  <TableCell className="text-right">
                    <span
                      className={position.unrealizedPnlPercent >= 0 ? 'text-success' : 'text-destructive'}
                    >
                      {formatPercent(position.unrealizedPnlPercent)}
                    </span>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
