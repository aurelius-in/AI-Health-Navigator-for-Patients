import React from 'react'
import { Container, Text, Card, Stack } from '@mantine/core'

const HealthHistory: React.FC = () => {
  return (
    <Container size="lg" py="xl">
      <Stack spacing="xl">
        <div>
          <Text size="xl" weight={700} mb="xs">Health History</Text>
          <Text color="dimmed">View your complete health history and trends</Text>
        </div>
        <Card shadow="sm" p="lg" radius="md" withBorder>
          <Text>Health history functionality coming soon...</Text>
        </Card>
      </Stack>
    </Container>
  )
}

export { HealthHistory }
