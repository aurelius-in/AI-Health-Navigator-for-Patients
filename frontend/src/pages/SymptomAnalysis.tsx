/**
 * Symptom Analysis Page Component
 * 
 * This page provides advanced symptom analysis using the EnhancedSymptomAnalysisAgent
 * with memory integration, multi-modal reasoning, and autonomous decision-making.
 * Users can input symptoms and receive comprehensive AI-powered health assessments.
 */

import React, { useState } from 'react'
import { 
  Container, 
  Card, 
  Text, 
  TextInput, 
  Textarea, 
  Select, 
  Button, 
  Group, 
  Stack,
  Alert,
  Badge,
  Divider,
  List,
  Accordion,
  Progress,
  Modal,
  LoadingOverlay
} from '@mantine/core'
import { 
  IconBrain, 
  IconStethoscope, 
  IconAlertTriangle,
  IconCheck,
  IconX,
  IconInfo,
  IconClock,
  IconThermometer,
  IconHeart,
  IconBrain as IconMemory
} from '@tabler/icons-react'
import { api } from '@/services/api'

interface SymptomAnalysisResult {
  assessment: {
    primary_conditions: Array<{
      condition: string
      probability: number
      confidence: number
      reasoning: string
    }>
    urgency_level: 'immediate' | 'emergency' | 'urgent' | 'priority' | 'routine'
    risk_score: number
    recommended_actions: string[]
    safety_instructions: string[]
    follow_up_instructions: string[]
  }
  ai_insights: {
    memory_integration: string
    reasoning_chain: string[]
    confidence_factors: string[]
    learning_outcomes: string[]
  }
  metadata: {
    analysis_id: string
    timestamp: string
    processing_time: number
    agent_version: string
  }
}

const SymptomAnalysis: React.FC = () => {
  const [symptoms, setSymptoms] = useState('')
  const [severity, setSeverity] = useState<string | null>(null)
  const [duration, setDuration] = useState<string | null>(null)
  const [additionalContext, setAdditionalContext] = useState('')
  const [analysisResult, setAnalysisResult] = useState<SymptomAnalysisResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [showDetails, setShowDetails] = useState(false)

  const handleAnalysis = async () => {
    if (!symptoms.trim() || !severity || !duration) {
      return
    }

    setLoading(true)
    try {
      const response = await api.post('/api/v1/enhanced-agents/advanced-symptom-analysis', {
        symptoms: symptoms.split(',').map(s => s.trim()),
        severity: severity,
        duration: duration,
        additional_context: additionalContext,
        enable_memory_integration: true,
        enable_autonomous_decisions: true,
        enable_reasoning_chain: true,
        enable_learning: true
      })

      setAnalysisResult(response.data)
    } catch (error) {
      console.error('Symptom analysis failed:', error)
    } finally {
      setLoading(false)
    }
  }

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case 'immediate': return 'red'
      case 'emergency': return 'red'
      case 'urgent': return 'orange'
      case 'priority': return 'yellow'
      case 'routine': return 'blue'
      default: return 'gray'
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'severe': return 'red'
      case 'moderate': return 'yellow'
      case 'mild': return 'blue'
      default: return 'gray'
    }
  }

  return (
    <Container size="lg" py="xl">
      <Stack spacing="xl">
        {/* Header */}
        <div>
          <Text size="xl" weight={700} mb="xs">
            AI Symptom Analysis
          </Text>
          <Text color="dimmed">
            Get comprehensive health insights powered by advanced AI agents with memory and reasoning capabilities
          </Text>
        </div>

        {/* Input Form */}
        <Card shadow="sm" p="lg" radius="md" withBorder>
          <Stack spacing="md">
            <Text weight={500} size="lg">Describe Your Symptoms</Text>
            
            <TextInput
              label="Symptoms"
              placeholder="e.g., chest pain, headache, fever, shortness of breath"
              value={symptoms}
              onChange={(e) => setSymptoms(e.target.value)}
              required
              description="Separate multiple symptoms with commas"
            />

            <Group grow>
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

              <Select
                label="Duration"
                placeholder="How long?"
                value={duration}
                onChange={setDuration}
                data={[
                  { value: 'minutes', label: 'Minutes' },
                  { value: 'hours', label: 'Hours' },
                  { value: 'days', label: 'Days' },
                  { value: 'weeks', label: 'Weeks' },
                  { value: 'months', label: 'Months' }
                ]}
                required
              />
            </Group>

            <Textarea
              label="Additional Context (Optional)"
              placeholder="Any additional information that might be relevant..."
              value={additionalContext}
              onChange={(e) => setAdditionalContext(e.target.value)}
              minRows={3}
            />

            <Button 
              onClick={handleAnalysis}
              loading={loading}
              leftIcon={<IconBrain size={16} />}
              size="lg"
              disabled={!symptoms.trim() || !severity || !duration}
            >
              Analyze with Enhanced AI
            </Button>
          </Stack>
        </Card>

        {/* Analysis Results */}
        {analysisResult && (
          <Card shadow="sm" p="lg" radius="md" withBorder>
            <LoadingOverlay visible={loading} />
            
            <Stack spacing="lg">
              <Group position="apart">
                <Text weight={500} size="lg">Analysis Results</Text>
                <Badge 
                  color={getUrgencyColor(analysisResult.assessment.urgency_level)}
                  size="lg"
                >
                  {analysisResult.assessment.urgency_level.toUpperCase()}
                </Badge>
              </Group>

              {/* Risk Assessment */}
              <div>
                <Text weight={500} mb="xs">Risk Assessment</Text>
                <Progress 
                  value={analysisResult.assessment.risk_score * 100} 
                  color={getUrgencyColor(analysisResult.assessment.urgency_level)}
                  size="lg"
                  mb="xs"
                />
                <Text size="sm" color="dimmed">
                  Risk Score: {(analysisResult.assessment.risk_score * 100).toFixed(1)}%
                </Text>
              </div>

              {/* Primary Conditions */}
              <div>
                <Text weight={500} mb="xs">Possible Conditions</Text>
                <Stack spacing="xs">
                  {analysisResult.assessment.primary_conditions.map((condition, index) => (
                    <Card key={index} withBorder p="sm">
                      <Group position="apart">
                        <div>
                          <Text weight={500}>{condition.condition}</Text>
                          <Text size="sm" color="dimmed">{condition.reasoning}</Text>
                        </div>
                        <Badge color="blue">
                          {(condition.probability * 100).toFixed(1)}%
                        </Badge>
                      </Group>
                    </Card>
                  ))}
                </Stack>
              </div>

              {/* Recommended Actions */}
              <div>
                <Text weight={500} mb="xs">Recommended Actions</Text>
                <List spacing="xs">
                  {analysisResult.assessment.recommended_actions.map((action, index) => (
                    <List.Item key={index} icon={<IconCheck size={16} color="green" />}>
                      {action}
                    </List.Item>
                  ))}
                </List>
              </div>

              {/* Safety Instructions */}
              {analysisResult.assessment.safety_instructions.length > 0 && (
                <Alert icon={<IconAlertTriangle size={16} />} color="red">
                  <Text weight={500} mb="xs">Safety Instructions</Text>
                  <List spacing="xs">
                    {analysisResult.assessment.safety_instructions.map((instruction, index) => (
                      <List.Item key={index}>{instruction}</List.Item>
                    ))}
                  </List>
                </Alert>
              )}

              {/* AI Insights */}
              <Accordion>
                <Accordion.Item value="ai-insights">
                  <Accordion.Control>
                    <Group>
                      <IconMemory size={16} />
                      <Text>AI Agent Insights</Text>
                    </Group>
                  </Accordion.Control>
                  <Accordion.Panel>
                    <Stack spacing="md">
                      <div>
                        <Text weight={500} size="sm">Memory Integration</Text>
                        <Text size="sm" color="dimmed">{analysisResult.ai_insights.memory_integration}</Text>
                      </div>
                      
                      <div>
                        <Text weight={500} size="sm">Reasoning Chain</Text>
                        <List spacing="xs">
                          {analysisResult.ai_insights.reasoning_chain.map((step, index) => (
                            <List.Item key={index}>{step}</List.Item>
                          ))}
                        </List>
                      </div>
                      
                      <div>
                        <Text weight={500} size="sm">Learning Outcomes</Text>
                        <List spacing="xs">
                          {analysisResult.ai_insights.learning_outcomes.map((outcome, index) => (
                            <List.Item key={index}>{outcome}</List.Item>
                          ))}
                        </List>
                      </div>
                    </Stack>
                  </Accordion.Panel>
                </Accordion.Item>
              </Accordion>

              {/* Analysis Metadata */}
              <Divider />
              <Group position="apart" size="xs">
                <Text size="xs" color="dimmed">
                  Analysis ID: {analysisResult.metadata.analysis_id}
                </Text>
                <Text size="xs" color="dimmed">
                  Processing Time: {analysisResult.metadata.processing_time}ms
                </Text>
                <Text size="xs" color="dimmed">
                  Agent Version: {analysisResult.metadata.agent_version}
                </Text>
              </Group>
            </Stack>
          </Card>
        )}
      </Stack>
    </Container>
  )
}

export { SymptomAnalysis }
