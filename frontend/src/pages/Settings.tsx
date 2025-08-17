import React from 'react'
import { Container, Text, Card, Stack } from '@mantine/core'

const Settings: React.FC = () => {
  return (
    <Container size="lg" py="xl">
      <Stack spacing="xl">
        <div>
          <Text size="xl" weight={700} mb="xs">Settings</Text>
          <Text color="dimmed">Manage your account and preferences</Text>
        </div>
        <Card shadow="sm" p="lg" radius="md" withBorder>
          <Text>Settings functionality coming soon...</Text>
        </Card>
      </Stack>
    </Container>
  )
}

export { Settings }
