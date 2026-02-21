import { ClassTranslator, ensureCsrfToken } from '@/shared/lib'
import { apiClient, handleApiError } from '@/shared/api'

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
      throw handleApiError(
        error,
        'Не вдалось додати курс у вішліст: ',
        this.t,
        'Невідома помилка при додаванні курсу у вішліст'
      )
    }
  }
}

export const addCourseToWishlistService = new AddCourseToWishlistService()
