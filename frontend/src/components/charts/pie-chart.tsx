'use client'

import { PieChart as RechartsPieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'
import { formatCurrency, formatPercent } from '@/lib/utils'
import { CHART_COLORS } from '@/lib/constants'

interface AllocationData {
  name: string
  value: number
  percentage: number
  color?: string
}

interface PieChartProps {
  data: AllocationData[]
  height?: number
  showLegend?: boolean
}

const COLORS = [
  CHART_COLORS.chart1,
  CHART_COLORS.chart2,
  CHART_COLORS.chart3,
  CHART_COLORS.chart4,
  CHART_COLORS.chart5,
  'hsl(200 70% 50%)',
  'hsl(160 60% 45%)',
  'hsl(30 90% 55%)',
]

export function AllocationPieChart({ data, height = 300, showLegend = true }: PieChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex h-[300px] items-center justify-center text-muted-foreground">
        No allocation data available
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <RechartsPieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={80}
          paddingAngle={2}
          dataKey="value"
          nameKey="name"
          label={({ name, percentage }) => `${name} (${percentage.toFixed(1)}%)`}
          labelLine={false}
        >
          {data.map((entry, index) => (
            <Cell
              key={`cell-${index}`}
              fill={entry.color || COLORS[index % COLORS.length]}
              stroke="hsl(var(--background))"
              strokeWidth={2}
            />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            backgroundColor: 'hsl(var(--card))',
            border: '1px solid hsl(var(--border))',
            borderRadius: '8px',
          }}
          formatter={(value: number, name: string, props: any) => [
            formatCurrency(value),
            name,
          ]}
        />
        {showLegend && (
          <Legend
            verticalAlign="bottom"
            height={36}
            formatter={(value, entry: any) => (
              <span style={{ color: 'hsl(var(--foreground))' }}>{value}</span>
            )}
          />
        )}
      </RechartsPieChart>
    </ResponsiveContainer>
  )
}
