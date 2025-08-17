import { MantineThemeOverride } from '@mantine/core'

export const theme: MantineThemeOverride = {
  colorScheme: 'light',
  primaryColor: 'blue',
  colors: {
    // Custom healthcare-themed colors
    health: [
      '#f0f9ff', // 0 - Light blue background
      '#e0f2fe', // 1 - Very light blue
      '#bae6fd', // 2 - Light blue
      '#7dd3fc', // 3 - Medium light blue
      '#38bdf8', // 4 - Medium blue
      '#0ea5e9', // 5 - Primary blue
      '#0284c7', // 6 - Dark blue
      '#0369a1', // 7 - Darker blue
      '#075985', // 8 - Very dark blue
      '#0c4a6e', // 9 - Darkest blue
    ],
    medical: [
      '#fef2f2', // 0 - Light red background
      '#fee2e2', // 1 - Very light red
      '#fecaca', // 2 - Light red
      '#fca5a5', // 3 - Medium light red
      '#f87171', // 4 - Medium red
      '#ef4444', // 5 - Primary red
      '#dc2626', // 6 - Dark red
      '#b91c1c', // 7 - Darker red
      '#991b1b', // 8 - Very dark red
      '#7f1d1d', // 9 - Darkest red
    ],
    wellness: [
      '#f0fdf4', // 0 - Light green background
      '#dcfce7', // 1 - Very light green
      '#bbf7d0', // 2 - Light green
      '#86efac', // 3 - Medium light green
      '#4ade80', // 4 - Medium green
      '#22c55e', // 5 - Primary green
      '#16a34a', // 6 - Dark green
      '#15803d', // 7 - Darker green
      '#166534', // 8 - Very dark green
      '#14532d', // 9 - Darkest green
    ],
  },
  fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif',
  fontFamilyMonospace: 'JetBrains Mono, Monaco, Consolas, monospace',
  headings: {
    fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif',
    fontWeight: 600,
    sizes: {
      h1: { fontSize: '2.5rem', lineHeight: 1.2 },
      h2: { fontSize: '2rem', lineHeight: 1.3 },
      h3: { fontSize: '1.5rem', lineHeight: 1.4 },
      h4: { fontSize: '1.25rem', lineHeight: 1.4 },
      h5: { fontSize: '1.125rem', lineHeight: 1.4 },
      h6: { fontSize: '1rem', lineHeight: 1.4 },
    },
  },
  spacing: {
    xs: '0.5rem',
    sm: '0.75rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
  },
  radius: {
    xs: '0.25rem',
    sm: '0.375rem',
    md: '0.5rem',
    lg: '0.75rem',
    xl: '1rem',
  },
  shadows: {
    xs: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    sm: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  },
  breakpoints: {
    xs: '36em',
    sm: '48em',
    md: '62em',
    lg: '75em',
    xl: '88em',
  },
  components: {
    Button: {
      defaultProps: {
        size: 'md',
        radius: 'md',
      },
      styles: (theme) => ({
        root: {
          fontWeight: 500,
          transition: 'all 0.2s ease',
        },
      }),
    },
    Card: {
      defaultProps: {
        radius: 'md',
        withBorder: true,
      },
      styles: (theme) => ({
        root: {
          backgroundColor: theme.colorScheme === 'dark' ? theme.colors.dark[7] : theme.white,
          borderColor: theme.colorScheme === 'dark' ? theme.colors.dark[4] : theme.colors.gray[3],
        },
      }),
    },
    Input: {
      defaultProps: {
        radius: 'md',
      },
    },
    Select: {
      defaultProps: {
        radius: 'md',
      },
    },
    Textarea: {
      defaultProps: {
        radius: 'md',
      },
    },
    Modal: {
      defaultProps: {
        radius: 'lg',
        padding: 'lg',
      },
    },
    Notification: {
      defaultProps: {
        radius: 'md',
      },
    },
    Alert: {
      defaultProps: {
        radius: 'md',
      },
    },
  },
  other: {
    // Custom properties for healthcare-specific styling
    healthColors: {
      primary: '#0ea5e9',
      secondary: '#22c55e',
      warning: '#f59e0b',
      danger: '#ef4444',
      info: '#3b82f6',
      success: '#10b981',
    },
    gradients: {
      primary: { from: '#0ea5e9', to: '#3b82f6' },
      secondary: { from: '#22c55e', to: '#10b981' },
      warning: { from: '#f59e0b', to: '#f97316' },
      danger: { from: '#ef4444', to: '#dc2626' },
    },
  },
}
