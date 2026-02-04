import { ClassTranslator, ensureCsrfToken } from '@/shared/lib'
import { apiClient } from '@/shared/api'
import axios from 'axios'

export interface GenerateCertificateResponse {
  message: string
  course_id: string
  id: string
  certificate_id: string
  issued_at: number
  is_valid: boolean
  status: number
}

class UserCourseCertificateService {
  private t = ClassTranslator.translate

  async createCertificate(
    courseId: string
  ): Promise<GenerateCertificateResponse> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      const response = await apiClient.post<GenerateCertificateResponse>(
        `/course/generate-certificate/${courseId}/`,
        {},
        {
          headers: {
            'X-CSRFToken': csrfToken || '',
          },
          withCredentials: true,
        }
      )

      return response.data
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
          this.t('Не вдалось згенерувати сертифікат. ') + serverMessage
        )
      }
      throw new Error(
        this.t('Невідома помилка при спробі генерації сертифікату.')
      )
    }
  }
}

export const userCourseCertificateService = new UserCourseCertificateService()
