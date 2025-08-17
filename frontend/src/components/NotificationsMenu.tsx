import React from 'react'
import { ActionIcon, Menu, Badge, Text, Group, Box } from '@mantine/core'
import { IconBell } from '@tabler/icons-react'

export const NotificationsMenu: React.FC = () => {
  // Mock notifications - in real app, this would come from API
  const notifications = [
    {
      id: '1',
      title: 'Appointment Reminder',
      message: 'Your appointment with Dr. Smith is tomorrow at 2:00 PM',
      type: 'info' as const,
      read: false,
      createdAt: '2024-01-15T10:00:00Z',
    },
    {
      id: '2',
      title: 'Test Results Available',
      message: 'Your blood test results are ready for review',
      type: 'success' as const,
      read: false,
      createdAt: '2024-01-14T15:30:00Z',
    },
  ]

  const unreadCount = notifications.filter(n => !n.read).length

  return (
    <Menu shadow="md" width={350} position="bottom-end">
      <Menu.Target>
        <ActionIcon variant="subtle" size="lg" pos="relative">
          <IconBell size={20} />
          {unreadCount > 0 && (
            <Badge
              size="xs"
              color="red"
              variant="filled"
              pos="absolute"
              top={-5}
              right={-5}
              style={{ minWidth: '18px', height: '18px', fontSize: '10px' }}
            >
              {unreadCount}
            </Badge>
          )}
        </ActionIcon>
      </Menu.Target>

      <Menu.Dropdown>
        <Menu.Label>
          <Group justify="space-between">
            <Text size="sm" fw={500}>
              Notifications
            </Text>
            {unreadCount > 0 && (
              <Badge size="xs" color="blue">
                {unreadCount} new
              </Badge>
            )}
          </Group>
        </Menu.Label>

        {notifications.length === 0 ? (
          <Menu.Item disabled>
            <Text size="sm" c="dimmed" ta="center" py="md">
              No notifications
            </Text>
          </Menu.Item>
        ) : (
          notifications.map((notification) => (
            <Menu.Item key={notification.id}>
              <Box>
                <Text size="sm" fw={500} mb={4}>
                  {notification.title}
                </Text>
                <Text size="xs" c="dimmed" lineClamp={2}>
                  {notification.message}
                </Text>
                <Text size="xs" c="dimmed" mt={4}>
                  {new Date(notification.createdAt).toLocaleDateString()}
                </Text>
              </Box>
            </Menu.Item>
          ))
        )}

        {notifications.length > 0 && (
          <>
            <Menu.Divider />
            <Menu.Item>
              <Text size="sm" ta="center">
                View all notifications
              </Text>
            </Menu.Item>
          </>
        )}
      </Menu.Dropdown>
    </Menu>
  )
}
