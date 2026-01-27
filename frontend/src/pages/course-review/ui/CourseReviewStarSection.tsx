import React from 'react'
import { Card, CardContent, CardHeader } from '@/shared/ui'
import { Star } from 'lucide-react'
import { useI18n } from '@/shared/lib'
import { type Review } from '@/features/course'

interface StarSectionProps {
  reviews: Review[]
  averageRating: number
  distribution: Record<string, number>
}

export const StarSection: React.FC<StarSectionProps> = ({
  reviews,
  averageRating,
  distribution,
}) => {
  const { t } = useI18n()
  const totalCount = reviews.length
  const starLevels = [5, 4, 3, 2, 1]

  return (
    <Card className="mb-8 overflow-hidden shadow-sm border border-slate-200 dark:border-slate-800">
      <CardHeader className="pb-4 border-b border-slate-100 dark:border-slate-800">
        <h3 className="text-xl font-bold text-slate-800 dark:text-slate-100 flex items-center gap-2">
          <Star className="w-5 h-5 text-brand-600" />
          {t('Рейтинг курсу')}
        </h3>
      </CardHeader>

      <CardContent className="p-6">
        <div className="flex flex-col md:flex-row gap-8 items-center">
          <div className="flex flex-col items-center justify-center min-w-[200px] text-center">
            <div className="text-5xl font-extrabold text-slate-900 dark:text-slate-100 mb-2">
              {averageRating.toFixed(1)}
            </div>

            <div className="flex items-center gap-1 mb-2">
              {[1, 2, 3, 4, 5].map(star => (
                <Star
                  key={star}
                  className={`w-5 h-5 ${
                    star <= Math.round(averageRating)
                      ? 'fill-yellow-400 text-yellow-400'
                      : 'fill-slate-200 text-slate-200 dark:fill-slate-700 dark:text-slate-700'
                  }`}
                />
              ))}
            </div>

            <p className="text-sm text-slate-500 dark:text-slate-400">
              {t('На основі')}{' '}
              <span className="font-semibold text-slate-700 dark:text-slate-200">
                {totalCount}
              </span>{' '}
              {t('відгуків')}
            </p>
          </div>

          <div className="flex-1 w-full space-y-3">
            {starLevels.map(level => {
              const count = distribution[level] || 0
              const percentage = totalCount > 0 ? (count / totalCount) * 100 : 0

              return (
                <div key={level} className="flex items-center gap-3 text-sm">
                  <div className="flex items-center gap-1 w-16 shrink-0 text-slate-600 dark:text-slate-400 font-medium">
                    <span>{level}</span>
                    <Star className="w-3.5 h-3.5 fill-slate-400 text-slate-400" />
                  </div>

                  <div className="flex-1 h-2.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-yellow-400 rounded-full transition-all duration-500 ease-out"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>

                  <div className="w-20 shrink-0 text-right text-slate-500 dark:text-slate-500 text-xs">
                    <span className="font-semibold text-slate-700 dark:text-slate-300 mr-1">
                      {count}
                    </span>
                    ({Math.round(percentage)}%)
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
