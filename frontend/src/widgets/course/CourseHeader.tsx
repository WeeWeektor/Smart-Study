import { BookOpen, Globe, Loader2, Plus, Save } from 'lucide-react'
import { Button, EditableHeader } from '@/shared/ui'
import { useI18n } from '@/shared/lib'
import type { ReactNode } from 'react'

interface CourseHeaderProps {
  title: string
  description: string
  action?: boolean
  onActionClick?: () => void
  createCourse?: boolean
  actionOnClick?: [() => void, () => void, () => void]
  actionInfo?: boolean
  actionText?: [string, string] | string
  actionsBackPage?: ReactNode
  icon?: ReactNode
  user_is_login?: boolean
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
  actionsBackPage,
  icon,
  user_is_login = true,
}: CourseHeaderProps) => {
  const { t } = useI18n()

  return (
    <EditableHeader
      is_user_login={user_is_login}
      title={title}
      description={description}
      icon={
        icon ? (
          icon
        ) : (
          <BookOpen className="w-6 h-6 text-brand-600 dark:text-brand-400" />
        )
      }
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
            <Button
              className="bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 text-white"
              onClick={actionOnClick?.[2]}
              disabled={actionInfo}
            >
              {actionInfo ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  {t('Публікація...')}
                </>
              ) : (
                <>
                  <Globe className="w-4 h-4 mr-2" />
                  {t('Опублікувати')}
                </>
              )}
            </Button>
          </div>
        ))
      }
      actionsBackPage={actionsBackPage}
    />
  )
}
