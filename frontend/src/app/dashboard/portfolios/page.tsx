'use client'

import Link from 'next/link'
import { Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { PortfolioCard } from '@/components/dashboard/portfolio-card'
import { PortfolioSummary } from '@/types/portfolio'

// Mock data
const mockPortfolios: PortfolioSummary[] = [
  {
    id: '1',
    name: 'Main Portfolio',
    totalValue: 125420.50,
    dayChange: 1250.00,
    dayChangePercent: 1.01,
    positionCount: 5,
  },
  {
    id: '2',
    name: 'Crypto Trading',
    totalValue: 45680.25,
    dayChange: -320.15,
    dayChangePercent: -0.70,
    positionCount: 3,
  },
  {
    id: '3',
    name: 'Test Portfolio',
    totalValue: 10000.00,
    dayChange: 0,
    dayChangePercent: 0,
    positionCount: 0,
  },
]

export default function PortfoliosPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Portfolios</h1>
          <p className="text-muted-foreground">Manage your investment portfolios</p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          New Portfolio
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {mockPortfolios.map((portfolio) => (
          <PortfolioCard key={portfolio.id} portfolio={portfolio} />
        ))}
      </div>

      {mockPortfolios.length === 0 && (
        <div className="flex h-64 items-center justify-center rounded-lg border border-dashed">
          <div className="text-center">
            <p className="text-muted-foreground">No portfolios yet</p>
            <Button variant="link">Create your first portfolio</Button>
          </div>
        </div>
      )}
    </div>
  )
}
