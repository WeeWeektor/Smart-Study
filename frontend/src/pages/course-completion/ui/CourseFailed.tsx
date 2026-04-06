import { Button, Card, CardContent, CardFooter, CardHeader } from '@/shared/ui'
import {
  ChevronLeftCircle,
  Eye,
  EyeOff,
  MessageSquarePlus,
  XCircle,
} from 'lucide-react'
import { useI18n } from '@/shared/lib'
import { CourseResults } from '@/pages/course-completion'
import React, { useEffect, useState } from 'react'
import { userCourseEnrollmentService } from '@/features/course'

interface CourseFailedProps {
  courseId: string
  onReturn: () => void
  onLeaveReview: () => void
  returnButtons: () => React.ReactNode
}

export const CourseFailed = ({
  courseId,
  onReturn,
  onLeaveReview,
  returnButtons,
}: CourseFailedProps) => {
  const { t } = useI18n()
  const [showResults, setShowResults] = useState<boolean>(false)

  const [canShowResults, setCanShowResults] = useState(false)
  const [checking, setChecking] = useState(true)

  useEffect(() => {
    let isMounted = true

    const checkResults = async () => {
      if (!courseId) return

      setChecking(true)
      setCanShowResults(false)
      setShowResults(false)

      try {
        const data =
          await userCourseEnrollmentService.getCourseTestResults(courseId)

        if (isMounted) {
          if (Array.isArray(data) && data.length > 0) {
            setCanShowResults(true)
          } else {
            setCanShowResults(false)
          }
        }
      } catch (e) {
        console.error('Failed to check results:', e)
        if (isMounted) setCanShowResults(false)
      } finally {
        if (isMounted) setChecking(false)
      }
    }

    checkResults()

    return () => {
      isMounted = false
    }
  }, [courseId])

  const toggleResults = () => {
    setShowResults(prev => !prev)
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <Card className="w-full max-w-4xl mx-auto overflow-hidden bg-white dark:bg-slate-800 border-red-200 dark:border-red-900/50 shadow-md">
        <div className="flex flex-col items-center text-center p-6 sm:p-10">
          <div className="mb-6 flex h-24 w-24 items-center justify-center rounded-full bg-red-50 dark:bg-red-900/20">
            <XCircle className="h-12 w-12 text-red-600 dark:text-red-400" />
          </div>

          <CardHeader className="p-0 mb-4">
            <h3 className="text-2xl font-bold tracking-tight text-foreground text-red-600 dark:text-red-500">
              {t('Курс не зараховано')}
            </h3>
          </CardHeader>

          <CardContent className="p-0 mb-8 max-w-lg mx-auto">
            <p className="text-muted-foreground text-lg leading-relaxed">
              {t(
                'На жаль, ви не пройшли цей курс, оскільки використали всі спроби тестування. Зверніться до адміністратора або спробуйте записатися на курс повторно.'
              )}
            </p>
          </CardContent>

          <CardFooter className="p-0 w-full flex flex-col items-center gap-4">
            <Button
              onClick={onReturn}
              size="lg"
              className="w-full sm:w-auto min-w-[240px] gap-2 text-base font-medium bg-red-600 hover:bg-red-700 text-white shadow-red-200 dark:shadow-none shadow-lg transition-all hover:scale-105"
            >
              <ChevronLeftCircle className="w-5 h-5" />
              {t('Повернутись до змісту')}
            </Button>

            <div className="flex items-center gap-4">
              <Button
                onClick={toggleResults}
                variant="outline"
                className="text-muted-foreground hover:text-foreground gap-2 mt-2 w-64"
                disabled={checking || !canShowResults}
                title={
                  !checking && !canShowResults
                    ? t('У цьому курсі немає тестів')
                    : ''
                }
              >
                {showResults ? (
                  <>
                    <EyeOff className="w-4 h-4" />
                    {t('Приховати результати')}
                  </>
                ) : (
                  <>
                    <Eye className="w-4 h-4" />
                    {checking
                      ? t('Перевірка...')
                      : t('Переглянути, де були помилки')}
                  </>
                )}
              </Button>
              <Button
                onClick={onLeaveReview}
                variant="outline"
                className="text-muted-foreground hover:text-foreground gap-2 mt-2 w-64"
              >
                <MessageSquarePlus className="w-4 h-4" />
                {t('Залишити відгук')}
              </Button>
            </div>

            {returnButtons()}
          </CardFooter>
        </div>

        <div className="h-1.5 w-full bg-gradient-to-r from-red-500 to-orange-600" />
      </Card>

      {showResults && !checking && canShowResults && (
        <div className="animate-in slide-in-from-top-4 fade-in duration-300 w-full max-w-4xl mx-auto">
          <CourseResults courseId={courseId} />
        </div>
      )}
    </div>
  )
}
