import { AlertCircle } from 'lucide-react'
import { Button } from '@/shared/ui'
import { useI18n } from '@/shared/lib'
import clsx from 'clsx'

interface ErrorProfileProps {
  error?: string
  onRetry?: () => void
  retryText?: string
  size?: 'full' | 'medium' | 'small'
}

export const ErrorProfile = ({
  error,
  onRetry,
  retryText,
  size = 'full',
}: ErrorProfileProps) => {
  const { t } = useI18n()

  const containerClass = clsx(
    'bg-background flex items-center justify-center',
    {
      'min-h-screen': size === 'full',
      'min-h-[60vh]': size === 'medium',
      'min-h-[30vh]': size === 'small',
    }
  )

  return (
    <div className={containerClass}>
      <div className="text-center">
        <AlertCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
        <p className="text-destructive mb-4">
          {error || t('Помилка завантаження профілю')}
        </p>
        {onRetry && (
          <Button
            onClick={onRetry}
            className="bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 text-white"
          >
            {retryText || t('Спробувати знову')}
          </Button>
        )}
      </div>
    </div>
  )
}
