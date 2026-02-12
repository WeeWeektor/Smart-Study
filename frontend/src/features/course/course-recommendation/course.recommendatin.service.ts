import { ClassTranslator, ensureCsrfToken } from '@/shared/lib'
import { apiClient } from '@/shared/api'
import axios from 'axios'
import type { CourseWrapper } from '@/features/course'

interface RecommendationsResponse {
  courses_data: CourseWrapper[]
}

class CourseRecommendationsService {
  private t = ClassTranslator.translate

  async getRecommendations(
    courseId: string,
    status: 'passed' | 'failed',
    limit: number = 6
  ): Promise<CourseWrapper[]> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      const response = await apiClient.get<RecommendationsResponse>(
        `/course/course-recommendations/${courseId}/`,
        {
          params: {
            status,
            limit,
          },
          headers: {
            'X-CSRFToken': csrfToken || '',
          },
          withCredentials: true,
        }
      )

      return response.data.courses_data
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
          this.t('Не вдалось завантажити рекомендовані курси ') + serverMessage
        )
      }
      throw new Error(
        this.t('Невідома помилка при спробі отримання рекомендованих курсів.')
      )
    }
  }
}

export const courseRecommendationsService = new CourseRecommendationsService()
