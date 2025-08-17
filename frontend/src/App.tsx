import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { Layout } from '@/components/Layout'
import { LoadingScreen } from '@/components/LoadingScreen'

// Pages
import { Dashboard } from '@/pages/Dashboard'
import { SymptomAnalysis } from '@/pages/SymptomAnalysis'
import { TriageAssessment } from '@/pages/TriageAssessment'
import { ProviderSearch } from '@/pages/ProviderSearch'
import { InsuranceGuide } from '@/pages/InsuranceGuide'
import { HealthHistory } from '@/pages/HealthHistory'
import { Settings } from '@/pages/Settings'
import { Login } from '@/pages/Login'
import { Register } from '@/pages/Register'
import { NotFound } from '@/pages/NotFound'

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth()

  if (loading) {
    return <LoadingScreen />
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

// Public Route Component (redirects if already authenticated)
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth()

  if (loading) {
    return <LoadingScreen />
  }

  if (user) {
    return <Navigate to="/dashboard" replace />
  }

  return <>{children}</>
}

const App: React.FC = () => {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/login" element={
        <PublicRoute>
          <Login />
        </PublicRoute>
      } />
      <Route path="/register" element={
        <PublicRoute>
          <Register />
        </PublicRoute>
      } />

      {/* Protected Routes */}
      <Route path="/" element={
        <ProtectedRoute>
          <Layout />
        </ProtectedRoute>
      }>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="symptoms" element={<SymptomAnalysis />} />
        <Route path="triage" element={<TriageAssessment />} />
        <Route path="providers" element={<ProviderSearch />} />
        <Route path="insurance" element={<InsuranceGuide />} />
        <Route path="history" element={<HealthHistory />} />
        <Route path="settings" element={<Settings />} />
      </Route>

      {/* 404 Route */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}

export default App
