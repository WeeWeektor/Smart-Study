import { ClassTranslator, ensureCsrfToken } from '@/shared/lib'
import { apiClient } from '@/shared/api'

export interface ChoicesResponse {
  levels: Record<string, string>[]
  category: Record<string, string>[]
  lesson_content_types: Record<string, string>[]
}

class ChoicesGetService {
  private t = ClassTranslator.translate

  async getChoices(): Promise<ChoicesResponse> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      const response = await apiClient.get<ChoicesResponse>(
        '/choices/choices-get/',
        {
          headers: {
            'X-CSRFToken': csrfToken || '',
          },
          withCredentials: true,
        }
      )
      return response.data
    } catch (error) {
      throw new Error(this.t('Не вдалося завантажити варіанти вибору') + error)
    }
  }
}

export const choicesGetService = new ChoicesGetService()
