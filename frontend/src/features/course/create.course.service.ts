import { ClassTranslator, ensureCsrfToken } from '@/shared/lib'
import { apiClient } from '@/shared/api'
import axios from 'axios'

export interface CreateCourseResponse {
  message: string
  status: number
}

class CreateCourseService {
  private t = ClassTranslator.translate

  async createCourse(requestData: {
    title: string
    description: string
    category: string
    is_published: boolean
    level: string
    course_language: string
    time_to_complete: string
    cover_imageFile?: File | null
  }): Promise<CreateCourseResponse> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      const formData = new FormData()
      const { cover_imageFile, ...data } = requestData
      formData.append('data', JSON.stringify(data))
      if (cover_imageFile) {
        formData.append('cover_image', cover_imageFile)
      }

      const response = await apiClient.post<CreateCourseResponse>(
        `/course/create-course/`,
        formData,
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

        throw new Error(this.t('Не вдалось зберегти курс: ') + serverMessage)
      }
      throw new Error(this.t('Невідома помилка при створенні курсу'))
    }
  }
}

export const createCourseService = new CreateCourseService()
