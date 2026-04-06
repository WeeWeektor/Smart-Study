import { ClassTranslator, ensureCsrfToken } from '@/shared/lib'
import { apiClient, handleApiError } from '@/shared/api'

export interface GenerateCertificateResponse {
  message: string
  course_id: string
  id: string
  certificate_id: string
  issued_at: number
  is_valid: boolean
  status: number
}

export interface CertificateVerificationResponse {
  message: string
  status: number
  certificate: CertificateData
}

export interface CertificateData {
  certificate_id: string
  student_name: string
  course_title: string
  issued_at: string
  is_valid: boolean
}

class UserCourseCertificateService {
  private t = ClassTranslator.translate

  async createCertificate(
    courseId: string
  ): Promise<GenerateCertificateResponse> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      const response = await apiClient.post<GenerateCertificateResponse>(
        `/course/create-certificate/${courseId}/`,
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
      throw handleApiError(
        error,
        'Не вдалось згенерувати сертифікат.: ',
        this.t,
        'Невідома помилка при спробі генерації сертифікату'
      )
    }
  }

  async downloadCertificateFile(certificateId: string, format: 'pdf' | 'png') {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      const response = await apiClient.get<Blob>(
        `/course/download-certificate/${certificateId}/`,
        {
          params: { format },
          headers: {
            'X-CSRFToken': csrfToken || '',
            'Cache-Control': 'public',
            Pragma: 'cache',
          },
          withCredentials: true,
          responseType: 'blob',
        }
      )

      return response.data
    } catch (error: unknown) {
      throw handleApiError(
        error,
        'Не вдалось завантажити сертифікат: ',
        this.t,
        'Невідома помилка при спробі завантаження сертифікату'
      )
    }
  }

  async verifyCertificate(certificateId: string) {
    const response = await apiClient.get<CertificateVerificationResponse>(
      `/course/certificates/verify/${certificateId}/`
    )
    return response.data.certificate
  }
}

export const userCourseCertificateService = new UserCourseCertificateService()
