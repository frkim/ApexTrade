'use client'

import {
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from 'recharts'
import { formatCurrency, formatDate } from '@/lib/utils'
import { CHART_COLORS } from '@/lib/constants'

interface EquityPoint {
  date: string
  equity: number
  drawdown?: number
}

interface EquityCurveProps {
  data: EquityPoint[]
  showDrawdown?: boolean
  height?: number
}

export function EquityCurve({ data, showDrawdown = false, height = 300 }: EquityCurveProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex h-[300px] items-center justify-center text-muted-foreground">
        No equity data available
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={CHART_COLORS.primary} stopOpacity={0.3} />
            <stop offset="95%" stopColor={CHART_COLORS.primary} stopOpacity={0} />
          </linearGradient>
          {showDrawdown && (
            <linearGradient id="colorDrawdown" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={CHART_COLORS.destructive} stopOpacity={0.3} />
              <stop offset="95%" stopColor={CHART_COLORS.destructive} stopOpacity={0} />
            </linearGradient>
          )}
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
        <XAxis
          dataKey="date"
          tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
          tickFormatter={(value) => formatDate(value, { month: 'short', day: 'numeric' })}
          stroke="hsl(var(--border))"
        />
        <YAxis
          tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
          tickFormatter={(value) => formatCurrency(value)}
          stroke="hsl(var(--border))"
        />
        <Tooltip
          contentStyle={{
            backgroundColor: 'hsl(var(--card))',
            border: '1px solid hsl(var(--border))',
            borderRadius: '8px',
          }}
          labelFormatter={(value) => formatDate(value)}
          formatter={(value: number, name: string) => [
            formatCurrency(value),
            name === 'equity' ? 'Equity' : 'Drawdown',
          ]}
        />
        <Area
          type="monotone"
          dataKey="equity"
          stroke={CHART_COLORS.primary}
          fillOpacity={1}
          fill="url(#colorEquity)"
          strokeWidth={2}
        />
        {showDrawdown && (
          <Area
            type="monotone"
            dataKey="drawdown"
            stroke={CHART_COLORS.destructive}
            fillOpacity={1}
            fill="url(#colorDrawdown)"
            strokeWidth={2}
          />
        )}
      </AreaChart>
    </ResponsiveContainer>
  )
}
