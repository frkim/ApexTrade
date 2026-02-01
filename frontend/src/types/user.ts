// User type aligned with backend UserResponse schema
export interface User {
  id: string
  email: string
  username: string
  full_name: string | null
  is_active: boolean
  is_verified: boolean
  created_at: string
  last_login: string | null
}

export interface UserSettings {
  userId: string
  theme: 'light' | 'dark' | 'system'
  notifications: boolean
  defaultPortfolioId?: string
}

export interface ApiKey {
  id: string
  name: string
  exchange: string
  createdAt: string
  lastUsed?: string
  isActive: boolean
}
