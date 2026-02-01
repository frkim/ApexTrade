'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { Strategy, StrategyPerformance } from '@/types/strategy'

export function useStrategies() {
  return useQuery({
    queryKey: ['strategies'],
    queryFn: () => api.get<Strategy[]>('/api/strategies'),
  })
}

export function useStrategy(id: string) {
  return useQuery({
    queryKey: ['strategy', id],
    queryFn: () => api.get<Strategy>(`/api/strategies/${id}`),
    enabled: !!id,
  })
}

export function useStrategyPerformance(id: string) {
  return useQuery({
    queryKey: ['strategy-performance', id],
    queryFn: () => api.get<StrategyPerformance>(`/api/strategies/${id}/performance`),
    enabled: !!id,
  })
}

export function useCreateStrategy() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: Partial<Strategy>) => api.post<Strategy>('/api/strategies', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['strategies'] })
    },
  })
}

export function useUpdateStrategy() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Strategy> }) =>
      api.put<Strategy>(`/api/strategies/${id}`, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['strategies'] })
      queryClient.invalidateQueries({ queryKey: ['strategy', variables.id] })
    },
  })
}

export function useDeleteStrategy() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => api.delete(`/api/strategies/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['strategies'] })
    },
  })
}

export function useActivateStrategy() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => api.post(`/api/strategies/${id}/activate`),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['strategies'] })
      queryClient.invalidateQueries({ queryKey: ['strategy', id] })
    },
  })
}

export function usePauseStrategy() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => api.post(`/api/strategies/${id}/pause`),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['strategies'] })
      queryClient.invalidateQueries({ queryKey: ['strategy', id] })
    },
  })
}
