import { ClassTranslator, ensureCsrfToken } from '@/shared/lib'
import { apiClient, handleApiError } from '@/shared/api'

export interface PublishCourseRequest {
  courseId: string
}

export interface PublishCourseResponse {
  message: string
  status: number
  course_id: string
}

class PublishCourseService {
  private t = ClassTranslator.translate

  async publishCourse({
    courseId,
  }: PublishCourseRequest): Promise<PublishCourseResponse> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      const response = await apiClient.post<PublishCourseResponse>(
        `/course/publish-course/${courseId}/`,
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
        course_id: response.data.course_id,
      }
    } catch (error: unknown) {
      throw handleApiError(
        error,
        'Не вдалось опублікувати курс: ',
        this.t,
        'Невідома помилка при публікації курсу'
      )
    }
  }
}

export const publishCourseService = new PublishCourseService()
