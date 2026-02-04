import { Button } from '@/shared/ui'
import { Eye, EyeOff, RotateCcw } from 'lucide-react'
import { useI18n } from '@/shared/lib'
import { CourseResults } from '@/pages/course-completion'
import { useState } from 'react'

interface CourseFailedProps {
  courseId: string
  onReturn: () => void
}

export const CourseFailed = ({ courseId, onReturn }: CourseFailedProps) => {
  const { t } = useI18n()
  const [showResults, setShowResults] = useState<boolean>(false)

  const toggleResults = () => {
    setShowResults(prev => !prev)
  }

  return (
    <div className="space-y-6">
      <div className="bg-card border border-red-200 dark:border-red-900 rounded-xl p-6 shadow-sm">
        <h3 className="text-xl font-semibold text-red-600 mb-2">
          {t('Курс не зараховано')}
        </h3>
        <p className="text-lg mb-6 text-muted-foreground">
          {t(
            'На жаль, ви не пройшли цей курс. Ви використали всі спроби тестування. Зверніться до адміністратора або спробуйте записатися на курс повторно, якщо це можливо.'
          )}
        </p>

        <div className="flex flex-wrap gap-4 mt-4">
          <Button onClick={onReturn} variant="outline" className="gap-2">
            <RotateCcw className="w-4 h-4" />
            {t('Повернутись до змісту')}
          </Button>

          <Button
            onClick={toggleResults}
            className="gap-2 w-64 bg-red-100 text-red-700 hover:bg-red-200 border-red-20"
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
