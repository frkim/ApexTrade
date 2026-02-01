import Link from 'next/link'
import { Play, Pause, AlertCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { formatPercent } from '@/lib/utils'
import { Strategy } from '@/types/strategy'

interface StrategyCardProps {
  strategy: Strategy
  performance?: {
    totalReturn: number
    winRate: number
    totalTrades: number
  }
  onActivate?: (id: string) => void
  onPause?: (id: string) => void
}

// Get display status from is_active flag
function getStatusDisplay(isActive: boolean): { label: string; variant: 'default' | 'success' | 'warning' | 'destructive' | 'secondary' } {
  return isActive
    ? { label: 'Active', variant: 'success' }
    : { label: 'Inactive', variant: 'secondary' }
}

export function StrategyCard({ strategy, performance, onActivate, onPause }: StrategyCardProps) {
  const status = getStatusDisplay(strategy.is_active)
  const symbolDisplay = strategy.symbols.join(', ')

  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between">
        <div>
          <Link href={`/dashboard/strategies/${strategy.id}`}>
            <CardTitle className="hover:text-primary">{strategy.name}</CardTitle>
          </Link>
          <CardDescription className="mt-1">
            {symbolDisplay} • {strategy.timeframe}
          </CardDescription>
        </div>
        <Badge variant={status.variant}>{status.label}</Badge>
      </CardHeader>
      <CardContent>
        {performance && (
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-sm text-muted-foreground">Return</p>
              <p
                className={`text-lg font-semibold ${
                  performance.totalReturn >= 0 ? 'text-success' : 'text-destructive'
                }`}
              >
                {formatPercent(performance.totalReturn)}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Win Rate</p>
              <p className="text-lg font-semibold">{formatPercent(performance.winRate, 1)}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Trades</p>
              <p className="text-lg font-semibold">{performance.totalTrades}</p>
            </div>
          </div>
        )}

        <div className="mt-4 flex gap-2">
          {strategy.is_active && onPause && (
            <Button variant="outline" size="sm" onClick={() => onPause(strategy.id)}>
              <Pause className="mr-1 h-4 w-4" />
              Pause
            </Button>
          )}
          {!strategy.is_active && onActivate && (
            <Button variant="outline" size="sm" onClick={() => onActivate(strategy.id)}>
              <Play className="mr-1 h-4 w-4" />
              Activate
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
