import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { User, LoginCredentials, RegisterData } from '@/types'
import { authAPI } from '@/services/api'

interface AuthContextType {
  user: User | null
  loading: boolean
  isAuthenticated: boolean
  login: (credentials: LoginCredentials) => Promise<void>
  register: (userData: RegisterData) => Promise<void>
  logout: () => Promise<void>
  updateProfile: (userData: Partial<User>) => Promise<void>
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const queryClient = useQueryClient()

  // Check if user is authenticated on mount
  useEffect(() => {
    const token = localStorage.getItem('accessToken')
    if (token) {
      // Token exists, try to get user profile
      refetchProfile()
    } else {
      setLoading(false)
    }
  }, [])

  // Get user profile query
  const { refetch: refetchProfile } = useQuery({
    queryKey: ['user-profile'],
    queryFn: authAPI.getProfile,
    enabled: false, // Don't run automatically
    retry: false,
    onSuccess: (data) => {
      setUser(data)
      setLoading(false)
    },
    onError: () => {
      // Profile fetch failed, clear auth data
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('user')
      setUser(null)
      setLoading(false)
    },
  })

  // Login mutation
  const loginMutation = useMutation({
    mutationFn: authAPI.login,
    onSuccess: (data) => {
      const { user, token, refreshToken } = data
      
      // Store tokens
      localStorage.setItem('accessToken', token)
      localStorage.setItem('refreshToken', refreshToken)
      localStorage.setItem('user', JSON.stringify(user))
      
      // Update state
      setUser(user)
      
      // Invalidate and refetch user data
      queryClient.invalidateQueries({ queryKey: ['user-profile'] })
      
      toast.success('Welcome back!')
    },
    onError: (error: any) => {
      const message = error.response?.data?.message || 'Login failed'
      toast.error(message)
    },
  })

  // Register mutation
  const registerMutation = useMutation({
    mutationFn: authAPI.register,
    onSuccess: (data) => {
      const { user, token, refreshToken } = data
      
      // Store tokens
      localStorage.setItem('accessToken', token)
      localStorage.setItem('refreshToken', refreshToken)
      localStorage.setItem('user', JSON.stringify(user))
      
      // Update state
      setUser(user)
      
      // Invalidate and refetch user data
      queryClient.invalidateQueries({ queryKey: ['user-profile'] })
      
      toast.success('Account created successfully!')
    },
    onError: (error: any) => {
      const message = error.response?.data?.message || 'Registration failed'
      toast.error(message)
    },
  })

  // Logout mutation
  const logoutMutation = useMutation({
    mutationFn: authAPI.logout,
    onSuccess: () => {
      // Clear local storage
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('user')
      
      // Clear state
      setUser(null)
      
      // Clear all queries
      queryClient.clear()
      
      toast.success('Logged out successfully')
    },
    onError: () => {
      // Even if logout API fails, clear local data
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('user')
      setUser(null)
      queryClient.clear()
    },
  })

  // Update profile mutation
  const updateProfileMutation = useMutation({
    mutationFn: authAPI.updateProfile,
    onSuccess: (updatedUser) => {
      setUser(updatedUser)
      localStorage.setItem('user', JSON.stringify(updatedUser))
      queryClient.invalidateQueries({ queryKey: ['user-profile'] })
      toast.success('Profile updated successfully')
    },
    onError: (error: any) => {
      const message = error.response?.data?.message || 'Failed to update profile'
      toast.error(message)
    },
  })

  // Change password mutation
  const changePasswordMutation = useMutation({
    mutationFn: ({ currentPassword, newPassword }: { currentPassword: string; newPassword: string }) =>
      authAPI.changePassword(currentPassword, newPassword),
    onSuccess: () => {
      toast.success('Password changed successfully')
    },
    onError: (error: any) => {
      const message = error.response?.data?.message || 'Failed to change password'
      toast.error(message)
    },
  })

  // Auth methods
  const login = async (credentials: LoginCredentials) => {
    await loginMutation.mutateAsync(credentials)
  }

  const register = async (userData: RegisterData) => {
    await registerMutation.mutateAsync(userData)
  }

  const logout = async () => {
    await logoutMutation.mutateAsync()
  }

  const updateProfile = async (userData: Partial<User>) => {
    await updateProfileMutation.mutateAsync(userData)
  }

  const changePassword = async (currentPassword: string, newPassword: string) => {
    await changePasswordMutation.mutateAsync({ currentPassword, newPassword })
  }

  const value: AuthContextType = {
    user,
    loading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    updateProfile,
    changePassword,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// Custom hook to use auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// Hook to check if user has specific permissions
export const usePermissions = () => {
  const { user } = useAuth()
  
  return {
    canViewHealthHistory: !!user,
    canEditProfile: !!user,
    canAccessAnalytics: !!user,
    canManageNotifications: !!user,
    isAdmin: user?.role === 'admin',
    isProvider: user?.role === 'provider',
  }
}

// Hook to get user's emergency contact
export const useEmergencyContact = () => {
  const { user } = useAuth()
  return user?.emergencyContact
}

// Hook to get user's insurance info
export const useInsuranceInfo = () => {
  const { user } = useAuth()
  return user?.insurance
}
