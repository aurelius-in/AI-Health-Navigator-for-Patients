import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { MantineProvider } from '@mantine/core'
import { Notifications } from '@mantine/notifications'
import { HelmetProvider } from 'react-helmet-async'
import { ErrorBoundary } from 'react-error-boundary'
import { Toaster } from 'react-hot-toast'

import App from './App'
import { theme } from './styles/theme'
import { ErrorFallback } from './components/ErrorFallback'
import { AuthProvider } from './contexts/AuthContext'
import { AnalyticsProvider } from './contexts/AnalyticsContext'

import './styles/globals.css'

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
    mutations: {
      retry: 1,
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ErrorBoundary FallbackComponent={ErrorFallback}>
      <HelmetProvider>
        <QueryClientProvider client={queryClient}>
          <MantineProvider theme={theme} withGlobalStyles withNormalizeCSS>
            <Notifications position="top-right" />
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: '#363636',
                  color: '#fff',
                },
              }}
            />
            <BrowserRouter>
              <AuthProvider>
                <AnalyticsProvider>
                  <App />
                </AnalyticsProvider>
              </AuthProvider>
            </BrowserRouter>
          </MantineProvider>
          <ReactQueryDevtools initialIsOpen={false} />
        </QueryClientProvider>
      </HelmetProvider>
    </ErrorBoundary>
  </React.StrictMode>,
)
