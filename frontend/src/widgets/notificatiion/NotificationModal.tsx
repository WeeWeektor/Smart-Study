import React, { useEffect, useState } from 'react'
import { Bell, Clock, X } from 'lucide-react'
import { useI18n } from '@/shared/lib'
import { Button } from '@/shared/ui'
import { useNotifications } from '@/shared/hooks/useNotificationData'
import { NotificationItem } from '@/widgets/notificatiion/NotificationItem.tsx'

interface NotificationModalProps {
  isOpen: boolean
  onClose: () => void
}

// TODO скролбар під тему

export const NotificationModal: React.FC<NotificationModalProps> = ({
  isOpen,
  onClose,
}) => {
  const { t } = useI18n()
  const {
    notifications,
    markAllAsRead,
    fetchNotifications,
    syncReadStatusWithServer,
    isArchivedView,
    markAsReadLocally,
    loading,
  } = useNotifications(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (isOpen) fetchNotifications(false)
  }, [isOpen, fetchNotifications])

  const handleClose = async () => {
    await syncReadStatusWithServer()
    onClose()
  }

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [isOpen])

  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleEsc)
    return () => window.removeEventListener('keydown', handleEsc)
  }, [onClose])

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-[999] flex justify-end">
      <div
        className="absolute inset-0 bg-black/40 backdrop-blur-[2px] transition-opacity duration-300"
        onClick={onClose}
      />

      <aside className="relative w-full max-w-md bg-white dark:bg-slate-900 h-screen shadow-2xl flex flex-col animate-in slide-in-from-right duration-300 border-l border-border">
        <div className="flex items-center justify-between p-6 border-b border-border bg-card">
          <div className="flex items-center gap-3">
            <Clock className="w-6 h-6 text-brand-600" />
            <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
              {isArchivedView ? t('Архів повідомлень') : t('Сповіщення')}
            </h2>
          </div>
          <div className="flex items-center ring-0 ml-auto gap-1">
            <Button
              variant="ghost"
              size="icon"
              onClick={handleClose}
              className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full transition-colors text-muted-foreground hover:text-foreground"
              aria-label={t('Закрити')}
            >
              <X className="w-5 h-5" />
            </Button>
          </div>
        </div>

        <div
          className="flex-1 overflow-y-auto p-6 dark:bg-slate-900/30 bg-slate-50/50 rounded-b-xl space-y-4
                 dark:scrollbar-slate-800
                 scrollbar-track-transparent
                 scrollbar-thumb-gray-300
                 dark:scrollbar-thumb-slate-700
                 hover:scrollbar-thumb-gray-400
                 dark:hover:scrollbar-thumb-slate-500
                 scrollbar-thumb-rounded-full
                 transition-colors"
        >
          {notifications.length > 0 ? (
            notifications.map(notification => (
              <NotificationItem
                key={notification.id}
                onMarkRead={() => markAsReadLocally(notification.id)}
                notification={notification}
              />
            ))
          ) : (
            <div className="text-center py-20 flex flex-col items-center justify-center">
              <div className="bg-slate-100 dark:bg-slate-800 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 text-slate-400 opacity-50">
                <Bell className="w-8 h-8" />
              </div>
              <p className="text-sm text-muted-foreground font-medium">
                {t('Поки що немає нових сповіщень')}
              </p>
            </div>
          )}
        </div>

        <div className="p-4 border-t border-border bg-slate-50 dark:bg-slate-800/30 space-y-3">
          {!isArchivedView && (
            <Button
              className="w-full text-brand-600 dark:text-brand-400 font-semibold py-3 px-4 rounded-xl hover:bg-brand-50 dark:hover:bg-brand-900/20 transition-colors bg-white dark:bg-slate-900 border"
              onClick={markAllAsRead}
            >
              {t('Позначити всі як прочитані')}
            </Button>
          )}
          <Button
            className="w-full text-brand-600 dark:text-brand-400 font-semibold py-3 px-4 rounded-xl hover:bg-brand-50 dark:hover:bg-brand-900/20 transition-colors bg-slate-50 dark:bg-slate-900/20"
            onClick={() => fetchNotifications(!isArchivedView)}
          >
            {isArchivedView
              ? t('Повернутись до активних')
              : t('Архів повідомлень')}
          </Button>
        </div>
      </aside>
    </div>
  )
}
