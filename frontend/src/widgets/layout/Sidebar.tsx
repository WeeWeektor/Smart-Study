import { Link, useLocation } from 'react-router-dom'
import {
  BarChart3,
  BookOpen,
  Calendar,
  GraduationCap,
  Home,
  User,
} from 'lucide-react'
import { LogoutButton } from '@/features/logout'
import { getInitials, LANGUAGE_STORAGE_KEY, useI18n } from '@/shared/lib'
import { useState } from 'react'

interface UserInfo {
  name: string
  surname: string
  email: string
  role: string
}

interface SidebarProps {
  userInfo: UserInfo
}

export const Sidebar = ({ userInfo }: SidebarProps) => {
  const location = useLocation()
  const { t } = useI18n()
  const [openCourseMenu, setOpenCourseMenu] = useState<string | null>(null)

  const navLinks = [
    { to: '/dashboard/student', icon: Home, text: t('Головна') },
    {
      icon: BookOpen,
      text: t('Курси'),
      subItems: [
        { to: '/catalog-my-courses', text: t('Мої курси') },
        { to: '/find-new-courses', text: t('Знайти нові курси') },
        ...(userInfo.role === 'teacher'
          ? [
              {
                to: '/catalog-my-created-courses',
                text: t('Мої створені курси'),
              },
            ]
          : []),
      ],
    },
    { to: '/tests', icon: BarChart3, text: t('Тести') },
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

  const handleToggle = (text: string) => {
    setOpenCourseMenu(openCourseMenu === text ? null : text)
  }

  return (
    <div className="fixed inset-y-0 left-0 z-50 w-64 bg-sidebar border-r border-sidebar-border">
      <div className="flex flex-col h-full">
        {/* Logo */}
        <div className="flex items-center px-6 py-4 border-b border-sidebar-border">
          <Link to="/" className="m-0 p-0 flex items-center">
            <div className="w-8 h-8 bg-brand-600 dark:bg-brand-500 rounded-lg flex items-center justify-center">
              <GraduationCap className="w-5 h-5 text-white" />
            </div>
            <span className="ml-2 text-xl font-bold text-foreground">
              Smart Study
            </span>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-2">
          {navLinks.map((link, idx) => (
            <div key={idx}>
              {link.subItems ? (
                <div
                  className={`flex items-center px-3 py-2 text-sm font-medium rounded-lg cursor-pointer ${
                    openCourseMenu === link.text
                      ? 'text-brand-600 dark:text-brand-400 bg-brand-50 dark:bg-brand-900'
                      : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                  }`}
                  onClick={() => handleToggle(link.text)}
                >
                  {link.icon && <link.icon className="w-5 h-5 mr-3" />}
                  {link.text}
                  <span className="ml-auto">
                    {openCourseMenu === link.text ? '▲' : '▼'}
                  </span>
                </div>
              ) : (
                <Link
                  to={link.to!}
                  className={`flex items-center px-3 py-2 text-sm font-medium rounded-lg ${
                    location.pathname === link.to
                      ? 'text-brand-600 dark:text-brand-400 bg-brand-50 dark:bg-brand-900'
                      : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                  }`}
                >
                  {link.icon && <link.icon className="w-5 h-5 mr-3" />}
                  {link.text}
                </Link>
              )}

              {/* Підменю */}
              {link.subItems && openCourseMenu === link.text && (
                <ul className="pl-6 mt-1 space-y-1">
                  {link.subItems.map((sub, i) => (
                    <li key={i}>
                      <Link
                        to={sub.to}
                        className={`flex items-center px-3 py-2 text-sm rounded-lg ${
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

        {/* User menu */}
        <div className="p-4 border-t border-sidebar-border">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-brand-100 dark:bg-brand-900 rounded-full flex items-center justify-center">
              <span className="text-brand-600 dark:text-brand-400 font-semibold">
                {getInitials(userInfo.name, userInfo.surname)}
              </span>
            </div>
            <div className="ml-3 flex-1">
              <p
                className="text-sm font-medium text-foreground truncate max-w-[140px] overflow-hidden whitespace-nowrap"
                title={`${userInfo.name} ${userInfo.surname}`}
              >
                {userInfo.name} {userInfo.surname}
              </p>
              <p className="text-xs text-muted-foreground">{userInfo.email}</p>
            </div>
            <LogoutButton />
          </div>
        </div>
      </div>
    </div>
  )
}
