import { ClassTranslator, ensureCsrfToken } from '@/shared/lib'
import { apiClient, handleApiCalendarError } from '@/shared/api'

export interface PersonalEvent {
  id: string
  title: string
  description: string
  event_date: string
  importance: 'low' | 'medium' | 'high'
  is_completed: boolean
  completed_at: string | null
  link: string | null
  is_personal: boolean
}

export interface CreateEventDto {
  title: string
  description: string
  event_date: string
  importance: string
  link?: string
}

class CalendarApiService {
  private t = ClassTranslator.translate

  async getEvents(): Promise<PersonalEvent[]> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)
      const response = await apiClient.get<PersonalEvent[]>(
        '/user-calendar/personal-events/',
        {
          headers: { 'X-CSRFToken': csrfToken || '' },
          withCredentials: true,
        }
      )
      return response.data
    } catch (error) {
      throw handleApiCalendarError(
        error,
        'Не вдалось завантажити події: ',
        this.t
      )
    }
  }

  async createEvent(data: CreateEventDto): Promise<PersonalEvent[]> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      if (data.description === null || data.description === undefined) {
        data.description = ''
      }

      const response = await apiClient.post<PersonalEvent[]>(
        '/user-calendar/personal-events/',
        data,
        {
          headers: { 'X-CSRFToken': csrfToken || '' },
          withCredentials: true,
        }
      )
      return response.data
    } catch (error) {
      throw handleApiCalendarError(error, 'Не вдалось створити подію: ', this.t)
    }
  }

  async updateEvent(
    eventId: string,
    data: Partial<CreateEventDto & { is_completed: boolean }>
  ): Promise<PersonalEvent[]> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      const payload = { ...data }
      if (
        'description' in payload &&
        (payload.description === null || payload.description === undefined)
      ) {
        payload.description = ''
      }

      const response = await apiClient.patch<PersonalEvent[]>(
        `/user-calendar/personal-events/${eventId}/`,
        payload,
        {
          headers: { 'X-CSRFToken': csrfToken || '' },
          withCredentials: true,
        }
      )
      return response.data
    } catch (error) {
      throw handleApiCalendarError(error, 'Не вдалось оновити подію: ', this.t)
    }
  }

  async deleteEvent(eventId: string): Promise<void> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)
      await apiClient.delete(`/user-calendar/personal-events/${eventId}/`, {
        headers: { 'X-CSRFToken': csrfToken || '' },
        withCredentials: true,
      })
    } catch (error) {
      throw handleApiCalendarError(error, 'Не вдалось видалити подію: ', this.t)
    }
  }
}

export const calendarApiService = new CalendarApiService()
