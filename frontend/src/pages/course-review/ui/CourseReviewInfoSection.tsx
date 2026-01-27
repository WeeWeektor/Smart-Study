import React from 'react'
import { Card, CardContent } from '@/shared/ui'
import {
  BarChart,
  BookOpen,
  Clock,
  FileCheck,
  Globe,
  Layers,
  Star,
} from 'lucide-react'
import { parseISODuration, useI18n } from '@/shared/lib'
import { type CourseResponse } from '@/features/course'

interface CourseInfoSectionProps {
  course: CourseResponse | null
  averageRating: number
}

export const CourseInfoSection: React.FC<CourseInfoSectionProps> = ({
  course,
  averageRating,
}) => {
  const { t } = useI18n()

  if (!course || !course.course) return null

  const { title, description, cover_image, category, details } = course.course

  return (
    <Card className="mb-8 overflow-hidden shadow-sm border border-slate-200 dark:border-slate-800">
      {cover_image && (
        <div className="w-full h-64 md:h-80 relative bg-slate-100 dark:bg-slate-800">
          <img
            src={cover_image}
            alt={title}
            className="w-full h-full object-cover"
          />
          {category && (
            <div className="absolute top-4 left-4">
              <span className="bg-brand-600/90 text-white px-3 py-1 rounded-full text-sm font-medium uppercase tracking-wide shadow-md backdrop-blur-sm">
                {category}
              </span>
            </div>
          )}
        </div>
      )}

      <CardContent className="p-6">
        <div className="flex flex-col gap-6">
          <div>
            <h3 className="text-lg font-bold mb-2 text-slate-800 dark:text-slate-100 flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-brand-600" />
              {t('Про цей курс')}
            </h3>
            <p className="text-slate-600 dark:text-slate-300 leading-relaxed whitespace-pre-wrap">
              {description || t('Опис відсутній')}
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="flex flex-col gap-1 p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-100 dark:border-slate-800">
              <div className="flex items-center gap-2 text-slate-500 text-xs uppercase font-bold">
                <BarChart className="w-4 h-4" />
                {t('Рівень')}
              </div>
              <div className="font-semibold text-slate-700 dark:text-slate-200 capitalize">
                {details.level || t('Не вказано')}
              </div>
            </div>

            <div className="flex flex-col gap-1 p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-100 dark:border-slate-800">
              <div className="flex items-center gap-2 text-slate-500 text-xs uppercase font-bold">
                <Globe className="w-4 h-4" />
                {t('Мова')}
              </div>
              <div className="font-semibold text-slate-700 dark:text-slate-200">
                {details.course_language || t('Не вказано')}
              </div>
            </div>

            <div className="flex flex-col gap-1 p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-100 dark:border-slate-800">
              <div className="flex items-center gap-2 text-slate-500 text-xs uppercase font-bold">
                <Clock className="w-4 h-4" />
                {t('Тривалість')}
              </div>
              <div className="font-semibold text-slate-700 dark:text-slate-200">
                {parseISODuration(details.time_to_complete, t)}
              </div>
            </div>

            <div className="flex flex-col gap-1 p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-100 dark:border-slate-800">
              <div className="flex items-center gap-2 text-slate-500 text-xs uppercase font-bold">
                <Star className="w-4 h-4" />
                {t('Рейтинг')}
              </div>
              <div className="font-semibold text-slate-700 dark:text-slate-200 flex items-center gap-1">
                <span>{averageRating.toFixed(1)}</span>
                <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
              </div>
            </div>
          </div>

          <div className="flex flex-wrap gap-4 pt-4 border-t border-slate-100 dark:border-slate-800">
            <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
              <Layers className="w-4 h-4 text-brand-500" />
              <span className="font-medium">
                {details.total_modules} {t('модулів')}
              </span>
            </div>
            <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
              <BookOpen className="w-4 h-4 text-blue-500" />
              <span className="font-medium">
                {details.total_lessons} {t('уроків')}
              </span>
            </div>
            <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
              <FileCheck className="w-4 h-4 text-green-500" />
              <span className="font-medium">
                {details.total_tests} {t('тестів')}
              </span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
