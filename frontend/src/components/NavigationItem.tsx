import React from 'react'
import { UnstyledButton, Group, Text, useMantineTheme } from '@mantine/core'
import { IconProps } from '@tabler/icons-react'

interface NavigationItemProps {
  label: string
  icon: React.ComponentType<IconProps>
  path: string
  description: string
  active: boolean
  onClick: () => void
}

export const NavigationItem: React.FC<NavigationItemProps> = ({
  label,
  icon: Icon,
  description,
  active,
  onClick,
}) => {
  const theme = useMantineTheme()

  return (
    <UnstyledButton
      onClick={onClick}
      sx={(theme) => ({
        display: 'block',
        width: '100%',
        padding: theme.spacing.xs,
        borderRadius: theme.radius.sm,
        color: active ? theme.white : theme.colorScheme === 'dark' ? theme.colors.dark[0] : theme.black,
        backgroundColor: active ? theme.colors.blue[6] : 'transparent',
        '&:hover': {
          backgroundColor: active 
            ? theme.colors.blue[7] 
            : theme.colorScheme === 'dark' ? theme.colors.dark[6] : theme.colors.gray[0],
        },
        transition: 'all 0.2s ease',
      })}
    >
      <Group>
        <Icon size={20} stroke={1.5} />
        <Box style={{ flex: 1 }}>
          <Text size="sm" fw={500}>
            {label}
          </Text>
          <Text size="xs" c="dimmed" lineClamp={1}>
            {description}
          </Text>
        </Box>
      </Group>
    </UnstyledButton>
  )
}
