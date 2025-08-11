import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { TrendingUp } from 'lucide-react'
import { useI18n } from '@/shared/lib'

interface LearningStatsProps {
  stats: {
    totalHours: number
    coursesCompleted: number
    coursesInProgress: number
    averageScore: number
    streak: number
    totalTests: number
    certificates: number
  }
}

export const LearningStats = ({ stats }: LearningStatsProps) => {
  const { t } = useI18n()
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <TrendingUp className="w-5 h-5 mr-2 text-brand-600 dark:text-brand-400" />
          {t('stats.title')}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex justify-between">
          <span className="text-muted-foreground">{t('stats.totalTime')}</span>
          <span className="font-semibold">
            {stats.totalHours} {t('stats.hoursSuffix')}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">
            {t('stats.completedCourses')}
          </span>
          <span className="font-semibold">{stats.coursesCompleted}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">
            {t('stats.averageScore')}
          </span>
          <span className="font-semibold">{stats.averageScore}%</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">{t('stats.streak')}</span>
          <span className="font-semibold flex items-center">
            🔥 {stats.streak} {t('stats.daysSuffix')}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">
            {t('stats.certificates')}
          </span>
          <span className="font-semibold">{stats.certificates}</span>
        </div>
      </CardContent>
    </Card>
  )
}
