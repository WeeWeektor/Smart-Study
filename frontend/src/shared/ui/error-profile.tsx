import { AlertCircle } from 'lucide-react'
import { Button } from '@/shared/ui'
import { useI18n } from '@/shared/lib'

interface ErrorProfileProps {
  error?: string
  onRetry?: () => void
  retryText?: string
}

export const ErrorProfile = ({
  error,
  onRetry,
  retryText,
}: ErrorProfileProps) => {
  const { t } = useI18n()

  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
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
