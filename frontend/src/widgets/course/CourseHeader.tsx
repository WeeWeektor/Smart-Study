import { BookOpen, Loader2, Plus, Save } from 'lucide-react'
import { Button, EditableHeader } from '@/shared/ui'
import { useI18n } from '@/shared/lib'

interface CourseHeaderProps {
  title: string
  description: string
  action?: boolean
  onActionClick?: () => void
  createCourse?: boolean
  actionOnClick?: [() => void, () => void]
  actionInfo?: boolean
  actionText?: [string, string] | string
}

export const CourseHeader = ({
  title,
  description,
  action,
  onActionClick,
  createCourse,
  actionOnClick,
  actionInfo,
  actionText,
}: CourseHeaderProps) => {
  const { t } = useI18n()

  return (
    <EditableHeader
      title={title}
      description={description}
      icon={<BookOpen className="w-6 h-6 text-brand-600 dark:text-brand-400" />}
      actions={
        (action && (
          <Button
            onClick={onActionClick}
            className="bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 text-white"
          >
            <Plus className="w-4 h-4 mr-2" />
            {actionText}
          </Button>
        )) ||
        (createCourse && (
          <div className="flex space-x-2">
            <Button
              variant="outline"
              onClick={actionOnClick?.[0]}
              disabled={actionInfo}
            >
              {actionText?.[0]}
            </Button>
            <Button
              className="bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 text-white"
              onClick={actionOnClick?.[1]}
              disabled={actionInfo}
            >
              {actionInfo ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  {t('Збереження...')}
                </>
              ) : (
                <>
                  <Save className="w-4 h-4 mr-2" />
                  {t('Зберегти')}
                </>
              )}
            </Button>
          </div>
        ))
      }
    />
  )
}
