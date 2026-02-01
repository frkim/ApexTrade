import { StrategyForm } from '@/components/forms/strategy-form'

export default function NewStrategyPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Create Strategy</h1>
        <p className="text-muted-foreground">Define your trading rules and parameters</p>
      </div>

      <StrategyForm />
    </div>
  )
}
