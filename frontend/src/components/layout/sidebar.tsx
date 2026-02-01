'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard,
  LineChart,
  Briefcase,
  History,
  Settings,
  TrendingUp,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Strategies', href: '/dashboard/strategies', icon: LineChart },
  { name: 'Portfolios', href: '/dashboard/portfolios', icon: Briefcase },
  { name: 'Backtests', href: '/dashboard/backtests', icon: History },
  { name: 'Settings', href: '/dashboard/settings', icon: Settings },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="hidden w-64 flex-shrink-0 border-r bg-card lg:block">
      <div className="flex h-full flex-col">
        <div className="flex h-16 items-center gap-2 border-b px-6">
          <TrendingUp className="h-6 w-6 text-primary" />
          <span className="text-xl font-bold">ApexTrade</span>
        </div>

        <nav className="flex-1 space-y-1 px-3 py-4">
          {navigation.map((item) => {
            const isActive =
              pathname === item.href ||
              (item.href !== '/dashboard' && pathname.startsWith(item.href))

            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                )}
              >
                <item.icon className="h-5 w-5" />
                {item.name}
              </Link>
            )
          })}
        </nav>

        <div className="border-t p-4">
          <div className="rounded-lg bg-muted p-4">
            <p className="text-sm font-medium">Need Help?</p>
            <p className="mt-1 text-xs text-muted-foreground">
              Check our documentation for guides and tutorials.
            </p>
            <Link
              href="/docs"
              className="mt-3 inline-block text-sm text-primary hover:underline"
            >
              View Documentation
            </Link>
          </div>
        </div>
      </div>
    </aside>
  )
}
