import { Link } from 'react-router-dom'
import { GraduationCap } from 'lucide-react'
import * as React from 'react'
import { ThemeToggle } from '@/shared/ui/theme-toggle'

interface AuthLayoutProps {
  headerContent?: React.ReactNode
  children: React.ReactNode
}

export const AuthLayout = ({ headerContent, children }: AuthLayoutProps) => {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/80 dark:bg-card/60 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link to="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-brand-600 dark:bg-brand-500 rounded-lg flex items-center justify-center">
                <GraduationCap className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-foreground">
                Smart Study
              </span>
            </Link>

            <div className="flex items-center space-x-3">
              {headerContent}
              <ThemeToggle variant="default" size="default" />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <div className="w-full space-y-8">{children}</div>
      </div>

      {/* Background Decoration */}
      <div className="fixed top-0 right-0 -translate-y-12 translate-x-12 w-96 h-96 bg-gradient-to-br from-brand-200 to-smartblue-200 dark:from-brand-950 dark:to-smartblue-950 rounded-full blur-3xl opacity-10 pointer-events-none"></div>
      <div className="fixed bottom-0 left-0 translate-y-12 -translate-x-12 w-80 h-80 bg-gradient-to-tr from-purple-200 to-pink-200 dark:from-purple-950 dark:to-pink-950 rounded-full blur-3xl opacity-10 pointer-events-none"></div>
    </div>
  )
}
