import Link from 'next/link'
import { ArrowUpRight, ArrowDownRight } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { formatCurrency, formatPercent } from '@/lib/utils'
import { PortfolioSummary } from '@/types/portfolio'

interface PortfolioCardProps {
  portfolio: PortfolioSummary
}

export function PortfolioCard({ portfolio }: PortfolioCardProps) {
  const isPositive = portfolio.dayChangePercent >= 0

  return (
    <Link href={`/dashboard/portfolios/${portfolio.id}`}>
      <Card className="transition-colors hover:bg-accent/50">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium">{portfolio.name}</CardTitle>
          <Badge variant="secondary">{portfolio.positionCount} positions</Badge>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{formatCurrency(portfolio.totalValue)}</div>
          <div className="flex items-center gap-1 text-sm">
            {isPositive ? (
              <ArrowUpRight className="h-4 w-4 text-success" />
            ) : (
              <ArrowDownRight className="h-4 w-4 text-destructive" />
            )}
            <span className={isPositive ? 'text-success' : 'text-destructive'}>
              {formatCurrency(Math.abs(portfolio.dayChange))} (
              {formatPercent(portfolio.dayChangePercent)})
            </span>
            <span className="text-muted-foreground">today</span>
          </div>
        </CardContent>
      </Card>
    </Link>
  )
}
