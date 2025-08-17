import React from 'react'
import { Container, Text, Card, Stack } from '@mantine/core'

const ProviderSearch: React.FC = () => {
  return (
    <Container size="lg" py="xl">
      <Stack spacing="xl">
        <div>
          <Text size="xl" weight={700} mb="xs">Find Healthcare Providers</Text>
          <Text color="dimmed">Search for healthcare providers in your area</Text>
        </div>
        <Card shadow="sm" p="lg" radius="md" withBorder>
          <Text>Provider search functionality coming soon...</Text>
        </Card>
      </Stack>
    </Container>
  )
}

export { ProviderSearch }
