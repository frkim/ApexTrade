export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
export const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'

// API version prefix - all API calls should use this
export const API_V1_PREFIX = '/api/v1'

export const TIMEFRAMES = [
  { value: '1m', label: '1 Minute' },
  { value: '5m', label: '5 Minutes' },
  { value: '15m', label: '15 Minutes' },
  { value: '1h', label: '1 Hour' },
  { value: '4h', label: '4 Hours' },
  { value: '1d', label: '1 Day' },
  { value: '1w', label: '1 Week' },
] as const

export const INDICATORS = [
  { value: 'sma', label: 'Simple Moving Average (SMA)' },
  { value: 'ema', label: 'Exponential Moving Average (EMA)' },
  { value: 'rsi', label: 'Relative Strength Index (RSI)' },
  { value: 'macd', label: 'MACD' },
  { value: 'bollinger_bands', label: 'Bollinger Bands' },
  { value: 'atr', label: 'Average True Range (ATR)' },
  { value: 'volume', label: 'Volume' },
  { value: 'price', label: 'Price' },
] as const

export const OPERATORS = [
  { value: 'gt', label: 'Greater Than (>)' },
  { value: 'lt', label: 'Less Than (<)' },
  { value: 'eq', label: 'Equals (=)' },
  { value: 'gte', label: 'Greater or Equal (>=)' },
  { value: 'lte', label: 'Less or Equal (<=)' },
  { value: 'crosses_above', label: 'Crosses Above' },
  { value: 'crosses_below', label: 'Crosses Below' },
] as const

export const EXCHANGES = [
  { value: 'binance', label: 'Binance' },
  { value: 'coinbase', label: 'Coinbase' },
  { value: 'kraken', label: 'Kraken' },
  { value: 'alpaca', label: 'Alpaca' },
] as const

export const CHART_COLORS = {
  primary: 'hsl(217.2 91.2% 59.8%)',
  success: 'hsl(142 70% 45%)',
  warning: 'hsl(38 92% 50%)',
  destructive: 'hsl(0 84.2% 60.2%)',
  chart1: 'hsl(217.2 91.2% 59.8%)',
  chart2: 'hsl(142 70% 45%)',
  chart3: 'hsl(38 92% 50%)',
  chart4: 'hsl(280 65% 60%)',
  chart5: 'hsl(340 75% 55%)',
}
