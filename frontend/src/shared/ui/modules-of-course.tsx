import { useI18n } from '@/shared/lib'
import { BookOpen, Plus } from 'lucide-react'
import { Button } from '@/shared/ui/button.tsx'

export const ModulesOfCourse = () => {
  const { t } = useI18n()
  return (
    <div className="text-center py-12 text-slate-500">
      <BookOpen className="w-12 h-12 mx-auto mb-4 text-slate-300" />
      <p className="text-lg font-medium mb-2">{t('Модулі не додано')}</p>
      <p>{t('Додайте перший модуль для початку створення курсу')}</p>
      <Button className="mt-6 w-40 bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 text-white">
        <Plus className="w-4 h-4 mr-2" />
        {t('Додати модуль')}
      </Button>
    </div>
  )
}
