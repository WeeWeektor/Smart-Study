import { ClassTranslator, ensureCsrfToken } from '@/shared/lib'
import { apiClient } from '@/shared/api'

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
    } catch (error) {
      throw new Error(this.t('Курс не вдалось видалити') + error)
    }
  }
}

export const deleteCourseService = new DeleteCourseService()
