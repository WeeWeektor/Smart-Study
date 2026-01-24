import { ClassTranslator, ensureCsrfToken } from '@/shared/lib'
import { apiClient } from '@/shared/api'
import axios from 'axios'

export interface AddCourseToWishlistRequest {
  courseId: string
}

export interface AddCourseToWishlistResponse {
  message: string
  status: number
  user_id?: string
  course_id?: string
}

class AddCourseToWishlistService {
  private t = ClassTranslator.translate

  async addCourseToWishlist({
    courseId,
  }: AddCourseToWishlistRequest): Promise<AddCourseToWishlistResponse> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      const response = await apiClient.post<AddCourseToWishlistResponse>(
        `/wishlist/add-course-to-wishlist/${courseId}/`,
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
        user_id: response.data.user_id,
        course_id: response.data.course_id,
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
          this.t('Не вдалось додати курс у вішліст') + serverMessage
        )
      }
      throw new Error(this.t('Невідома помилка при додаванні курсу у вішліст'))
    }
  }
}

export const addCourseToWishlistService = new AddCourseToWishlistService()
