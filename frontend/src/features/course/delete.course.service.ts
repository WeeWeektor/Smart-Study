import { ClassTranslator, ensureCsrfToken } from '@/shared/lib'
import { apiClient } from '@/shared/api'
import axios from 'axios'

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

        throw new Error(this.t('Курс не вдалось видалити') + serverMessage)
      }
      throw new Error(this.t('Невідома помилка при видаленні курсу'))
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
          this.t('Курс з вішліста не вдалось видалити') + serverMessage
        )
      }
      throw new Error(this.t('Невідома помилка при видаленні курсу з вішліста'))
    }
  }
}

export const deleteCourseService = new DeleteCourseService()
