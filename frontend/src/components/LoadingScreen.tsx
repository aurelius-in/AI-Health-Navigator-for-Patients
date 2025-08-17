import React from 'react'
import { Center, Loader, Text, Stack } from '@mantine/core'
import { IconHeartbeat } from '@tabler/icons-react'

interface LoadingScreenProps {
  message?: string
}

export const LoadingScreen: React.FC<LoadingScreenProps> = ({ 
  message = 'Loading AI Health Navigator...' 
}) => {
  return (
    <Center style={{ height: '100vh', width: '100vw' }}>
      <Stack align="center" spacing="lg">
        <IconHeartbeat size={48} color="#0ea5e9" />
        <Loader size="lg" color="blue" />
        <Text size="lg" c="dimmed">
          {message}
        </Text>
      </Stack>
    </Center>
  )
}
