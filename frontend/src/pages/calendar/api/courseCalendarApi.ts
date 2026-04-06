import { ClassTranslator, ensureCsrfToken } from '@/shared/lib'
import { apiClient, handleApiCalendarError } from '@/shared/api'

export interface CourseEvent {
  id: string
  course: string
  course_title: string
  module?: string
  lesson?: string
  module_test?: string
  course_test?: string
  event_date: string
  note: string
  link: string | null
  is_completed: boolean
  is_personal: boolean
}

export interface BulkCreateCourseEventsResponse {
  created_count: number
  events: CourseEvent[]
}

export interface CoursePlanningBulkDto {
  [key: string]:
    | {
        course: string
        event_date: string
        note: string
        type: string
        link: string
        module_id?: string
        lesson_id?: string
        module_test_id?: string
        course_test_id?: string
      }
    | string
}

class CourseCalendarApiService {
  private t = ClassTranslator.translate

  async getCourseEvents(): Promise<CourseEvent[]> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)
      const response = await apiClient.get<CourseEvent[]>(
        '/user-calendar/course-events/',
        {
          headers: { 'X-CSRFToken': csrfToken || '' },
          withCredentials: true,
        }
      )
      return response.data
    } catch (error) {
      throw handleApiCalendarError(
        error,
        'Не вдалось завантажити план навчання: ',
        this.t
      )
    }
  }

  async bulkCreateCourseEvents(
    data: CoursePlanningBulkDto
  ): Promise<BulkCreateCourseEventsResponse> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)
      const response = await apiClient.post<BulkCreateCourseEventsResponse>(
        '/user-calendar/course-events/',
        data,
        {
          headers: { 'X-CSRFToken': csrfToken || '' },
          withCredentials: true,
        }
      )
      return response.data
    } catch (error) {
      throw handleApiCalendarError(
        error,
        'Не вдалось сформувати графік навчання: ',
        this.t
      )
    }
  }

  async deleteCourseEvent(eventId: string): Promise<void> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)
      await apiClient.delete(`/user-calendar/course-events/${eventId}/`, {
        headers: { 'X-CSRFToken': csrfToken || '' },
        withCredentials: true,
      })
    } catch (error) {
      throw handleApiCalendarError(
        error,
        'Не вдалось видалити подію з графіка: ',
        this.t
      )
    }
  }
}

export const courseCalendarApiService = new CourseCalendarApiService()
