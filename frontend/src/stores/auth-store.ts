import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { User } from '@/types/user'
import { api } from '@/lib/api'

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (name: string, email: string, password: string) => Promise<void>
  logout: () => void
  setUser: (user: User) => void
  checkAuth: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: true,

      login: async (email: string, password: string) => {
        const response = await api.post<{ user: User; token: string }>('/api/auth/login', {
          email,
          password,
        })
        localStorage.setItem('auth_token', response.token)
        set({
          user: response.user,
          token: response.token,
          isAuthenticated: true,
        })
      },

      register: async (name: string, email: string, password: string) => {
        const response = await api.post<{ user: User; token: string }>('/api/auth/register', {
          name,
          email,
          password,
        })
        localStorage.setItem('auth_token', response.token)
        set({
          user: response.user,
          token: response.token,
          isAuthenticated: true,
        })
      },

      logout: () => {
        localStorage.removeItem('auth_token')
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        })
      },

      setUser: (user: User) => {
        set({ user })
      },

      checkAuth: async () => {
        const token = localStorage.getItem('auth_token')
        if (!token) {
          set({ isLoading: false, isAuthenticated: false })
          return
        }

        try {
          const user = await api.get<User>('/api/auth/me')
          set({ user, token, isAuthenticated: true, isLoading: false })
        } catch {
          localStorage.removeItem('auth_token')
          set({ user: null, token: null, isAuthenticated: false, isLoading: false })
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token }),
    }
  )
)
