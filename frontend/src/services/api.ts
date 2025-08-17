import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { toast } from 'react-hot-toast'
import { 
  ApiResponse, 
  AuthResponse, 
  LoginCredentials, 
  RegisterData, 
  User,
  SymptomRequest,
  SymptomAnalysis,
  TriageRequest,
  TriageAssessment,
  HealthcareProvider,
  InsuranceProvider,
  HealthRecord,
  SearchFilters,
  PaginatedResponse
} from '@/types'

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const API_TIMEOUT = 30000 // 30 seconds

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for adding auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for handling errors and token refresh
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refreshToken')
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          })
          
          const { access_token } = response.data
          localStorage.setItem('accessToken', access_token)
          
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        }
      } catch (refreshError) {
        // Refresh token failed, redirect to login
        localStorage.removeItem('accessToken')
        localStorage.removeItem('refreshToken')
        localStorage.removeItem('user')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    // Handle other errors
    const errorMessage = error.response?.data?.message || error.message || 'An error occurred'
    
    if (error.response?.status >= 500) {
      toast.error('Server error. Please try again later.')
    } else if (error.response?.status === 404) {
      toast.error('Resource not found.')
    } else if (error.response?.status === 403) {
      toast.error('Access denied.')
    } else if (error.response?.status === 422) {
      toast.error('Invalid data provided.')
    } else {
      toast.error(errorMessage)
    }

    return Promise.reject(error)
  }
)

// Generic API methods
const apiService = {
  // GET request
  get: async <T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> => {
    const response = await api.get(url, config)
    return response.data
  },

  // POST request
  post: async <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> => {
    const response = await api.post(url, data, config)
    return response.data
  },

  // PUT request
  put: async <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> => {
    const response = await api.put(url, data, config)
    return response.data
  },

  // PATCH request
  patch: async <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> => {
    const response = await api.patch(url, data, config)
    return response.data
  },

  // DELETE request
  delete: async <T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> => {
    const response = await api.delete(url, config)
    return response.data
  },

  // File upload
  upload: async <T>(url: string, formData: FormData, config?: AxiosRequestConfig): Promise<ApiResponse<T>> => {
    const response = await api.post(url, formData, {
      ...config,
      headers: {
        'Content-Type': 'multipart/form-data',
        ...config?.headers,
      },
    })
    return response.data
  },
}

// Authentication API
export const authAPI = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response = await apiService.post<AuthResponse>('/auth/login', credentials)
    return response.data!
  },

  register: async (userData: RegisterData): Promise<AuthResponse> => {
    const response = await apiService.post<AuthResponse>('/auth/register', userData)
    return response.data!
  },

  logout: async (): Promise<void> => {
    await apiService.post('/auth/logout')
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('user')
  },

  refreshToken: async (refreshToken: string): Promise<{ access_token: string }> => {
    const response = await apiService.post<{ access_token: string }>('/auth/refresh', {
      refresh_token: refreshToken,
    })
    return response.data!
  },

  getProfile: async (): Promise<User> => {
    const response = await apiService.get<User>('/auth/profile')
    return response.data!
  },

  updateProfile: async (userData: Partial<User>): Promise<User> => {
    const response = await apiService.put<User>('/auth/profile', userData)
    return response.data!
  },

  changePassword: async (currentPassword: string, newPassword: string): Promise<void> => {
    await apiService.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    })
  },
}

// Symptom Analysis API
export const symptomsAPI = {
  analyzeSymptoms: async (request: SymptomRequest): Promise<SymptomAnalysis> => {
    const response = await apiService.post<SymptomAnalysis>('/symptoms/analyze', request)
    return response.data!
  },

  analyzeSymptomsBatch: async (requests: SymptomRequest[]): Promise<SymptomAnalysis[]> => {
    const response = await apiService.post<SymptomAnalysis[]>('/symptoms/analyze/batch', {
      requests,
    })
    return response.data!
  },

  getSymptomHistory: async (userId: string, page = 1, limit = 10): Promise<PaginatedResponse<SymptomAnalysis>> => {
    const response = await apiService.get<PaginatedResponse<SymptomAnalysis>>(
      `/symptoms/history/${userId}?page=${page}&limit=${limit}`
    )
    return response.data!
  },

  getMedicalConditions: async (): Promise<any[]> => {
    const response = await apiService.get<any[]>('/symptoms/conditions')
    return response.data!
  },
}

// Triage Assessment API
export const triageAPI = {
  assessTriage: async (request: TriageRequest): Promise<TriageAssessment> => {
    const response = await apiService.post<TriageAssessment>('/triage/assess', request)
    return response.data!
  },

  getTriageHistory: async (userId: string, page = 1, limit = 10): Promise<PaginatedResponse<TriageAssessment>> => {
    const response = await apiService.get<PaginatedResponse<TriageAssessment>>(
      `/triage/history/${userId}?page=${page}&limit=${limit}`
    )
    return response.data!
  },
}

// Provider Search API
export const providersAPI = {
  searchProviders: async (
    filters: SearchFilters,
    page = 1,
    limit = 10,
    sort?: { field: string; direction: 'asc' | 'desc' }
  ): Promise<PaginatedResponse<HealthcareProvider>> => {
    const params = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString(),
      ...filters,
    })
    
    if (sort) {
      params.append('sort_field', sort.field)
      params.append('sort_direction', sort.direction)
    }

    const response = await apiService.get<PaginatedResponse<HealthcareProvider>>(
      `/providers/search?${params.toString()}`
    )
    return response.data!
  },

  getProviderDetails: async (providerId: string): Promise<HealthcareProvider> => {
    const response = await apiService.get<HealthcareProvider>(`/providers/${providerId}`)
    return response.data!
  },

  getProviderReviews: async (providerId: string, page = 1, limit = 10): Promise<any> => {
    const response = await apiService.get<any>(
      `/providers/${providerId}/reviews?page=${page}&limit=${limit}`
    )
    return response.data!
  },

  bookAppointment: async (providerId: string, appointmentData: any): Promise<any> => {
    const response = await apiService.post<any>(`/providers/${providerId}/book`, appointmentData)
    return response.data!
  },
}

// Insurance API
export const insuranceAPI = {
  getInsuranceProviders: async (): Promise<InsuranceProvider[]> => {
    const response = await apiService.get<InsuranceProvider[]>('/insurance/providers')
    return response.data!
  },

  checkCoverage: async (providerId: string, serviceCode: string): Promise<any> => {
    const response = await apiService.post<any>('/insurance/check-coverage', {
      provider_id: providerId,
      service_code: serviceCode,
    })
    return response.data!
  },

  getInsuranceGuide: async (): Promise<any> => {
    const response = await apiService.get<any>('/insurance/guide')
    return response.data!
  },
}

// Health History API
export const healthHistoryAPI = {
  getHealthRecords: async (userId: string, page = 1, limit = 10): Promise<PaginatedResponse<HealthRecord>> => {
    const response = await apiService.get<PaginatedResponse<HealthRecord>>(
      `/health-history/${userId}?page=${page}&limit=${limit}`
    )
    return response.data!
  },

  addHealthRecord: async (record: Omit<HealthRecord, 'id' | 'userId' | 'createdAt'>): Promise<HealthRecord> => {
    const response = await apiService.post<HealthRecord>('/health-history', record)
    return response.data!
  },

  updateHealthRecord: async (recordId: string, updates: Partial<HealthRecord>): Promise<HealthRecord> => {
    const response = await apiService.put<HealthRecord>(`/health-history/${recordId}`, updates)
    return response.data!
  },

  deleteHealthRecord: async (recordId: string): Promise<void> => {
    await apiService.delete(`/health-history/${recordId}`)
  },

  uploadHealthDocument: async (file: File, recordId?: string): Promise<any> => { // Assuming FileUpload type is not defined, using 'any' for now
    const formData = new FormData()
    formData.append('file', file)
    if (recordId) {
      formData.append('record_id', recordId)
    }

    const response = await apiService.upload<any>('/health-history/upload', formData) // Assuming FileUpload type is not defined, using 'any' for now
    return response.data!
  },
}

// Analytics API
export const analyticsAPI = {
  trackEvent: async (event: string, properties: Record<string, any>): Promise<void> => {
    await apiService.post('/analytics/track', {
      event,
      properties,
      timestamp: new Date().toISOString(),
    })
  },

  getHealthMetrics: async (userId: string, startDate: string, endDate: string): Promise<any[]> => {
    const response = await apiService.get<any[]>(
      `/analytics/health-metrics/${userId}?start_date=${startDate}&end_date=${endDate}`
    )
    return response.data!
  },
}

// Notifications API
export const notificationsAPI = {
  getNotifications: async (page = 1, limit = 20): Promise<PaginatedResponse<any>> => {
    const response = await apiService.get<PaginatedResponse<any>>(
      `/notifications?page=${page}&limit=${limit}`
    )
    return response.data!
  },

  markAsRead: async (notificationId: string): Promise<void> => {
    await apiService.patch(`/notifications/${notificationId}/read`)
  },

  markAllAsRead: async (): Promise<void> => {
    await apiService.patch('/notifications/read-all')
  },

  deleteNotification: async (notificationId: string): Promise<void> => {
    await apiService.delete(`/notifications/${notificationId}`)
  },
}

// Health Check API
export const healthAPI = {
  checkHealth: async (): Promise<any> => {
    const response = await apiService.get<any>('/health')
    return response.data!
  },

  getSystemStatus: async (): Promise<any> => {
    const response = await apiService.get<any>('/health/status')
    return response.data!
  },
}

export default apiService
