import { Button } from '@/shared/ui'
import { Download, Eye, EyeOff, ImagePlusIcon, Loader2 } from 'lucide-react'
import { useI18n } from '@/shared/lib'
import { CourseResults } from '@/pages/course-completion'
import { useState } from 'react'

interface CourseSuccessProps {
  courseId: string
  certificateUrl: string | null
  isGenerating: boolean
  onDownload: () => void
  onGenerate: () => void
}

export const CourseSuccess = ({
  courseId,
  certificateUrl,
  isGenerating,
  onDownload,
  onGenerate,
}: CourseSuccessProps) => {
  const { t } = useI18n()
  const [showResults, setShowResults] = useState<boolean>(false)

  const toggleResults = () => {
    setShowResults(prev => !prev)
  }

  // TODO додати при генерації сертифікату
  const renderLoader = () => {
    return (
      <div className="flex flex-col items-center">
        <Loader2 className="h-12 w-12 animate-spin mx-auto text-brand-600 dark:text-brand-400" />
        <h2 className="text-center text-lg font-semibold mt-4 text-muted-foreground">
          {t('Генерація сертифікату...')}
        </h2>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="bg-card border border-green-200 dark:border-green-900 rounded-xl p-6 shadow-sm">
        <h3 className="text-xl font-semibold text-green-600 mb-2">
          {t('Вітаємо!')}
        </h3>
        <p className="text-lg mb-6 text-muted-foreground">
          {t(
            'Ви успішно завершили цей курс. Ваш сертифікат готовий до завантаження.'
          )}
        </p>

        <div className="flex flex-wrap gap-4 mt-4">
          {certificateUrl ? (
            <Button
              onClick={onDownload}
              className="gap-2 bg-green-600 hover:bg-green-700 text-white"
            >
              <Download className="w-4 h-4" />
              {t('Завантажити сертифікат')}
            </Button>
          ) : (
            <Button
              onClick={onGenerate}
              disabled={isGenerating}
              variant="outline"
              className="gap-2"
            >
              {isGenerating ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <ImagePlusIcon className="w-4 h-4" />
              )}
              {isGenerating ? t('Генерація...') : t('Отримати сертифікат')}
            </Button>
          )}

          <Button
            onClick={toggleResults}
            className="gap-2 w-64 bg-green-100 text-green-700 hover:bg-green-200 border-green-20"
          >
            {showResults ? (
              <>
                <EyeOff className="w-4 h-4" />
                {t('Приховати результати')}
              </>
            ) : (
              <>
                <Eye className="w-4 h-4" />
                {t('Переглянути результати тестів')}
              </>
            )}
          </Button>
        </div>
      </div>
      {showResults && (
        <div className="animate-in fade-in slide-in-from-top-4 duration-300">
          <CourseResults courseId={courseId} />
        </div>
      )}
    </div>
  )
}
