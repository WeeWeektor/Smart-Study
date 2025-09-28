import { BookOpen } from 'lucide-react'
import { EditableHeader } from '@/shared/ui'
import { useI18n } from '@/shared/lib'

export const CourseHeader = () => {
  const { t } = useI18n()

  return (
    <EditableHeader
      title={t('Підібрати курс')}
      description={t('Підберіть курс за вашими інтересами та цілями')}
      icon={<BookOpen className="w-6 h-6 text-brand-600 dark:text-brand-400" />}
    />
  )
}
