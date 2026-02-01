import { create } from 'zustand'
import { Portfolio, PortfolioSummary } from '@/types/portfolio'
import { api } from '@/lib/api'

interface PortfolioState {
  portfolios: PortfolioSummary[]
  selectedPortfolio: Portfolio | null
  isLoading: boolean
  error: string | null
  fetchPortfolios: () => Promise<void>
  fetchPortfolio: (id: string) => Promise<void>
  selectPortfolio: (id: string) => void
  clearError: () => void
}

export const usePortfolioStore = create<PortfolioState>((set, get) => ({
  portfolios: [],
  selectedPortfolio: null,
  isLoading: false,
  error: null,

  fetchPortfolios: async () => {
    set({ isLoading: true, error: null })
    try {
      const portfolios = await api.get<PortfolioSummary[]>('/api/portfolios')
      set({ portfolios, isLoading: false })
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to fetch portfolios',
        isLoading: false,
      })
    }
  },

  fetchPortfolio: async (id: string) => {
    set({ isLoading: true, error: null })
    try {
      const portfolio = await api.get<Portfolio>(`/api/portfolios/${id}`)
      set({ selectedPortfolio: portfolio, isLoading: false })
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to fetch portfolio',
        isLoading: false,
      })
    }
  },

  selectPortfolio: (id: string) => {
    const portfolio = get().portfolios.find((p) => p.id === id)
    if (portfolio) {
      get().fetchPortfolio(id)
    }
  },

  clearError: () => set({ error: null }),
}))
