import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import {
  Award,
  BookOpen,
  CheckCircle,
  FileText,
  TrendingUp,
} from 'lucide-react'
import { useI18n } from '@/shared/lib'

interface LearningStatsProps {
  stats: {
    coursesCompleted: number
    coursesInProgress: number
    totalTests: number
    completedTopics: number
    certificates: number
  }
}

export const LearningStats = ({
  stats = {
    coursesCompleted: 0,
    coursesInProgress: 0,
    totalTests: 0,
    completedTopics: 0,
    certificates: 0,
  },
}: LearningStatsProps) => {
  const { t } = useI18n()

  if (!stats) return null

  return (
    <Card className="">
      <CardHeader>
        <CardTitle className="flex items-center text-xl">
          <TrendingUp className="w-5 h-5 mr-2 text-brand-600 dark:text-brand-400" />
          {t('Прогрес навчання')}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center">
            <CheckCircle className="w-4 h-4 mr-3 text-muted-foreground" />
            <span className="text-muted-foreground">
              {t('Завершено курсів')}
            </span>
          </div>
          <span className="font-semibold text-foreground">
            {stats.coursesCompleted}
          </span>
        </div>

        <div className="flex justify-between items-center">
          <div className="flex items-center">
            <BookOpen className="w-4 h-4 mr-3 text-muted-foreground" />
            <span className="text-muted-foreground">
              {t('Курсів у процесі')}
            </span>
          </div>
          <span className="font-semibold text-foreground">
            {stats.coursesInProgress}
          </span>
        </div>

        <div className="flex justify-between items-center">
          <div className="flex items-center">
            <FileText className="w-4 h-4 mr-3 text-muted-foreground" />
            <span className="text-muted-foreground">
              {t('Пройдено тестів')}
            </span>
          </div>
          <span className="font-semibold text-foreground">
            {stats.totalTests}
          </span>
        </div>

        <div className="flex justify-between items-center">
          <div className="flex items-center">
            <BookOpen className="w-4 h-4 mr-3 text-muted-foreground" />
            <span className="text-muted-foreground">{t('Вивчено тем')}</span>
          </div>
          <span className="font-semibold text-brand-600 dark:text-brand-400">
            {stats.completedTopics}
          </span>
        </div>

        <div className="flex justify-between items-center border-t pt-4 mt-2">
          <div className="flex items-center">
            <Award className="w-5 h-5 mr-3 text-brand-600 dark:text-brand-400" />
            <span className="text-muted-foreground font-medium">
              {t('Отримано сертифікатів')}
            </span>
          </div>
          <span className="font-bold text-lg text-brand-600 dark:text-brand-400">
            {stats.certificates}
          </span>
        </div>
      </CardContent>
    </Card>
  )
}
