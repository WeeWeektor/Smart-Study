import { ClassTranslator, ensureCsrfToken } from '@/shared/lib'
import { apiClient } from '@/shared/api'
import axios from 'axios'

export interface StudentStatItem {
  id: string
  name: string
  email: string
  progress: number
  status: 'in_progress' | 'success' | 'failed'
  joined_at: string
}

export interface CourseStatistics {
  total_students: number
  total_in_progress_course_students: number
  total_completed_course_students: number
  total_success_complete: number
  total_failed_complete: number
  average_rating: number
  total_reviews: number
  students: StudentStatItem[]
}

class CourseStatisticForOwnerService {
  private t = ClassTranslator.translate

  async getStatistic(courseId: string): Promise<CourseStatistics> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      const response = await apiClient.get<CourseStatistics>(
        `/course/course-statistics-for-owner/${courseId}/`,
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
          this.t('Не вдалось завантажити статистику курсу: ') + serverMessage
        )
      }
      throw new Error(
        this.t('Невідома помилка при спробі отримання статистики.')
      )
    }
  }
}

export const courseStatisticForOwnerService =
  new CourseStatisticForOwnerService()
