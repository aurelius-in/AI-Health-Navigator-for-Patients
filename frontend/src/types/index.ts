// User Types
export interface User {
  id: string
  email: string
  firstName: string
  lastName: string
  dateOfBirth: string
  phone?: string
  emergencyContact?: EmergencyContact
  insurance?: InsuranceInfo
  preferences: UserPreferences
  createdAt: string
  updatedAt: string
}

export interface EmergencyContact {
  name: string
  relationship: string
  phone: string
  email?: string
}

export interface InsuranceInfo {
  provider: string
  memberId: string
  groupNumber?: string
  planType: string
  effectiveDate: string
  expirationDate?: string
}

export interface UserPreferences {
  notifications: {
    email: boolean
    sms: boolean
    push: boolean
  }
  privacy: {
    shareData: boolean
    allowResearch: boolean
  }
  accessibility: {
    highContrast: boolean
    largeText: boolean
    screenReader: boolean
  }
}

// Authentication Types
export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData extends LoginCredentials {
  firstName: string
  lastName: string
  dateOfBirth: string
  phone?: string
}

export interface AuthResponse {
  user: User
  token: string
  refreshToken: string
}

// Symptom Analysis Types
export interface SymptomRequest {
  symptoms: string[]
  severity: 'mild' | 'moderate' | 'severe'
  duration: string
  additionalInfo?: string
  images?: File[]
  location?: string
  triggers?: string[]
  medications?: string[]
  allergies?: string[]
}

export interface SymptomAnalysis {
  id: string
  userId: string
  symptoms: string[]
  severity: 'mild' | 'moderate' | 'severe'
  duration: string
  analysis: {
    possibleConditions: MedicalCondition[]
    confidence: number
    urgency: 'low' | 'medium' | 'high' | 'emergency'
    recommendations: string[]
    warnings: string[]
    nextSteps: string[]
  }
  aiInsights: {
    model: string
    confidence: number
    reasoning: string
  }
  createdAt: string
}

export interface MedicalCondition {
  icd10Code: string
  name: string
  description: string
  probability: number
  symptoms: string[]
  severity: 'mild' | 'moderate' | 'severe'
  requiresImmediateAttention: boolean
}

// Triage Assessment Types
export interface TriageRequest {
  symptoms: string[]
  vitalSigns?: VitalSigns
  painLevel: number
  consciousness: 'alert' | 'confused' | 'unresponsive'
  breathing: 'normal' | 'difficult' | 'labored'
  bleeding?: 'none' | 'minor' | 'moderate' | 'severe'
  trauma?: boolean
  pregnancy?: boolean
  age: number
}

export interface VitalSigns {
  temperature?: number
  heartRate?: number
  bloodPressure?: {
    systolic: number
    diastolic: number
  }
  oxygenSaturation?: number
  respiratoryRate?: number
}

export interface TriageAssessment {
  id: string
  userId: string
  urgency: 'immediate' | 'emergency' | 'urgent' | 'priority' | 'routine'
  estimatedWaitTime: string
  recommendedAction: string
  riskFactors: string[]
  vitalSignsStatus: 'normal' | 'concerning' | 'critical'
  aiAssessment: {
    confidence: number
    reasoning: string
    model: string
  }
  createdAt: string
}

// Provider Types
export interface HealthcareProvider {
  id: string
  name: string
  type: 'physician' | 'nurse' | 'specialist' | 'therapist' | 'pharmacist'
  specialty: string[]
  credentials: string[]
  location: ProviderLocation
  contact: ProviderContact
  availability: Availability[]
  insurance: string[]
  languages: string[]
  rating: number
  reviewCount: number
  verified: boolean
  acceptingPatients: boolean
}

export interface ProviderLocation {
  address: string
  city: string
  state: string
  zipCode: string
  coordinates?: {
    lat: number
    lng: number
  }
  distance?: number
}

export interface ProviderContact {
  phone: string
  email?: string
  website?: string
  fax?: string
}

export interface Availability {
  day: string
  startTime: string
  endTime: string
  available: boolean
}

// Insurance Types
export interface InsuranceProvider {
  id: string
  name: string
  type: 'private' | 'medicare' | 'medicaid' | 'tricare' | 'va'
  coverage: CoverageInfo
  network: NetworkInfo
  contact: InsuranceContact
}

export interface CoverageInfo {
  deductible: number
  copay: number
  coinsurance: number
  outOfPocketMax: number
  coveredServices: string[]
  exclusions: string[]
}

export interface NetworkInfo {
  inNetwork: boolean
  preferredProviders: string[]
  facilities: string[]
}

export interface InsuranceContact {
  phone: string
  website: string
  claimsAddress: string
}

// Health History Types
export interface HealthRecord {
  id: string
  userId: string
  type: 'symptom' | 'diagnosis' | 'medication' | 'procedure' | 'lab' | 'imaging'
  title: string
  description: string
  date: string
  provider?: string
  location?: string
  attachments?: File[]
  tags: string[]
  severity?: 'mild' | 'moderate' | 'severe'
  status: 'active' | 'resolved' | 'ongoing'
  notes?: string
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  message?: string
  timestamp: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
  hasNext: boolean
  hasPrev: boolean
}

// Error Types
export interface ApiError {
  code: string
  message: string
  details?: Record<string, any>
  timestamp: string
}

// Analytics Types
export interface AnalyticsEvent {
  event: string
  properties: Record<string, any>
  userId?: string
  sessionId: string
  timestamp: string
}

// Notification Types
export interface Notification {
  id: string
  type: 'info' | 'success' | 'warning' | 'error'
  title: string
  message: string
  read: boolean
  createdAt: string
  actionUrl?: string
}

// Search and Filter Types
export interface SearchFilters {
  location?: string
  specialty?: string[]
  insurance?: string[]
  availability?: string
  rating?: number
  distance?: number
  languages?: string[]
}

export interface SortOptions {
  field: string
  direction: 'asc' | 'desc'
}

// Form Types
export interface FormField {
  name: string
  label: string
  type: 'text' | 'email' | 'password' | 'select' | 'multiselect' | 'date' | 'number' | 'textarea' | 'file'
  required: boolean
  validation?: any
  options?: Array<{ value: string; label: string }>
  placeholder?: string
  helpText?: string
}

// Component Props Types
export interface BaseComponentProps {
  className?: string
  children?: React.ReactNode
}

export interface LoadingProps extends BaseComponentProps {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  color?: string
  text?: string
}

export interface ButtonProps extends BaseComponentProps {
  variant?: 'filled' | 'outline' | 'light' | 'white' | 'default' | 'subtle' | 'gradient'
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  loading?: boolean
  disabled?: boolean
  onClick?: () => void
  type?: 'button' | 'submit' | 'reset'
  fullWidth?: boolean
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
}

// Chart and Visualization Types
export interface ChartData {
  labels: string[]
  datasets: Array<{
    label: string
    data: number[]
    backgroundColor?: string | string[]
    borderColor?: string | string[]
    borderWidth?: number
  }>
}

export interface HealthMetrics {
  date: string
  value: number
  unit: string
  category: string
}

// File Upload Types
export interface FileUpload {
  id: string
  name: string
  size: number
  type: string
  url?: string
  progress?: number
  status: 'uploading' | 'completed' | 'error'
  error?: string
}

// Real-time Types
export interface ChatMessage {
  id: string
  sender: 'user' | 'ai' | 'provider'
  content: string
  timestamp: string
  attachments?: FileUpload[]
  metadata?: Record<string, any>
}

export interface WebSocketMessage {
  type: string
  payload: any
  timestamp: string
  sessionId: string
}
