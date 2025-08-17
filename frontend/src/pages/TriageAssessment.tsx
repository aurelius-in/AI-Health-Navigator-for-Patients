/**
 * Triage Assessment Page Component
 * 
 * This page provides emergency triage assessment using the EnhancedTriageAssessmentAgent.
 * It helps users determine the urgency of their symptoms and get appropriate guidance.
 */

import React from 'react'
import { Container, Text, Card, Stack } from '@mantine/core'

const TriageAssessment: React.FC = () => {
  return (
    <Container size="lg" py="xl">
      <Stack spacing="xl">
        <div>
          <Text size="xl" weight={700} mb="xs">
            Emergency Triage Assessment
          </Text>
          <Text color="dimmed">
            Get immediate guidance on symptom urgency and emergency care needs
          </Text>
        </div>

        <Card shadow="sm" p="lg" radius="md" withBorder>
          <Text>Emergency triage assessment functionality coming soon...</Text>
        </Card>
      </Stack>
    </Container>
  )
}

export { TriageAssessment }
