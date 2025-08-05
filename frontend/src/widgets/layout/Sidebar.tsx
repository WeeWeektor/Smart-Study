import { Link, useLocation } from 'react-router-dom'
import { ThemeToggle } from '@/shared/ui'
import {
  GraduationCap,
  BookOpen,
  BarChart3,
  User,
  Home,
  Calendar,
} from 'lucide-react'
import { LogoutButton } from '@/features/logout'
import { getInitials } from '@/shared/lib'

interface UserInfo {
  name: string
  surname: string
  email: string
  is_admin: string
}

interface SidebarProps {
  userInfo: UserInfo
}

export const Sidebar = ({ userInfo }: SidebarProps) => {
  const location = useLocation()

  const navLinks = [
    { to: '/dashboard/student', icon: Home, text: 'Головна' },
    { to: '/courses', icon: BookOpen, text: 'Курси' },
    { to: '/tests', icon: BarChart3, text: 'Тести' },
    { to: '/calendar/student', icon: Calendar, text: 'Календар' },
    { to: '/profile', icon: User, text: 'Профіль' },
  ]

  if (userInfo.is_admin === 'admin') {
    navLinks.push({
      to: 'https://127.0.0.1:5173/admin',
      icon: Home,
      text: 'Адмін панель',
    })
  }

  return (
    <div className="fixed inset-y-0 left-0 z-50 w-64 bg-sidebar border-r border-border dark:bg-sidebar dark:border-border">
      <div className="flex flex-col h-full">
        {/* Logo */}
        <div className="flex items-center px-6 py-4 border-b border-border">
          <Link to="/" className="m-0 p-0 flex items-center">
            <div className="w-8 h-8 bg-brand-600 rounded-lg flex items-center justify-center">
              <GraduationCap className="w-5 h-5 text-white" />
            </div>
            <span className="ml-2 text-xl font-bold text-sidebar-foreground dark:text-sidebar-foreground">
              Smart Study
            </span>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-2">
          {navLinks.map(link => (
            <Link
              key={link.to}
              to={link.to}
              className={`flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors duration-150
                ${
                  location.pathname === link.to
                    ? 'text-brand-600 bg-brand-50 dark:bg-brand-900 dark:text-brand-400'
                    : 'text-sidebar-foreground hover:text-foreground hover:bg-muted dark:hover:bg-muted dark:text-sidebar-foreground dark:hover:text-foreground'
                }
              `}
            >
              <link.icon className="w-5 h-5 mr-3" />
              {link.text}
            </Link>
          ))}
        </nav>

        {/* User menu */}
        <div className="p-4 border-t border-border">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-brand-100 dark:bg-brand-900 rounded-full flex items-center justify-center">
              <span className="text-brand-600 dark:text-brand-400 font-semibold">
                {getInitials(userInfo.name, userInfo.surname)}
              </span>
            </div>
            <div className="ml-3 flex-1">
              <p
                className="text-sm font-medium text-sidebar-foreground dark:text-sidebar-foreground truncate max-w-[140px] overflow-hidden whitespace-nowrap"
                title={`${userInfo.name} ${userInfo.surname}`}
              >
                {userInfo.name} {userInfo.surname}
              </p>
              <p className="text-xs text-muted-foreground">{userInfo.email}</p>
            </div>
            <LogoutButton />
          </div>
          <ThemeToggle />
        </div>
      </div>
    </div>
  )
}
