import { Loader2 } from 'lucide-react'
import { useI18n } from '@/shared/lib'

interface LoadingProfileProps {
  message?: string
}

export const LoadingProfile = ({ message }: LoadingProfileProps) => {
  const { t } = useI18n()

  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="text-center">
        <Loader2 className="h-12 w-12 animate-spin mx-auto text-brand-600 dark:text-brand-400" />
        <p className="mt-4 text-muted-foreground">
          {message || t('Завантаження профілю...')}
        </p>
      </div>
    </div>
  )
}
