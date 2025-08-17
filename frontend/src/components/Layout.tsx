import React, { useState } from 'react'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import {
  AppShell,
  Navbar,
  Header,
  Footer,
  Text,
  MediaQuery,
  Burger,
  useMantineTheme,
  Group,
  Avatar,
  Menu,
  ActionIcon,
  Badge,
  Box,
  Divider,
  ScrollArea,
} from '@mantine/core'
import {
  IconDashboard,
  IconStethoscope,
  IconAlertTriangle,
  IconSearch,
  IconShield,
  IconHistory,
  IconSettings,
  IconLogout,
  IconUser,
  IconBell,
  IconMenu2,
  IconX,
} from '@tabler/icons-react'
import { useAuth } from '@/hooks/useAuth'
import { NavigationItem } from './NavigationItem'
import { NotificationsMenu } from './NotificationsMenu'
import { LoadingScreen } from './LoadingScreen'

const navigationItems = [
  {
    label: 'Dashboard',
    icon: IconDashboard,
    path: '/dashboard',
    description: 'Overview of your health',
  },
  {
    label: 'Symptom Analysis',
    icon: IconStethoscope,
    path: '/symptoms',
    description: 'Analyze your symptoms',
  },
  {
    label: 'Triage Assessment',
    icon: IconAlertTriangle,
    path: '/triage',
    description: 'Emergency assessment',
  },
  {
    label: 'Find Providers',
    icon: IconSearch,
    path: '/providers',
    description: 'Search healthcare providers',
  },
  {
    label: 'Insurance Guide',
    icon: IconShield,
    path: '/insurance',
    description: 'Insurance information',
  },
  {
    label: 'Health History',
    icon: IconHistory,
    path: '/history',
    description: 'Your medical records',
  },
  {
    label: 'Settings',
    icon: IconSettings,
    path: '/settings',
    description: 'Account settings',
  },
]

export const Layout: React.FC = () => {
  const theme = useMantineTheme()
  const [opened, setOpened] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  if (!user) {
    return <LoadingScreen />
  }

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const NavbarContent = () => (
    <Navbar.Section grow component={ScrollArea}>
      <Box p="md">
        <Text size="xs" tt="uppercase" fw={700} c="dimmed" mb="md">
          Navigation
        </Text>
        {navigationItems.map((item) => (
          <NavigationItem
            key={item.path}
            {...item}
            active={location.pathname === item.path}
            onClick={() => {
              navigate(item.path)
              setOpened(false)
            }}
          />
        ))}
      </Box>
    </Navbar.Section>

    <Divider />

    <Navbar.Section p="md">
      <Group>
        <Avatar
          src={user.profileImage}
          alt={`${user.firstName} ${user.lastName}`}
          radius="xl"
          size="md"
        >
          {user.firstName.charAt(0)}{user.lastName.charAt(0)}
        </Avatar>
        <Box style={{ flex: 1 }}>
          <Text size="sm" fw={500}>
            {user.firstName} {user.lastName}
          </Text>
          <Text size="xs" c="dimmed">
            {user.email}
          </Text>
        </Box>
      </Group>
    </Navbar.Section>
  )

  const HeaderContent = () => (
    <Header height={{ base: 50, md: 70 }} p="md">
      <Group justify="space-between" h="100%">
        <Group>
          <MediaQuery largerThan="sm" styles={{ display: 'none' }}>
            <Burger
              opened={opened}
              onClick={() => setOpened((o) => !o)}
              size="sm"
              color={theme.colors.gray[6]}
              mr="xl"
            />
          </MediaQuery>

          <Text
            size="lg"
            fw={700}
            variant="gradient"
            gradient={{ from: 'blue', to: 'cyan' }}
          >
            AI Health Navigator
          </Text>
        </Group>

        <Group>
          <NotificationsMenu />
          
          <Menu shadow="md" width={200}>
            <Menu.Target>
              <ActionIcon variant="subtle" size="lg">
                <IconUser size={20} />
              </ActionIcon>
            </Menu.Target>

            <Menu.Dropdown>
              <Menu.Label>Account</Menu.Label>
              <Menu.Item
                leftSection={<IconUser size={14} />}
                onClick={() => navigate('/settings')}
              >
                Profile Settings
              </Menu.Item>
              
              <Menu.Divider />
              
              <Menu.Label>Actions</Menu.Label>
              <Menu.Item
                color="red"
                leftSection={<IconLogout size={14} />}
                onClick={handleLogout}
              >
                Logout
              </Menu.Item>
            </Menu.Dropdown>
          </Menu>
        </Group>
      </Group>
    </Header>
  )

  return (
    <AppShell
      header={{ height: { base: 50, md: 70 } }}
      navbar={{
        width: { base: 200, md: 300 },
        breakpoint: 'sm',
        collapsed: { mobile: !opened },
      }}
      padding="md"
    >
      <AppShell.Header>
        <HeaderContent />
      </AppShell.Header>

      <AppShell.Navbar p="md">
        <NavbarContent />
      </AppShell.Navbar>

      <AppShell.Main>
        <Box
          style={{
            minHeight: 'calc(100vh - 140px)',
            background: theme.colorScheme === 'dark' ? theme.colors.dark[8] : theme.colors.gray[0],
          }}
        >
          <Outlet />
        </Box>
      </AppShell.Main>

      <AppShell.Footer p="md">
        <Group justify="space-between">
          <Text size="xs" c="dimmed">
            © 2024 AI Health Navigator. All rights reserved.
          </Text>
          <Group gap="xs">
            <Badge variant="light" size="xs">
              v1.0.0
            </Badge>
            <Badge variant="light" color="green" size="xs">
              HIPAA Compliant
            </Badge>
          </Group>
        </Group>
      </AppShell.Footer>
    </AppShell>
  )
}
