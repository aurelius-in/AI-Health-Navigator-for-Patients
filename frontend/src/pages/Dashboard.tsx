/**
 * Dashboard Page Component
 * 
 * This is the main landing page for authenticated users, providing an overview
 * of their health status, recent activities, and quick access to key features.
 * It integrates with the enhanced agentic AI system to provide personalized
 * health insights and recommendations.
 */

import React, { useState, useEffect } from 'react'
import { 
  Container, 
  Grid, 
  Card, 
  Text, 
  Group, 
  Badge, 
  Button, 
  Stack,
  Progress,
  Alert,
  Timeline,
  Avatar,
  ActionIcon,
  Modal,
  TextInput,
  Textarea,
  Select
} from '@mantine/core'
import { 
  IconActivity, 
  IconHeart, 
  IconStethoscope, 
  IconAlertTriangle,
  IconPlus,
  IconMessage,
  IconBrain,
  IconChartLine,
  IconCalendar,
  IconBell
} from '@tabler/icons-react'
import { useAuth } from '@/hooks/useAuth'
import { api } from '@/services/api'

interface HealthSummary {
  overall_health_score: number
  recent_symptoms: string[]
  upcoming_appointments: any[]
  medication_reminders: any[]
  health_alerts: any[]
  ai_recommendations: any[]
}

interface AgentInsight {
  agent_type: string
  insight: string
  confidence: number
  timestamp: string
  priority: 'low' | 'medium' | 'high'
}

const Dashboard: React.FC = () => {
  const { user } = useAuth()
  const [healthSummary, setHealthSummary] = useState<HealthSummary | null>(null)
  const [agentInsights, setAgentInsights] = useState<AgentInsight[]>([])
  const [loading, setLoading] = useState(true)
  const [symptomModalOpen, setSymptomModalOpen] = useState(false)
  const [symptomInput, setSymptomInput] = useState('')
  const [severity, setSeverity] = useState<string | null>(null)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      
      // Load health summary
      const summaryResponse = await api.get('/api/v1/health/summary')
      setHealthSummary(summaryResponse.data)
      
      // Load AI agent insights
      const insightsResponse = await api.get('/api/v1/enhanced-agents/insights')
      setAgentInsights(insightsResponse.data.insights || [])
      
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSymptomAnalysis = async () => {
    if (!symptomInput.trim() || !severity) return

    try {
      const response = await api.post('/api/v1/enhanced-agents/advanced-symptom-analysis', {
        symptoms: [symptomInput],
        severity: severity,
        duration: 'recent',
        enable_memory_integration: true,
        enable_autonomous_decisions: true
      })

      // Refresh dashboard data
      await loadDashboardData()
      setSymptomModalOpen(false)
      setSymptomInput('')
      setSeverity(null)
      
    } catch (error) {
      console.error('Symptom analysis failed:', error)
    }
  }

  const getHealthScoreColor = (score: number) => {
    if (score >= 80) return 'green'
    if (score >= 60) return 'yellow'
    return 'red'
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'red'
      case 'medium': return 'yellow'
      case 'low': return 'blue'
      default: return 'gray'
    }
  }

  if (loading) {
    return (
      <Container size="xl" py="xl">
        <Text>Loading dashboard...</Text>
      </Container>
    )
  }

  return (
    <Container size="xl" py="xl">
      {/* Welcome Header */}
      <Group position="apart" mb="xl">
        <div>
          <Text size="xl" weight={700}>
            Welcome back, {user?.first_name}!
          </Text>
          <Text color="dimmed" size="sm">
            Here's your personalized health overview powered by AI
          </Text>
        </div>
        <Button 
          leftIcon={<IconPlus size={16} />}
          onClick={() => setSymptomModalOpen(true)}
        >
          Report Symptom
        </Button>
      </Group>

      <Grid gutter="md">
        {/* Health Score Card */}
        <Grid.Col span={12} md={4}>
          <Card shadow="sm" p="lg" radius="md" withBorder>
            <Group position="apart" mb="md">
              <Text weight={500}>Overall Health Score</Text>
              <IconHeart size={20} color={getHealthScoreColor(healthSummary?.overall_health_score || 0)} />
            </Group>
            
            <Progress 
              value={healthSummary?.overall_health_score || 0} 
              color={getHealthScoreColor(healthSummary?.overall_health_score || 0)}
              size="xl"
              mb="md"
            />
            
            <Text size="lg" weight={700} align="center">
              {healthSummary?.overall_health_score || 0}/100
            </Text>
            
            <Text size="sm" color="dimmed" align="center" mt="xs">
              Based on your recent health data and AI analysis
            </Text>
          </Card>
        </Grid.Col>

        {/* AI Agent Insights */}
        <Grid.Col span={12} md={8}>
          <Card shadow="sm" p="lg" radius="md" withBorder>
            <Group position="apart" mb="md">
              <Text weight={500}>AI Health Insights</Text>
              <IconBrain size={20} />
            </Group>
            
            <Stack spacing="sm">
              {agentInsights.slice(0, 3).map((insight, index) => (
                <Alert 
                  key={index}
                  color={getPriorityColor(insight.priority)}
                  icon={<IconMessage size={16} />}
                >
                  <Group position="apart">
                    <div>
                      <Text size="sm" weight={500}>
                        {insight.agent_type.replace('_', ' ').toUpperCase()}
                      </Text>
                      <Text size="xs">{insight.insight}</Text>
                    </div>
                    <Badge 
                      color={getPriorityColor(insight.priority)}
                      variant="light"
                    >
                      {insight.priority}
                    </Badge>
                  </Group>
                </Alert>
              ))}
              
              {agentInsights.length === 0 && (
                <Text color="dimmed" size="sm" align="center">
                  No AI insights available. Report symptoms to get personalized recommendations.
                </Text>
              )}
            </Stack>
          </Card>
        </Grid.Col>

        {/* Recent Activity */}
        <Grid.Col span={12} md={6}>
          <Card shadow="sm" p="lg" radius="md" withBorder>
            <Group position="apart" mb="md">
              <Text weight={500}>Recent Activity</Text>
              <IconActivity size={20} />
            </Group>
            
            <Timeline active={1} bulletSize={24} lineWidth={2}>
              <Timeline.Item 
                bullet={<IconStethoscope size={12} />} 
                title="Symptom Analysis"
              >
                <Text color="dimmed" size="sm">AI analyzed your symptoms</Text>
                <Text size="xs" mt={4}>2 hours ago</Text>
              </Timeline.Item>
              
              <Timeline.Item 
                bullet={<IconCalendar size={12} />} 
                title="Appointment Scheduled"
              >
                <Text color="dimmed" size="sm">Follow-up with Dr. Smith</Text>
                <Text size="xs" mt={4}>Yesterday</Text>
              </Timeline.Item>
              
              <Timeline.Item 
                bullet={<IconBell size={12} />} 
                title="Medication Reminder"
              >
                <Text color="dimmed" size="sm">Time to take your medication</Text>
                <Text size="xs" mt={4}>3 days ago</Text>
              </Timeline.Item>
            </Timeline>
          </Card>
        </Grid.Col>

        {/* Quick Actions */}
        <Grid.Col span={12} md={6}>
          <Card shadow="sm" p="lg" radius="md" withBorder>
            <Text weight={500} mb="md">Quick Actions</Text>
            
            <Stack spacing="sm">
              <Button 
                variant="light" 
                leftIcon={<IconStethoscope size={16} />}
                onClick={() => window.location.href = '/symptoms'}
              >
                Symptom Analysis
              </Button>
              
              <Button 
                variant="light" 
                leftIcon={<IconAlertTriangle size={16} />}
                onClick={() => window.location.href = '/triage'}
              >
                Emergency Triage
              </Button>
              
              <Button 
                variant="light" 
                leftIcon={<IconChartLine size={16} />}
                onClick={() => window.location.href = '/history'}
              >
                Health History
              </Button>
              
              <Button 
                variant="light" 
                leftIcon={<IconCalendar size={16} />}
                onClick={() => window.location.href = '/providers'}
              >
                Find Provider
              </Button>
            </Stack>
          </Card>
        </Grid.Col>
      </Grid>

      {/* Symptom Analysis Modal */}
      <Modal
        opened={symptomModalOpen}
        onClose={() => setSymptomModalOpen(false)}
        title="Report New Symptom"
        size="md"
      >
        <Stack spacing="md">
          <TextInput
            label="Describe your symptoms"
            placeholder="e.g., chest pain, headache, fever..."
            value={symptomInput}
            onChange={(e) => setSymptomInput(e.target.value)}
            required
          />
          
          <Select
            label="Severity Level"
            placeholder="Select severity"
            value={severity}
            onChange={setSeverity}
            data={[
              { value: 'mild', label: 'Mild' },
              { value: 'moderate', label: 'Moderate' },
              { value: 'severe', label: 'Severe' }
            ]}
            required
          />
          
          <Group position="apart" mt="md">
            <Button variant="outline" onClick={() => setSymptomModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSymptomAnalysis}>
              Analyze with AI
            </Button>
          </Group>
        </Stack>
      </Modal>
    </Container>
  )
}

export { Dashboard }
