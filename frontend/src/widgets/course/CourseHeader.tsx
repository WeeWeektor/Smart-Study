import { BookOpen, Plus } from 'lucide-react'
import { Button, EditableHeader } from '@/shared/ui'

interface CourseHeaderProps {
  title: string
  description: string
  action?: boolean
  onActionClick?: () => void
  actionText?: string
}

export const CourseHeader = ({
  title,
  description,
  action,
  onActionClick,
  actionText,
}: CourseHeaderProps) => {
  return (
    <EditableHeader
      title={title}
      description={description}
      icon={<BookOpen className="w-6 h-6 text-brand-600 dark:text-brand-400" />}
      actions={
        action && (
          <Button
            onClick={onActionClick}
            className="bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 text-white"
          >
            <Plus className="w-4 h-4 mr-2" />
            {actionText}
          </Button>
        )
      }
    />
  )
}
