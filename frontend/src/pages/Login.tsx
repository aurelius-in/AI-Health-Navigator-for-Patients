/**
 * Login Page Component
 * 
 * This page handles user authentication with the AI Health Navigator system.
 * It provides a secure login form with proper validation and error handling.
 */

import React, { useState } from 'react'
import { 
  Container, 
  Card, 
  Text, 
  TextInput, 
  PasswordInput, 
  Button, 
  Group, 
  Stack,
  Alert,
  Anchor,
  Divider
} from '@mantine/core'
import { IconBrain, IconAlertCircle } from '@tabler/icons-react'
import { useAuth } from '@/hooks/useAuth'
import { useNavigate, Link } from 'react-router-dom'

const Login: React.FC = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      await login(email, password)
      navigate('/dashboard')
    } catch (err: any) {
      setError(err.message || 'Login failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container size="xs" py="xl">
      <Stack spacing="xl" align="center">
        {/* Header */}
        <div style={{ textAlign: 'center' }}>
          <IconBrain size={48} color="#228be6" />
          <Text size="xl" weight={700} mt="md">
            AI Health Navigator
          </Text>
          <Text color="dimmed" size="sm">
            Sign in to access your personalized health insights
          </Text>
        </div>

        {/* Login Form */}
        <Card shadow="sm" p="xl" radius="md" withBorder style={{ width: '100%' }}>
          <form onSubmit={handleSubmit}>
            <Stack spacing="md">
              {error && (
                <Alert icon={<IconAlertCircle size={16} />} color="red">
                  {error}
                </Alert>
              )}

              <TextInput
                label="Email"
                placeholder="your@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                type="email"
              />

              <PasswordInput
                label="Password"
                placeholder="Your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />

              <Button 
                type="submit" 
                loading={loading}
                size="lg"
                fullWidth
              >
                Sign In
              </Button>
            </Stack>
          </form>

          <Divider my="md" label="or" labelPosition="center" />

          <Group position="center">
            <Text size="sm" color="dimmed">
              Don't have an account?{' '}
              <Anchor component={Link} to="/register" size="sm">
                Sign up
              </Anchor>
            </Text>
          </Group>
        </Card>
      </Stack>
    </Container>
  )
}

export { Login }
