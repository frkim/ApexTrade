'use client'

import { Plus, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { INDICATORS, OPERATORS } from '@/lib/constants'
import { RuleCondition, RuleDefinition, ConditionOperator } from '@/types/strategy'

interface RuleBuilderProps {
  rules: RuleDefinition
  onChange: (rules: RuleDefinition) => void
  disabled?: boolean
}

const defaultCondition = (): RuleCondition => ({
  indicator: 'price',
  operator: 'gt',
  value: 0,
})

export function RuleBuilder({ rules, onChange, disabled }: RuleBuilderProps) {
  const addCondition = () => {
    onChange({
      ...rules,
      conditions: [...rules.conditions, defaultCondition()],
    })
  }

  const removeCondition = (index: number) => {
    onChange({
      ...rules,
      conditions: rules.conditions.filter((_, i) => i !== index),
    })
  }

  const updateCondition = (index: number, updates: Partial<RuleCondition>) => {
    onChange({
      ...rules,
      conditions: rules.conditions.map((c, i) =>
        i === index ? { ...c, ...updates } : c
      ),
    })
  }

  const updateLogic = (logic: 'and' | 'or') => {
    onChange({ ...rules, logic })
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="py-3">
          <div className="flex items-center justify-between">
            <Label className="text-sm font-medium">Trading Rules</Label>
            <Select
              value={rules.logic}
              onValueChange={(value: 'and' | 'or') => updateLogic(value)}
              disabled={disabled}
            >
              <SelectTrigger className="h-8 w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="and">All conditions (AND)</SelectItem>
                <SelectItem value="or">Any condition (OR)</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {rules.conditions.length === 0 && (
            <div className="flex h-20 items-center justify-center rounded-lg border border-dashed text-muted-foreground">
              No conditions defined. Add a condition to get started.
            </div>
          )}

          {rules.conditions.map((condition, index) => (
            <div key={index} className="flex items-center gap-2">
              {index > 0 && (
                <span className="w-10 text-center text-xs text-muted-foreground">
                  {rules.logic.toUpperCase()}
                </span>
              )}

              <Select
                value={condition.indicator}
                onValueChange={(value: string) =>
                  updateCondition(index, { indicator: value })
                }
                disabled={disabled}
              >
                <SelectTrigger className="h-8 w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {INDICATORS.map((ind) => (
                    <SelectItem key={ind.value} value={ind.value}>
                      {ind.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Select
                value={condition.operator}
                onValueChange={(value: ConditionOperator) =>
                  updateCondition(index, { operator: value })
                }
                disabled={disabled}
              >
                <SelectTrigger className="h-8 w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {OPERATORS.map((op) => (
                    <SelectItem key={op.value} value={op.value}>
                      {op.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Input
                type="number"
                placeholder="Value"
                value={typeof condition.value === 'number' ? condition.value : ''}
                onChange={(e) =>
                  updateCondition(index, {
                    value: parseFloat(e.target.value) || 0,
                  })
                }
                className="h-8 w-24"
                disabled={disabled}
              />

              {rules.conditions.length > 1 && (
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8"
                  onClick={() => removeCondition(index)}
                  disabled={disabled}
                >
                  <Trash2 className="h-3 w-3" />
                </Button>
              )}
            </div>
          ))}

          <Button
            variant="outline"
            size="sm"
            onClick={addCondition}
            disabled={disabled}
          >
            <Plus className="mr-1 h-3 w-3" />
            Add Condition
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
