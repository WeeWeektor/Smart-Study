import { useEffect, useState } from 'react'
import {
  Badge,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Skeleton,
} from '@/shared/ui'
import { CheckCircle, ListChecks, XCircle } from 'lucide-react'
import { useI18n } from '@/shared/lib'
import { userCourseEnrollmentService } from '@/features/course'
import type { CourseTestSummary } from '@/features/test'

interface CourseResultsProps {
  courseId: string
}

export const CourseResults = ({ courseId }: CourseResultsProps) => {
  const { t } = useI18n()
  const [results, setResults] = useState<CourseTestSummary[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadResults = async () => {
      setLoading(true)
      try {
        const data =
          await userCourseEnrollmentService.getCourseTestResults(courseId)
        setResults(data)
      } finally {
        setLoading(false)
      }
    }

    if (courseId) {
      loadResults()
    }
  }, [courseId])

  if (loading) {
    return <ResultsSkeleton />
  }

  if (!results || results.length === 0) {
    return null
  }

  return (
    <Card className="w-full mt-6 border rounded-xl shadow-sm bg-card overflow-hidden">
      <CardHeader className="border-b bg-muted/30 pb-4">
        <CardTitle className="flex items-center gap-2 text-lg font-semibold">
          <ListChecks className="w-5 h-5 text-brand-600" />
          {t('Результати тестування')}
        </CardTitle>
      </CardHeader>

      <CardContent className="p-0">
        <div className="divide-y divide-border">
          {results.map(test => (
            <div
              key={test.id}
              className="flex flex-col sm:flex-row sm:items-center justify-between p-4 gap-4 hover:bg-muted/20 transition-colors"
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h4
                    className="font-medium text-foreground truncate"
                    title={test.title}
                  >
                    {test.title.length > 50
                      ? test.title.slice(0, 50)
                      : test.title}
                  </h4>
                  {test.test_type === 'module_test' && (
                    <Badge
                      variant="secondary"
                      className="text-[10px] px-1.5 h-5"
                    >
                      {t('Модуль')}
                    </Badge>
                  )}
                </div>

                <div className="text-sm text-muted-foreground flex items-center gap-3">
                  <span className="flex items-center gap-1">
                    {t('Спроби:')}
                    <span
                      className={
                        test.attempts_used >= test.max_attempts &&
                        test.max_attempts !== 0
                          ? 'text-red-500 font-medium'
                          : 'text-foreground'
                      }
                    >
                      {test.attempts_used}
                    </span>
                    <span className="text-muted-foreground/60">/</span>
                    <span>
                      {test.max_attempts === 0 ? '∞' : test.max_attempts}
                    </span>
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-4 shrink-0">
                <div className="text-right hidden sm:block">
                  <div
                    className={`text-lg font-bold ${getScoreColor(test.score, test.passed)}`}
                  >
                    {test.score} {t('балів')}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {t('Мін:')} {test.pass_score} {t('балів')}
                  </div>
                </div>

                <div className="min-w-[100px] flex justify-end">
                  <StatusBadge passed={test.passed} />
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

const getScoreColor = (score: number, passed: boolean) => {
  if (passed) return 'text-green-600 dark:text-green-500'
  if (score > 0) return 'text-orange-600 dark:text-orange-500'
  return 'text-muted-foreground'
}

const StatusBadge = ({ passed }: { passed: boolean }) => {
  const { t } = useI18n()

  if (passed) {
    return (
      <Badge
        variant="outline"
        className="bg-green-100 text-green-700 border-green-200 dark:bg-green-900/30 dark:text-green-400 dark:border-green-800 gap-1.5 px-3 py-1"
      >
        <CheckCircle className="w-3.5 h-3.5" />
        {t('Здано')}
      </Badge>
    )
  }

  return (
    <Badge
      variant="outline"
      className="bg-red-100 text-red-700 border-red-200 dark:bg-red-900/30 dark:text-red-400 dark:border-red-800 gap-1.5 px-3 py-1"
    >
      <XCircle className="w-3.5 h-3.5" />
      {t('Не здано')}
    </Badge>
  )
}

const ResultsSkeleton = () => (
  <Card className="w-full mt-6 border rounded-xl shadow-sm bg-card">
    <CardHeader className="border-b pb-4">
      <Skeleton className="h-6 w-48" />
    </CardHeader>
    <CardContent className="p-0">
      {[1, 2, 3].map(i => (
        <div
          key={i}
          className="p-4 flex justify-between items-center border-b last:border-0"
        >
          <div className="space-y-2">
            <Skeleton className="h-5 w-64" />
            <Skeleton className="h-4 w-32" />
          </div>
          <Skeleton className="h-8 w-24 rounded-full" />
        </div>
      ))}
    </CardContent>
  </Card>
)
