import { useTheme } from '@/shared/hooks/use-theme'
import React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/shared/lib/utils'
import { useI18n } from '@/shared/lib'

const themeToggleVariants = cva(
  'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90',
        outline:
          'border border-input bg-background hover:bg-accent hover:text-accent-foreground dark:bg-card dark:hover:bg-accent dark:hover:text-accent-foreground',
        secondary:
          'bg-secondary text-secondary-foreground hover:bg-secondary/80 dark:bg-secondary dark:hover:bg-secondary/90',
        ghost:
          'hover:bg-accent hover:text-accent-foreground dark:hover:bg-accent dark:hover:text-accent-foreground',
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-9 rounded-md px-3',
        lg: 'h-11 rounded-md px-8',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'outline',
      size: 'default',
    },
  }
)

export interface ThemeToggleProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof themeToggleVariants> {}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({
  className,
  variant,
  size,
  ...props
}) => {
  const [theme, setTheme] = useTheme()
  const { t } = useI18n()

  return (
    <button
      onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
      className={cn(themeToggleVariants({ variant, size, className }))}
      {...props}
    >
      {theme === 'light' ? '🌞 ' + `${t('Світла')}` : '🌙 ' + `${t('Темна')}`}
    </button>
  )
}
