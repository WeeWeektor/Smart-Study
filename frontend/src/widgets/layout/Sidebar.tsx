import { Link, useLocation } from 'react-router-dom'
import {
  BookOpen,
  Calendar,
  ChevronLeft,
  ChevronRight,
  GraduationCap,
  Home,
  User,
} from 'lucide-react'
import { LogoutButton } from '@/features/logout'
import { getInitials, LANGUAGE_STORAGE_KEY, useI18n } from '@/shared/lib'
import { useEffect, useState } from 'react'

interface UserInfo {
  name: string
  surname: string
  email: string
  role: string
}

interface SidebarProps {
  userInfo: UserInfo
  isCollapsible?: boolean
  onCollapseChange?: (isCollapsed: boolean) => void
}

export const Sidebar = ({
  userInfo,
  isCollapsible = false,
  onCollapseChange,
}: SidebarProps) => {
  const location = useLocation()
  const { t } = useI18n()

  const [isCollapsed, setIsCollapsed] = useState(false)
  const [openCourseMenu, setOpenCourseMenu] = useState<string | null>(null)

  useEffect(() => {
    if (!isCollapsible) {
      setIsCollapsed(false)
      if (onCollapseChange) onCollapseChange(false)
    }
  }, [isCollapsible])

  const toggleSidebar = () => {
    if (!isCollapsible) return

    const newState = !isCollapsed
    setIsCollapsed(newState)

    if (newState) setOpenCourseMenu(null)

    if (onCollapseChange) onCollapseChange(newState)
  }

  const handleToggleMenu = (text: string) => {
    if (isCollapsed) {
      setIsCollapsed(false)
      setOpenCourseMenu(text)
      if (onCollapseChange) onCollapseChange(false)
    } else {
      setOpenCourseMenu(openCourseMenu === text ? null : text)
    }
  }

  const navLinks = [
    { to: '/dashboard/student', icon: Home, text: t('Головна') },
    {
      icon: BookOpen,
      text: t('Курси'),
      subItems: [
        { to: '/my-courses-subscriptions', text: t('Мої курси') },
        { to: '/find-new-courses', text: t('Знайти нові курси') },
        ...(userInfo.role === 'teacher'
          ? [{ to: '/my-created-courses', text: t('Мої створені курси') }]
          : []),
      ],
    },
    // { to: '/tests', icon: BarChart3, text: t('Тести') },
    { to: '/calendar/student', icon: Calendar, text: t('Календар') },
    { to: '/profile', icon: User, text: t('Профіль') },
  ]

  if (userInfo.role === 'admin') {
    navLinks.push({
      to: `https://localhost:8000/admin/?lang=${localStorage.getItem(LANGUAGE_STORAGE_KEY)}`,
      icon: Home,
      text: t('Адмін панель'),
    })
  }

  return (
    <div
      className={`fixed inset-y-0 left-0 z-50 bg-sidebar border-r border-sidebar-border transition-all duration-300 ease-in-out flex flex-col ${
        isCollapsed ? 'w-28' : 'w-64'
      }`}
    >
      <div className="h-16 flex items-center px-4 border-b border-sidebar-border shrink-0">
        <Link
          to="/"
          className="flex items-center gap-3 overflow-hidden flex-1 min-w-0"
        >
          <div className="w-8 h-8 bg-brand-600 dark:bg-brand-500 rounded-lg flex items-center justify-center shrink-0">
            <GraduationCap className="w-5 h-5 text-white" />
          </div>

          <span
            className={`text-xl font-bold text-foreground whitespace-nowrap transition-opacity duration-300 ${
              isCollapsed ? 'opacity-0 w-0 hidden' : 'opacity-100'
            }`}
          >
            Smart Study
          </span>
        </Link>

        {isCollapsible && (
          <button
            onClick={toggleSidebar}
            className="p-1.5 ml-auto rounded-lg hover:bg-muted text-muted-foreground transition-colors shrink-0"
          >
            {isCollapsed ? (
              <ChevronRight size={20} />
            ) : (
              <ChevronLeft size={20} />
            )}
          </button>
        )}
      </div>

      <nav className="flex-1 px-3 py-6 space-y-2 overflow-x-hidden overflow-y-auto">
        {navLinks.map((link, idx) => (
          <div key={idx}>
            {link.subItems ? (
              <div
                className={`flex items-center px-3 py-2 text-sm font-medium rounded-lg cursor-pointer transition-colors whitespace-nowrap ${
                  openCourseMenu === link.text
                    ? 'text-brand-600 dark:text-brand-400 bg-brand-50 dark:bg-brand-900'
                    : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                } ${isCollapsed ? 'justify-center' : ''}`}
                onClick={() => handleToggleMenu(link.text)}
                title={isCollapsed ? link.text : ''}
              >
                {link.icon && <link.icon className="w-5 h-5 shrink-0" />}

                <span
                  className={`ml-3 transition-all duration-300 ${
                    isCollapsed ? 'opacity-0 w-0 hidden' : 'opacity-100'
                  }`}
                >
                  {link.text}
                </span>

                {!isCollapsed && (
                  <span className="ml-auto text-xs opacity-60">
                    {openCourseMenu === link.text ? '▲' : '▼'}
                  </span>
                )}
              </div>
            ) : (
              <Link
                to={link.to!}
                className={`flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors whitespace-nowrap ${
                  location.pathname === link.to
                    ? 'text-brand-600 dark:text-brand-400 bg-brand-50 dark:bg-brand-900'
                    : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                } ${isCollapsed ? 'justify-center' : ''}`}
                title={isCollapsed ? link.text : ''}
              >
                {link.icon && <link.icon className="w-5 h-5 shrink-0" />}

                <span
                  className={`ml-3 transition-all duration-300 ${
                    isCollapsed ? 'opacity-0 w-0 hidden' : 'opacity-100'
                  }`}
                >
                  {link.text}
                </span>
              </Link>
            )}

            {link.subItems && openCourseMenu === link.text && !isCollapsed && (
              <ul className="mt-1 space-y-1 overflow-hidden">
                {link.subItems.map((sub, i) => (
                  <li key={i}>
                    <Link
                      to={sub.to}
                      className={`flex items-center pl-11 pr-3 py-2 text-sm rounded-lg transition-colors whitespace-nowrap ${
                        location.pathname === sub.to
                          ? 'text-brand-600 dark:text-brand-400 bg-brand-50 dark:bg-brand-900'
                          : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                      }`}
                    >
                      {sub.text}
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </nav>

      <div className="p-4 border-t border-sidebar-border shrink-0">
        <div
          className={`flex items-center ${isCollapsed ? 'justify-center' : ''}`}
        >
          <div className="w-10 h-10 bg-brand-100 dark:bg-brand-900 rounded-full flex items-center justify-center shrink-0">
            <span className="text-brand-600 dark:text-brand-400 font-semibold text-sm">
              {getInitials(userInfo.name, userInfo.surname)}
            </span>
          </div>

          <div
            className={`ml-3 overflow-hidden transition-all duration-300 ${
              isCollapsed ? 'w-0 opacity-0 hidden' : 'flex-1 opacity-100'
            }`}
          >
            <p
              className="text-sm font-medium text-foreground truncate"
              title={`${userInfo.name} ${userInfo.surname}`}
            >
              {userInfo.name} {userInfo.surname}
            </p>
            <p
              className="text-xs text-muted-foreground truncate"
              title={userInfo.email}
            >
              {userInfo.email}
            </p>
          </div>

          <div className={`shrink-0 ${isCollapsed ? 'hidden' : 'ml-auto'}`}>
            <LogoutButton />
          </div>
        </div>

        {isCollapsed && (
          <div className="mt-4 flex justify-center">
            <LogoutButton />
          </div>
        )}
      </div>
    </div>
  )
}
