'use client'

import Link from 'next/link'
import { Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { StrategyCard } from '@/components/dashboard/strategy-card'
import { Skeleton } from '@/components/ui/skeleton'
import { Strategy } from '@/types/strategy'

// Mock data
const mockStrategies: Strategy[] = [
  {
    id: '1',
    name: 'BTC Momentum',
    description: 'RSI-based momentum strategy for Bitcoin',
    symbol: 'BTCUSDT',
    timeframe: '4h',
    status: 'active',
    rules: [],
    createdAt: '2024-01-15T00:00:00Z',
    updatedAt: '2024-03-01T00:00:00Z',
  },
  {
    id: '2',
    name: 'ETH Mean Reversion',
    description: 'Bollinger Bands mean reversion for Ethereum',
    symbol: 'ETHUSDT',
    timeframe: '1h',
    status: 'paused',
    rules: [],
    createdAt: '2024-02-01T00:00:00Z',
    updatedAt: '2024-03-01T00:00:00Z',
  },
  {
    id: '3',
    name: 'SOL Breakout',
    description: 'Breakout strategy with volume confirmation',
    symbol: 'SOLUSDT',
    timeframe: '15m',
    status: 'draft',
    rules: [],
    createdAt: '2024-03-01T00:00:00Z',
    updatedAt: '2024-03-01T00:00:00Z',
  },
]

const mockPerformance: Record<string, { totalReturn: number; winRate: number; totalTrades: number }> = {
  '1': { totalReturn: 24.5, winRate: 72, totalTrades: 156 },
  '2': { totalReturn: -3.2, winRate: 58, totalTrades: 89 },
  '3': { totalReturn: 0, winRate: 0, totalTrades: 0 },
}

export default function StrategiesPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Strategies</h1>
          <p className="text-muted-foreground">Manage your trading strategies</p>
        </div>
        <Link href="/dashboard/strategies/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            New Strategy
          </Button>
        </Link>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {mockStrategies.map((strategy) => (
          <StrategyCard
            key={strategy.id}
            strategy={strategy}
            performance={mockPerformance[strategy.id]}
          />
        ))}
      </div>

      {mockStrategies.length === 0 && (
        <div className="flex h-64 items-center justify-center rounded-lg border border-dashed">
          <div className="text-center">
            <p className="text-muted-foreground">No strategies yet</p>
            <Link href="/dashboard/strategies/new">
              <Button variant="link">Create your first strategy</Button>
            </Link>
          </div>
        </div>
      )}
    </div>
  )
}
