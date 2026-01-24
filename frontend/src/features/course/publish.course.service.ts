import { ClassTranslator, ensureCsrfToken } from '@/shared/lib'
import { apiClient } from '@/shared/api'
import axios from 'axios'

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

        throw new Error(this.t('Не вдалось опублікувати курс') + serverMessage)
      }
      throw new Error(this.t('Невідома помилка при публікації курсу.'))
    }
  }
}

export const publishCourseService = new PublishCourseService()
