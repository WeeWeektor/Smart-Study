import { apiClient } from '@/shared/api'
import { ClassTranslator, ensureCsrfToken } from '@/shared/lib'
import type {
  CreateReviewRequest,
  CreateReviewResponse,
  GetReviewsResponse,
  Review,
} from '@/features/course/types.ts'

class CourseReviewService {
  private t = ClassTranslator.translate

  async getReviews(courseId: string): Promise<Review[]> {
    try {
      const response = await apiClient.get<GetReviewsResponse>(
        `/course-review/get_reviews/`,
        {
          params: { course_id: courseId },
          withCredentials: true,
        }
      )
      return response.data.reviews
    } catch (error) {
      throw new Error(
        this.t('Не вдалось завантажити відгуки курсу: ') +
          (error instanceof Error ? error.message : String(error))
      )
    }
  }

  async createReview(data: CreateReviewRequest): Promise<Review> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      const response = await apiClient.post<CreateReviewResponse>(
        `/course-review/create-review/`,
        data,
        {
          headers: {
            'X-CSRFToken': csrfToken || '',
          },
          withCredentials: true,
        }
      )

      return response.data.review
    } catch (error) {
      const err = error as any

      const errorMessage =
        err.response?.data?.message ||
        (err instanceof Error ? err.message : String(err))

      throw new Error(this.t('Не вдалось створити відгук: ') + errorMessage)
    }
  }
}

export const courseReviewService = new CourseReviewService()
