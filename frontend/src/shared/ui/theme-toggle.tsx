import { useTheme } from '@/shared/hooks/use-theme'
import React from 'react'

export const ThemeToggle: React.FC = () => {
  const [theme, setTheme] = useTheme()

  return (
    <button
      onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
      className="px-3 py-1 rounded border border-border bg-background text-foreground hover:bg-muted transition-colors"
    >
      {theme === 'light' ? '🌞 Світла' : '🌙 Темна'}
    </button>
  )
}
