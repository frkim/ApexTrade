'use client'

import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { formatCurrency, formatPercent, formatDateTime } from '@/lib/utils'
import { BacktestResult } from '@/types/trade'

// Mock data
const mockBacktests: BacktestResult[] = [
  {
    id: '1',
    strategyId: '1',
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
    equityCurve: [],
    trades: [],
    createdAt: '2024-03-01T10:30:00Z',
  },
  {
    id: '2',
    strategyId: '2',
    startDate: '2023-06-01',
    endDate: '2024-01-01',
    initialCapital: 10000,
    finalCapital: 9680,
    totalReturn: -320,
    totalReturnPercent: -3.2,
    maxDrawdown: 1850,
    maxDrawdownPercent: 15.2,
    sharpeRatio: -0.25,
    sortinoRatio: -0.18,
    winRate: 48.5,
    profitFactor: 0.92,
    totalTrades: 89,
    winningTrades: 43,
    losingTrades: 46,
    averageWin: 186.2,
    averageLoss: 195.8,
    equityCurve: [],
    trades: [],
    createdAt: '2024-02-28T14:15:00Z',
  },
]

const strategyNames: Record<string, string> = {
  '1': 'BTC Momentum',
  '2': 'ETH Mean Reversion',
}

export default function BacktestsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Backtests</h1>
        <p className="text-muted-foreground">View and analyze your backtest results</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Backtests</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Strategy</TableHead>
                <TableHead>Period</TableHead>
                <TableHead className="text-right">Return</TableHead>
                <TableHead className="text-right">Win Rate</TableHead>
                <TableHead className="text-right">Sharpe</TableHead>
                <TableHead className="text-right">Max DD</TableHead>
                <TableHead className="text-right">Trades</TableHead>
                <TableHead>Created</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {mockBacktests.map((backtest) => (
                <TableRow key={backtest.id}>
                  <TableCell>
                    <Link
                      href={`/dashboard/backtests/${backtest.id}`}
                      className="font-medium hover:text-primary"
                    >
                      {strategyNames[backtest.strategyId] || backtest.strategyId}
                    </Link>
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {backtest.startDate} to {backtest.endDate}
                  </TableCell>
                  <TableCell className="text-right">
                    <span
                      className={
                        backtest.totalReturnPercent >= 0 ? 'text-success' : 'text-destructive'
                      }
                    >
                      {formatPercent(backtest.totalReturnPercent)}
                    </span>
                  </TableCell>
                  <TableCell className="text-right">{backtest.winRate.toFixed(1)}%</TableCell>
                  <TableCell className="text-right">{backtest.sharpeRatio.toFixed(2)}</TableCell>
                  <TableCell className="text-right text-destructive">
                    {formatPercent(-backtest.maxDrawdownPercent)}
                  </TableCell>
                  <TableCell className="text-right">{backtest.totalTrades}</TableCell>
                  <TableCell className="text-muted-foreground">
                    {formatDateTime(backtest.createdAt)}
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
