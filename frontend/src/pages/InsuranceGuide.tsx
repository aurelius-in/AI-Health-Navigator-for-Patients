import React from 'react'
import { Container, Text, Card, Stack } from '@mantine/core'

const InsuranceGuide: React.FC = () => {
  return (
    <Container size="lg" py="xl">
      <Stack spacing="xl">
        <div>
          <Text size="xl" weight={700} mb="xs">Insurance & Cost Guide</Text>
          <Text color="dimmed">Understand your coverage and estimate healthcare costs</Text>
        </div>
        <Card shadow="sm" p="lg" radius="md" withBorder>
          <Text>Insurance guide functionality coming soon...</Text>
        </Card>
      </Stack>
    </Container>
  )
}

export { InsuranceGuide }
