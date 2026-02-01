'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/stores/auth-store'

export function useAuth(requireAuth = true) {
  const router = useRouter()
  const { user, isAuthenticated, isLoading, login, logout, register, checkAuth } = useAuthStore()

  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  useEffect(() => {
    if (!isLoading && requireAuth && !isAuthenticated) {
      router.push('/login')
    }
  }, [isLoading, requireAuth, isAuthenticated, router])

  return {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    register,
  }
}
