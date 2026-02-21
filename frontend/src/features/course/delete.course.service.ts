import { ClassTranslator, ensureCsrfToken } from '@/shared/lib'
import { apiClient, handleApiError } from '@/shared/api'

export interface DeleteCourseRequest {
  courseId: string
}

export interface DeleteCourseResponse {
  message: string
  status: number
}

class DeleteCourseService {
  private t = ClassTranslator.translate

  async deleteCourse({
    courseId,
  }: DeleteCourseRequest): Promise<DeleteCourseResponse> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      const response = await apiClient.delete<DeleteCourseResponse>(
        `/course/delete-course/${courseId}/`,
        {
          headers: {
            'X-CSRFToken': csrfToken || '',
          },
          withCredentials: true,
        }
      )

      return {
        message: response.data.message,
        status: response.status,
      }
    } catch (error: unknown) {
      throw handleApiError(
        error,
        'Курс не вдалось видалити: ',
        this.t,
        'Невідома помилка при видаленні курсу'
      )
    }
  }

  async deleteCourseFromWishlist({
    courseId,
  }: DeleteCourseRequest): Promise<DeleteCourseResponse> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      const response = await apiClient.delete<DeleteCourseResponse>(
        `/wishlist/remove-course-from-wishlist/${courseId}/`,
        {
          headers: {
            'X-CSRFToken': csrfToken || '',
          },
          withCredentials: true,
        }
      )

      return {
        message: response.data.message,
        status: response.status,
      }
    } catch (error: unknown) {
      throw handleApiError(
        error,
        'Курс з вішліста не вдалось видалити: ',
        this.t,
        'Невідома помилка при видаленні курсу з вішліста'
      )
    }
  }
}

export const deleteCourseService = new DeleteCourseService()
