'use client'

import { useState } from 'react'
import { Plus, Trash2, GripVertical } from 'lucide-react'
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
import { INDICATORS, OPERATORS } from '@/lib/constants'
import { Rule, RuleCondition, IndicatorType, ConditionOperator } from '@/types/strategy'

interface RuleBuilderProps {
  rules: Rule[]
  onChange: (rules: Rule[]) => void
  disabled?: boolean
}

function generateId() {
  return Math.random().toString(36).substring(2, 9)
}

const defaultCondition: () => RuleCondition = () => ({
  id: generateId(),
  indicator: { type: 'price' as IndicatorType },
  operator: 'greater_than' as ConditionOperator,
  value: 0,
})

const defaultRule: () => Rule = () => ({
  id: generateId(),
  name: 'New Rule',
  action: 'buy',
  conditions: [defaultCondition()],
  conditionLogic: 'and',
  positionSize: 10,
  positionSizeType: 'percent',
})

export function RuleBuilder({ rules, onChange, disabled }: RuleBuilderProps) {
  const addRule = () => {
    onChange([...rules, defaultRule()])
  }

  const removeRule = (ruleId: string) => {
    onChange(rules.filter((r) => r.id !== ruleId))
  }

  const updateRule = (ruleId: string, updates: Partial<Rule>) => {
    onChange(rules.map((r) => (r.id === ruleId ? { ...r, ...updates } : r)))
  }

  const addCondition = (ruleId: string) => {
    onChange(
      rules.map((r) =>
        r.id === ruleId ? { ...r, conditions: [...r.conditions, defaultCondition()] } : r
      )
    )
  }

  const removeCondition = (ruleId: string, conditionId: string) => {
    onChange(
      rules.map((r) =>
        r.id === ruleId
          ? { ...r, conditions: r.conditions.filter((c) => c.id !== conditionId) }
          : r
      )
    )
  }

  const updateCondition = (ruleId: string, conditionId: string, updates: Partial<RuleCondition>) => {
    onChange(
      rules.map((r) =>
        r.id === ruleId
          ? {
              ...r,
              conditions: r.conditions.map((c) =>
                c.id === conditionId ? { ...c, ...updates } : c
              ),
            }
          : r
      )
    )
  }

  return (
    <div className="space-y-4">
      {rules.length === 0 && (
        <div className="flex h-32 items-center justify-center rounded-lg border border-dashed text-muted-foreground">
          No rules defined. Add a rule to get started.
        </div>
      )}

      {rules.map((rule, ruleIndex) => (
        <Card key={rule.id}>
          <CardHeader className="flex flex-row items-center justify-between py-3">
            <div className="flex items-center gap-2">
              <GripVertical className="h-4 w-4 text-muted-foreground" />
              <Input
                value={rule.name}
                onChange={(e) => updateRule(rule.id, { name: e.target.value })}
                className="h-8 w-48"
                disabled={disabled}
              />
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => removeRule(rule.id)}
              disabled={disabled}
            >
              <Trash2 className="h-4 w-4 text-destructive" />
            </Button>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
              <div className="space-y-1">
                <Label className="text-xs">Action</Label>
                <Select
                  value={rule.action}
                  onValueChange={(value: 'buy' | 'sell') => updateRule(rule.id, { action: value })}
                  disabled={disabled}
                >
                  <SelectTrigger className="h-8">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="buy">Buy</SelectItem>
                    <SelectItem value="sell">Sell</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-1">
                <Label className="text-xs">Logic</Label>
                <Select
                  value={rule.conditionLogic}
                  onValueChange={(value: 'and' | 'or') =>
                    updateRule(rule.id, { conditionLogic: value })
                  }
                  disabled={disabled}
                >
                  <SelectTrigger className="h-8">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="and">All conditions (AND)</SelectItem>
                    <SelectItem value="or">Any condition (OR)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-1">
                <Label className="text-xs">Position Size</Label>
                <Input
                  type="number"
                  value={rule.positionSize}
                  onChange={(e) =>
                    updateRule(rule.id, { positionSize: parseFloat(e.target.value) || 0 })
                  }
                  className="h-8"
                  disabled={disabled}
                />
              </div>

              <div className="space-y-1">
                <Label className="text-xs">Size Type</Label>
                <Select
                  value={rule.positionSizeType}
                  onValueChange={(value: 'percent' | 'fixed') =>
                    updateRule(rule.id, { positionSizeType: value })
                  }
                  disabled={disabled}
                >
                  <SelectTrigger className="h-8">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="percent">% of Portfolio</SelectItem>
                    <SelectItem value="fixed">Fixed Amount</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label className="text-xs text-muted-foreground">Conditions</Label>
              {rule.conditions.map((condition, condIndex) => (
                <div key={condition.id} className="flex items-center gap-2">
                  {condIndex > 0 && (
                    <span className="w-10 text-center text-xs text-muted-foreground">
                      {rule.conditionLogic.toUpperCase()}
                    </span>
                  )}

                  <Select
                    value={condition.indicator.type}
                    onValueChange={(value: IndicatorType) =>
                      updateCondition(rule.id, condition.id, {
                        indicator: { ...condition.indicator, type: value },
                      })
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

                  {(condition.indicator.type === 'sma' ||
                    condition.indicator.type === 'ema' ||
                    condition.indicator.type === 'rsi') && (
                    <Input
                      type="number"
                      placeholder="Period"
                      value={condition.indicator.period || ''}
                      onChange={(e) =>
                        updateCondition(rule.id, condition.id, {
                          indicator: {
                            ...condition.indicator,
                            period: parseInt(e.target.value) || undefined,
                          },
                        })
                      }
                      className="h-8 w-20"
                      disabled={disabled}
                    />
                  )}

                  <Select
                    value={condition.operator}
                    onValueChange={(value: ConditionOperator) =>
                      updateCondition(rule.id, condition.id, { operator: value })
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
                      updateCondition(rule.id, condition.id, {
                        value: parseFloat(e.target.value) || 0,
                      })
                    }
                    className="h-8 w-24"
                    disabled={disabled}
                  />

                  {rule.conditions.length > 1 && (
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      onClick={() => removeCondition(rule.id, condition.id)}
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
                onClick={() => addCondition(rule.id)}
                disabled={disabled}
              >
                <Plus className="mr-1 h-3 w-3" />
                Add Condition
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}

      <Button variant="outline" onClick={addRule} disabled={disabled}>
        <Plus className="mr-2 h-4 w-4" />
        Add Rule
      </Button>
    </div>
  )
}
