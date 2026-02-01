import { LucideIcon, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { cn } from '@/lib/utils'

interface MetricsCardProps {
  title: string
  value: string | number
  change?: number
  changeLabel?: string
  icon?: LucideIcon
  className?: string
}

export function MetricsCard({
  title,
  value,
  change,
  changeLabel = 'vs last period',
  icon: Icon,
  className,
}: MetricsCardProps) {
  const getTrendIcon = () => {
    if (change === undefined || change === 0) {
      return <Minus className="h-4 w-4 text-muted-foreground" />
    }
    if (change > 0) {
      return <TrendingUp className="h-4 w-4 text-success" />
    }
    return <TrendingDown className="h-4 w-4 text-destructive" />
  }

  const getChangeColor = () => {
    if (change === undefined || change === 0) return 'text-muted-foreground'
    return change > 0 ? 'text-success' : 'text-destructive'
  }

  return (
    <Card className={className}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {Icon && <Icon className="h-4 w-4 text-muted-foreground" />}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {change !== undefined && (
          <div className="flex items-center gap-1 text-xs">
            {getTrendIcon()}
            <span className={cn(getChangeColor())}>
              {change > 0 ? '+' : ''}
              {change.toFixed(2)}%
            </span>
            <span className="text-muted-foreground">{changeLabel}</span>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
