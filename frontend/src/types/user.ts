export interface User {
  id: string
  email: string
  name: string
  createdAt: string
  updatedAt: string
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
