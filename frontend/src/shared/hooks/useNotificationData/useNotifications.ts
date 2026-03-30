import { useCallback, useEffect, useRef, useState } from 'react'
import type { NotificationItemInterface } from '@/widgets/notificatiion'
import { useI18n } from '@/shared/lib'
import { notificationApiService } from '@/entities/notification/api'

// TODO Історія відправлених
// TODO зберігати повідомлення: додати перехід(кнопку перейти) тоді автор курсу вже бачитеме повідомлення зможе його перевірити і додати радіобокс перед пубілкацією з попередженням що все більше не зможе йоого редагувати нехай шляпа перевірить і тоді кнопку опублікувати
// TODO при отриманні сповіщень від сервера, оновлювати стан сповіщень та кількість непрочитаних

export const useNotifications = (isAuthorized: boolean) => {
  const { t } = useI18n()
  const [notifications, setNotifications] = useState<
    NotificationItemInterface[]
  >([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isArchivedView, setIsArchivedView] = useState(false)

  const pendingReadIds = useRef<Set<string>>(new Set())

  const updateState = useCallback(
    (data: NotificationItemInterface[], archived: boolean) => {
      setNotifications(data)
      if (!archived) {
        setUnreadCount(data.filter(n => !n.is_read).length)
      }
    },
    []
  )

  const fetchNotifications = useCallback(
    async (archived = false) => {
      if (!isAuthorized) return
      setLoading(true)
      setError(null)
      setIsArchivedView(archived)
      try {
        const data = await notificationApiService.getNotifications(archived)
        updateState(data, archived)
        if (!archived) {
          setUnreadCount(data.filter(n => !n.is_read).length)
        }
      } catch (err) {
        setError(
          `${t('Не вдалося завантажити сповіщення')}: ${err instanceof Error ? err.message : String(err)}`
        )
      } finally {
        setLoading(false)
      }
    },
    [isAuthorized, t, updateState]
  )

  const markAsReadLocally = useCallback((id: string) => {
    setNotifications(prev =>
      prev.map(n => {
        if (n.id === id && !n.is_read) {
          pendingReadIds.current.add(id)
          return { ...n, is_read: true }
        }
        return n
      })
    )
    setUnreadCount(prev => Math.max(0, prev - 1))
  }, [])

  const syncReadStatusWithServer = useCallback(async () => {
    if (pendingReadIds.current.size === 0) return

    const idsToSend = Array.from(pendingReadIds.current)
    try {
      const updatedData = await notificationApiService.markAsRead({
        notification_ids: idsToSend,
      })
      updateState(updatedData, isArchivedView)
      pendingReadIds.current.clear()
    } catch (err) {
      setError(
        t('Помилка при оновленні статусів') +
          ': ' +
          (err instanceof Error ? err.message : String(err))
      )
    }
  }, [isArchivedView, t, updateState])

  const markAllAsRead = async () => {
    try {
      const updatedData = await notificationApiService.markAllAsRead()
      updateState(updatedData, isArchivedView)
      pendingReadIds.current.clear()
    } catch (err) {
      setError(
        t('Помилка при оновленні статусів') +
          ': ' +
          (err instanceof Error ? err.message : String(err))
      )
    }
  }

  useEffect(() => {
    return () => {
      if (isAuthorized) syncReadStatusWithServer()
    }
  }, [isAuthorized, syncReadStatusWithServer])

  return {
    notifications,
    unreadCount,
    loading,
    error,
    isArchivedView,
    fetchNotifications,
    markAsReadLocally,
    markAllAsRead,
    syncReadStatusWithServer,
  }
}
