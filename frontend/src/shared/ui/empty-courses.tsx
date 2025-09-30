import { BookOpen } from 'lucide-react'
import { useI18n } from '@/shared/lib'

export const EmptyCourses = () => {
  const { t } = useI18n()

  return (
    <div className="text-center py-12">
      <BookOpen className="w-12 h-12 text-slate-400 dark:text-slate-500 mx-auto mb-4" />
      <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100 mb-2">
        {t('Курси не знайдено')}
      </h3>
      <p className="text-slate-600 dark:text-slate-300">
        {t('Спробуйте змінити фільтри або пошуковий запит')}
      </p>
    </div>
  )
}
