import { ArrowUpRight, ArrowDownRight } from 'lucide-react'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { formatCurrency, formatDateTime } from '@/lib/utils'
import { Trade, TradeStatus, TradeSide } from '@/types/trade'

interface RecentTradesProps {
  trades: Trade[]
}

const statusConfig: Record<TradeStatus, { label: string; variant: 'default' | 'success' | 'warning' | 'destructive' | 'secondary' }> = {
  pending: { label: 'Pending', variant: 'secondary' },
  filled: { label: 'Filled', variant: 'success' },
  partial: { label: 'Partial', variant: 'warning' },
  cancelled: { label: 'Cancelled', variant: 'secondary' },
  rejected: { label: 'Rejected', variant: 'destructive' },
}

export function RecentTrades({ trades }: RecentTradesProps) {
  if (!trades || trades.length === 0) {
    return (
      <div className="flex h-32 items-center justify-center text-muted-foreground">
        No recent trades
      </div>
    )
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Symbol</TableHead>
          <TableHead>Side</TableHead>
          <TableHead>Type</TableHead>
          <TableHead className="text-right">Qty</TableHead>
          <TableHead className="text-right">Price</TableHead>
          <TableHead className="text-right">P&L</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Time</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {trades.map((trade) => {
          const status = statusConfig[trade.status]
          const hasPnl = trade.pnl !== undefined && trade.pnl !== null

          return (
            <TableRow key={trade.id}>
              <TableCell className="font-medium">{trade.symbol}</TableCell>
              <TableCell>
                <div className="flex items-center gap-1">
                  {trade.side === 'buy' ? (
                    <ArrowUpRight className="h-4 w-4 text-success" />
                  ) : (
                    <ArrowDownRight className="h-4 w-4 text-destructive" />
                  )}
                  <span className={trade.side === 'buy' ? 'text-success' : 'text-destructive'}>
                    {trade.side.toUpperCase()}
                  </span>
                </div>
              </TableCell>
              <TableCell className="capitalize">{trade.type}</TableCell>
              <TableCell className="text-right">{trade.filledQuantity}/{trade.quantity}</TableCell>
              <TableCell className="text-right">
                {trade.filledPrice ? formatCurrency(trade.filledPrice) : '-'}
              </TableCell>
              <TableCell className="text-right">
                {hasPnl ? (
                  <span className={trade.pnl! >= 0 ? 'text-success' : 'text-destructive'}>
                    {formatCurrency(trade.pnl!)}
                  </span>
                ) : (
                  '-'
                )}
              </TableCell>
              <TableCell>
                <Badge variant={status.variant}>{status.label}</Badge>
              </TableCell>
              <TableCell className="text-muted-foreground">
                {formatDateTime(trade.createdAt)}
              </TableCell>
            </TableRow>
          )
        })}
      </TableBody>
    </Table>
  )
}
