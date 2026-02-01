import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { User } from '@/types/user'
import { api } from '@/lib/api'

// Response types matching backend
interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string, fullName?: string) => Promise<void>
  logout: () => void
  setUser: (user: User) => void
  checkAuth: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: true,

      login: async (email: string, password: string) => {
        const response = await api.post<TokenResponse>('/api/v1/auth/login', {
          email,
          password,
        })
        localStorage.setItem('auth_token', response.access_token)
        
        // Fetch user info after login
        const user = await api.get<User>('/api/v1/auth/me')
        set({
          user,
          token: response.access_token,
          isAuthenticated: true,
        })
      },

      register: async (username: string, email: string, password: string, fullName?: string) => {
        // Register creates user but doesn't return token
        await api.post('/api/v1/auth/register', {
          username,
          email,
          password,
          full_name: fullName,
        })
        
        // Login after successful registration
        const response = await api.post<TokenResponse>('/api/v1/auth/login', {
          email,
          password,
        })
        localStorage.setItem('auth_token', response.access_token)
        
        const user = await api.get<User>('/api/v1/auth/me')
        set({
          user,
          token: response.access_token,
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
          const user = await api.get<User>('/api/v1/auth/me')
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
