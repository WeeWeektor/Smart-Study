import { ClassTranslator, ensureCsrfToken } from '@/shared/lib'
import { apiClient } from '@/shared/api'
import axios from 'axios'
import type { CourseTestSummary } from '@/features/test'

export interface StartCourseResponse {
  message: string
  enrollment_id: string
  course_id: string
  progress: number
  is_new: boolean
}

export interface EnrollmentDetailResponse {
  id: string
  course_id: string
  user_id: string
  progress: number
  time_spent: string | number
  last_visited_element_id?: string
  last_visited_element_type?: 'lesson' | 'test'
  is_completed: boolean
  completed_elements: string[]
}

export interface UpdateProgressRequest {
  courseId: string
  elementId?: string
  elementType?: 'lesson' | 'test'
  isCompleted?: boolean
  timeSpent?: number
  finishedCourse?: boolean
}

export interface UpdateProgressResponse {
  message: string
  data: {
    progress: number
    is_completed: boolean
    time_spent: string
    element_id: string
  }
}

export interface EnrollmentStatusResponse {
  id: string
  progress: number
  is_fully_completed: boolean
  is_failed: boolean
  certificate_url: string | null
  course_title: string
  course_description: string
}

class UserCourseEnrollmentService {
  private t = ClassTranslator.translate

  async startCourse(courseId: string): Promise<StartCourseResponse> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      const response = await apiClient.post<StartCourseResponse>(
        `/enrollment/start-course-enrollment/${courseId}/`,
        {
          headers: {
            'X-CSRFToken': csrfToken || '',
          },
          withCredentials: true,
        }
      )

      return response.data
    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        let serverMessage =
          error.response?.data?.message ||
          error.response?.data ||
          this.t('Помилка з’єднання з сервером')

        if (typeof serverMessage === 'string') {
          const match = serverMessage.match(/\['(.+)'\]/)
          if (match && match[1]) {
            serverMessage = match[1]
          }
        }

        throw new Error(this.t('Не вдалось розпочати курс. ') + serverMessage)
      }
      throw new Error(this.t('Невідома помилка при спробі запису на курс.'))
    }
  }

  async getEnrollment(courseId: string): Promise<EnrollmentDetailResponse> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      const response = await apiClient.get<EnrollmentDetailResponse>(
        `/enrollment/enrollment-course/${courseId}/`,
        {
          headers: {
            'X-CSRFToken': csrfToken || '',
          },
          withCredentials: true,
        }
      )

      return response.data
    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        let serverMessage =
          error.response?.data?.message ||
          error.response?.data ||
          this.t('Помилка з’єднання з сервером')

        if (typeof serverMessage === 'string') {
          const match = serverMessage.match(/\['(.+)'\]/)
          if (match && match[1]) {
            serverMessage = match[1]
          }
        }

        throw new Error(
          this.t('Не вдалось завантажити прогрес курсу. ') + serverMessage
        )
      }
      throw new Error(
        this.t('Невідома помилка при спробі отримання прогресу курсу.')
      )
    }
  }

  async updateProgress({
    courseId,
    elementId,
    elementType,
    isCompleted = false,
    timeSpent,
    finishedCourse = false,
  }: UpdateProgressRequest): Promise<UpdateProgressResponse> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      const response = await apiClient.patch<UpdateProgressResponse>(
        `/enrollment/update-enrollment-progress/${courseId}/`,
        {
          element_id: elementId,
          element_type: elementType,
          is_completed: isCompleted,
          time_spent: timeSpent,
          finished_course: finishedCourse,
        },
        {
          headers: {
            'X-CSRFToken': csrfToken || '',
          },
          withCredentials: true,
        }
      )

      return response.data
    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        let serverMessage =
          error.response?.data?.message ||
          error.response?.data ||
          this.t('Помилка з’єднання з сервером')

        if (typeof serverMessage === 'string') {
          const match = serverMessage.match(/\['(.+)'\]/)
          if (match && match[1]) {
            serverMessage = match[1]
          }
        }

        throw new Error(this.t('Не вдалось оновити прогрес. ') + serverMessage)
      }
      throw new Error(this.t('Невідома помилка при збереженні прогресу.'))
    }
  }

  async getEnrollmentStatus(
    courseId: string
  ): Promise<EnrollmentStatusResponse> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      const response = await apiClient.get<EnrollmentStatusResponse>(
        `/enrollment/get-enrollment-status/${courseId}/`,
        {
          headers: {
            'X-CSRFToken': csrfToken || '',
          },
          withCredentials: true,
        }
      )

      return response.data
    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        if (error.response?.status === 404) {
          return {
            id: '',
            progress: 0,
            is_fully_completed: false,
            is_failed: false,
            certificate_url: null,
          } as EnrollmentStatusResponse
        }

        let serverMessage =
          error.response?.data?.message ||
          error.response?.data ||
          this.t('Помилка з’єднання з сервером')

        if (typeof serverMessage === 'string') {
          const match = serverMessage.match(/\['(.+)'\]/)
          if (match && match[1]) {
            serverMessage = match[1]
          }
        }

        throw new Error(
          this.t('Не вдалось перевірити статус проходження курсу. ') +
            serverMessage
        )
      }
      throw new Error(this.t('Невідома помилка при перевірці статусу курсу.'))
    }
  }

  async getCourseTestResults(courseId: string): Promise<CourseTestSummary[]> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      const response = await apiClient.get<{ results: CourseTestSummary[] }>(
        `/enrollment/get-test-results/${courseId}/`,
        {
          headers: {
            'X-CSRFToken': csrfToken || '',
          },
          withCredentials: true,
        }
      )

      return response.data.results
    } catch {
      return []
    }
  }
}

export const userCourseEnrollmentService = new UserCourseEnrollmentService()
