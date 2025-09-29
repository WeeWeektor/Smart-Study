import { getCookie } from '@/shared/lib'
import { apiClient } from '@/shared/api'

export async function ensureCsrfToken(
  t?: (key: string) => string
): Promise<string | null> {
  try {
    let csrfToken = getCookie('csrftoken')
    if (!csrfToken) {
      await apiClient.get('/auth/get-csrf-token/')
      await new Promise(resolve => setTimeout(resolve, 100))
      csrfToken = getCookie('csrftoken')
    }
    return csrfToken || null
  } catch (error) {
    console.error(
      t ? t('Помилка отримання CSRF токена:') : 'CSRF token error:',
      error
    )
    return null
  }
}
