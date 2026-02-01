'use client'

import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useRouter } from 'next/navigation'
import { Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Alert, AlertDescription, AlertIcon } from '@/components/ui/alert'
import { RuleBuilder } from '@/components/dashboard/rule-builder'
import { useCreateStrategy, useUpdateStrategy } from '@/hooks/use-strategies'
import { TIMEFRAMES } from '@/lib/constants'
import { Strategy, Rule } from '@/types/strategy'

const strategySchema = z.object({
  name: z.string().min(1, 'Strategy name is required'),
  description: z.string().optional(),
  symbol: z.string().min(1, 'Symbol is required'),
  timeframe: z.string().min(1, 'Timeframe is required'),
})

type StrategyFormData = z.infer<typeof strategySchema>

interface StrategyFormProps {
  strategy?: Strategy
}

export function StrategyForm({ strategy }: StrategyFormProps) {
  const router = useRouter()
  const createStrategy = useCreateStrategy()
  const updateStrategy = useUpdateStrategy()

  const [error, setError] = useState<string | null>(null)
  const [rules, setRules] = useState<Rule[]>(strategy?.rules || [])

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<StrategyFormData>({
    resolver: zodResolver(strategySchema),
    defaultValues: {
      name: strategy?.name || '',
      description: strategy?.description || '',
      symbol: strategy?.symbol || '',
      timeframe: strategy?.timeframe || '1h',
    },
  })

  const timeframe = watch('timeframe')

  const onSubmit = async (data: StrategyFormData) => {
    try {
      setError(null)
      const strategyData = {
        ...data,
        rules,
        status: 'draft' as const,
      }

      if (strategy) {
        await updateStrategy.mutateAsync({ id: strategy.id, data: strategyData })
      } else {
        await createStrategy.mutateAsync(strategyData)
      }

      router.push('/dashboard/strategies')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save strategy')
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {error && (
        <Alert variant="destructive">
          <AlertIcon variant="destructive" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Basic Information</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="name">Strategy Name</Label>
              <Input
                id="name"
                placeholder="My Strategy"
                {...register('name')}
                disabled={isSubmitting}
              />
              {errors.name && <p className="text-sm text-destructive">{errors.name.message}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="symbol">Symbol</Label>
              <Input
                id="symbol"
                placeholder="BTCUSDT"
                {...register('symbol')}
                disabled={isSubmitting}
              />
              {errors.symbol && <p className="text-sm text-destructive">{errors.symbol.message}</p>}
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="timeframe">Timeframe</Label>
              <Select
                value={timeframe}
                onValueChange={(value) => setValue('timeframe', value)}
                disabled={isSubmitting}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select timeframe" />
                </SelectTrigger>
                <SelectContent>
                  {TIMEFRAMES.map((tf) => (
                    <SelectItem key={tf.value} value={tf.value}>
                      {tf.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.timeframe && (
                <p className="text-sm text-destructive">{errors.timeframe.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description (Optional)</Label>
              <Input
                id="description"
                placeholder="A brief description of your strategy"
                {...register('description')}
                disabled={isSubmitting}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Trading Rules</CardTitle>
        </CardHeader>
        <CardContent>
          <RuleBuilder rules={rules} onChange={setRules} disabled={isSubmitting} />
        </CardContent>
      </Card>

      <div className="flex justify-end gap-4">
        <Button
          type="button"
          variant="outline"
          onClick={() => router.push('/dashboard/strategies')}
          disabled={isSubmitting}
        >
          Cancel
        </Button>
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Saving...
            </>
          ) : strategy ? (
            'Update Strategy'
          ) : (
            'Create Strategy'
          )}
        </Button>
      </div>
    </form>
  )
}
