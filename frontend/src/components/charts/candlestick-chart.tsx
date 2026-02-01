'use client'

import { useMemo } from 'react'
import {
  ComposedChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts'
import { formatDate } from '@/lib/utils'
import { CHART_COLORS } from '@/lib/constants'

interface OHLCData {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume?: number
}

interface CandlestickChartProps {
  data: OHLCData[]
  height?: number
}

interface CandleData extends OHLCData {
  isUp: boolean
  body: [number, number]
  wick: [number, number]
}

export function CandlestickChart({ data, height = 400 }: CandlestickChartProps) {
  const chartData = useMemo(() => {
    return data.map((item) => {
      const isUp = item.close >= item.open
      return {
        ...item,
        isUp,
        body: isUp ? [item.open, item.close] : [item.close, item.open],
        wick: [item.low, item.high],
      }
    })
  }, [data])

  if (!data || data.length === 0) {
    return (
      <div className="flex h-[400px] items-center justify-center text-muted-foreground">
        No price data available
      </div>
    )
  }

  const minPrice = Math.min(...data.map((d) => d.low)) * 0.99
  const maxPrice = Math.max(...data.map((d) => d.high)) * 1.01

  return (
    <ResponsiveContainer width="100%" height={height}>
      <ComposedChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
        <XAxis
          dataKey="date"
          tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
          tickFormatter={(value) => formatDate(value, { month: 'short', day: 'numeric' })}
          stroke="hsl(var(--border))"
        />
        <YAxis
          domain={[minPrice, maxPrice]}
          tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
          stroke="hsl(var(--border))"
        />
        <Tooltip
          contentStyle={{
            backgroundColor: 'hsl(var(--card))',
            border: '1px solid hsl(var(--border))',
            borderRadius: '8px',
          }}
          labelFormatter={(value) => formatDate(value)}
          formatter={(value: number[], name: string) => {
            if (name === 'body') {
              return [`Open: ${value[0]}, Close: ${value[1]}`, 'Price']
            }
            if (name === 'wick') {
              return [`Low: ${value[0]}, High: ${value[1]}`, 'Range']
            }
            return [value, name]
          }}
        />
        <Bar dataKey="wick" barSize={2} shape={<WickShape />} />
        <Bar dataKey="body" barSize={8} shape={<CandleShape />} />
      </ComposedChart>
    </ResponsiveContainer>
  )
}

function WickShape({ x, y, width, height, payload }: any) {
  const color = payload.isUp ? CHART_COLORS.success : CHART_COLORS.destructive
  return (
    <line
      x1={x + width / 2}
      y1={y}
      x2={x + width / 2}
      y2={y + height}
      stroke={color}
      strokeWidth={1}
    />
  )
}

function CandleShape({ x, y, width, height, payload }: any) {
  const color = payload.isUp ? CHART_COLORS.success : CHART_COLORS.destructive
  return (
    <rect
      x={x}
      y={y}
      width={width}
      height={Math.max(height, 1)}
      fill={color}
      stroke={color}
      strokeWidth={1}
    />
  )
}
