'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { Portfolio, PortfolioSummary } from '@/types/portfolio'

export function usePortfolios() {
  return useQuery({
    queryKey: ['portfolios'],
    queryFn: () => api.get<PortfolioSummary[]>('/api/portfolios'),
  })
}

export function usePortfolio(id: string) {
  return useQuery({
    queryKey: ['portfolio', id],
    queryFn: () => api.get<Portfolio>(`/api/portfolios/${id}`),
    enabled: !!id,
  })
}

export function useCreatePortfolio() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: { name: string; description?: string }) =>
      api.post<Portfolio>('/api/portfolios', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portfolios'] })
    },
  })
}

export function useDeletePortfolio() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => api.delete(`/api/portfolios/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portfolios'] })
    },
  })
}
