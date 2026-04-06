import { useI18n } from '@/shared/lib'

const NotFound = () => {
  const { t } = useI18n()
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4 text-foreground">404</h1>
        <p className="text-xl text-muted-foreground mb-4">
          {t('Ой! Сторінка не знайдена')}
        </p>
        <a
          href="/"
          className="text-brand-600 dark:text-brand-400 hover:text-brand-700 dark:hover:text-brand-300 underline"
        >
          {t('Повернутися на головну')}
        </a>
      </div>
    </div>
  )
}

export default NotFound
