import { Button, ThemeToggle } from '@/shared/ui'
import { type ReactNode, useEffect, useState } from 'react'
import { Bell } from 'lucide-react'
import { NotificationModal } from '@/widgets/notificatiion'
import { useNotifications } from '@/shared/hooks/useNotificationData'

interface EditableHeaderProps {
  title: string
  description: string
  icon: ReactNode
  actions?: ReactNode
  actionsBackPage?: ReactNode
  is_user_login?: boolean
}

// TODO викладач отримує не ті повідомлення (студенту приходять в 8 ранку і викладач іх тоже бачить)

export const EditableHeader = ({
  title,
  description,
  icon,
  actions,
  actionsBackPage,
  is_user_login,
}: EditableHeaderProps) => {
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false)
  const { unreadCount, fetchNotifications } = useNotifications(!!is_user_login)

  useEffect(() => {
    if (is_user_login) {
      fetchNotifications()
    }
  }, [is_user_login, fetchNotifications])

  return (
    <header className="bg-card border-b border-border text-card-foreground">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center justify-between space-x-4">
            {actionsBackPage}
            <div>
              <h1 className="text-2xl font-semibold flex items-center text-foreground">
                {icon && <span className="mr-2">{icon}</span>}
                {title.length > 60 ? `${title.slice(0, 60)}...` : title}
              </h1>
              <p className="text-muted-foreground">
                {description.length > 100
                  ? `${description.slice(0, 100)}...`
                  : description}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {actions}
            <ThemeToggle variant="secondary" size="default" />
            {is_user_login && (
              <Button
                variant="ghost"
                size="sm"
                className="relative"
                onClick={() => setIsNotificationsOpen(true)}
              >
                <Bell className="w-5 h-5" />
                {unreadCount > 0 && (
                  <span className="absolute top-1 right-1 w-2.5 h-2.5 bg-red-500 rounded-full border-2 border-card"></span>
                )}
              </Button>
            )}
          </div>
        </div>
      </div>

      <NotificationModal
        isOpen={isNotificationsOpen}
        onClose={() => setIsNotificationsOpen(false)}
      />
    </header>
  )
}
