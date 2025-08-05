import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui'
import { TrendingUp } from 'lucide-react'

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
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <TrendingUp className="w-5 h-5 mr-2 text-brand-600 dark:text-brand-400" />
          Статистика навчання
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex justify-between">
          <span className="text-muted-foreground">Загальний час</span>
          <span className="font-semibold">{stats.totalHours} годин</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">Завершено курсів</span>
          <span className="font-semibold">{stats.coursesCompleted}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">Середній бал</span>
          <span className="font-semibold">{stats.averageScore}%</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">Streak</span>
          <span className="font-semibold flex items-center">
            🔥 {stats.streak} днів
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">Сертифікати</span>
          <span className="font-semibold">{stats.certificates}</span>
        </div>
      </CardContent>
    </Card>
  )
}
