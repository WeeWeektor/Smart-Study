import { ClassTranslator, ensureCsrfToken } from '@/shared/lib'
import { apiClient, handleApiError } from '@/shared/api'
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
      throw handleApiError(
        error,
        'Не вдалось завантажити рекомендовані курси: ',
        this.t,
        'Невідома помилка при спробі отримання рекомендованих курсів'
      )
    }
  }
}

export const courseRecommendationsService = new CourseRecommendationsService()
