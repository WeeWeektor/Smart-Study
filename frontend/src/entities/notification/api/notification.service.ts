import { ClassTranslator, ensureCsrfToken } from '@/shared/lib'
import { apiClient, handleApiCalendarError } from '@/shared/api'
import type { NotificationItemInterface } from '@/widgets/notificatiion'

export interface MarkReadDto {
  notification_ids: string[]
}

class NotificationApiService {
  private t = ClassTranslator.translate

  async getNotifications(
    archived: boolean = false
  ): Promise<NotificationItemInterface[]> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)
      const response = await apiClient.get<NotificationItemInterface[]>(
        '/notifications/get_notifications/',
        {
          params: { archived: archived.toString() },
          headers: { 'X-CSRFToken': csrfToken || '' },
          withCredentials: true,
        }
      )
      return response.data
    } catch (error) {
      throw handleApiCalendarError(
        error,
        'Не вдалось завантажити сповіщення: ',
        this.t
      )
    }
  }

  async markAsRead(data: MarkReadDto): Promise<void> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)
      await apiClient.post('/notifications/mark-read/', data, {
        headers: { 'X-CSRFToken': csrfToken || '' },
        withCredentials: true,
      })
    } catch (error) {
      throw handleApiCalendarError(
        error,
        'Не вдалось оновити статус сповіщень: ',
        this.t
      )
    }
  }

  async markAllAsRead(): Promise<void> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)
      await apiClient.post(
        '/notifications/mark-all-read/',
        {},
        {
          headers: { 'X-CSRFToken': csrfToken || '' },
          withCredentials: true,
        }
      )
    } catch (error) {
      throw handleApiCalendarError(
        error,
        'Не вдалось прочитати всі сповіщення: ',
        this.t
      )
    }
  }
}

export const notificationApiService = new NotificationApiService()
