import type { ApiResponse } from '@/shared/api'
import { apiClient, tokenService } from '@/shared/api'
import { type ProfileData, type UpdateProfileRequest } from './model'
import { ClassTranslator } from '@/shared/lib/i18n'

function getCookie(name: string): string | undefined {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) {
    const part = parts.pop()
    return part ? part.split(';').shift() : undefined
  }
  return undefined
}

class ProfileService {
  private t = ClassTranslator.translate

  async ensureCsrfToken(): Promise<string | null> {
    try {
      let csrfToken = getCookie('csrftoken')

      if (!csrfToken) {
        await apiClient.get('/auth/get-csrf-token/')
        await new Promise(resolve => setTimeout(resolve, 100))
        csrfToken = getCookie('csrftoken')
      }

      return csrfToken || null
    } catch (error) {
      console.error(this.t('Помилка отримання CSRF токена:'), error)
      return null
    }
  }

  async getProfile(): Promise<ApiResponse<ProfileData>> {
    try {
      const csrfToken = await this.ensureCsrfToken()

      const response = await apiClient.get<ProfileData>('/user/profile/', {
        headers: {
          'X-CSRFToken': csrfToken || '',
        },
        withCredentials: true,
      })

      return {
        data: response.data,
        status: 'success',
        message: this.t('Профіль завантажено успішно'),
      }
    } catch (error) {
      console.error(this.t('Помилка завантаження профілю:'), error)
      throw new Error(this.t('Не вдалося завантажити профіль') + error)
    }
  }

  async updateProfile(
    data: UpdateProfileRequest
  ): Promise<ApiResponse<ProfileData>> {
    try {
      const csrfToken = await this.ensureCsrfToken()

      const response = await apiClient.patch<ProfileData>(
        '/user/profile/',
        data,
        {
          headers: {
            'X-CSRFToken': csrfToken || '',
          },
          withCredentials: true,
        }
      )

      return {
        data: response.data,
        status: 'success',
        message: this.t('Профіль оновлено успішно'),
      }
    } catch (error) {
      console.error(this.t('Помилка оновлення профілю:'), error)
      throw new Error(this.t('Не вдалося оновити профіль') + error)
    }
  }

  async uploadProfilePicture(
    file: File
  ): Promise<ApiResponse<{ url: string }>> {
    try {
      const csrfToken = await this.ensureCsrfToken()

      const formData = new FormData()
      formData.append('profile_picture', file)

      const response = await apiClient.post(
        '/user/profile/upload-avatar/',
        formData,
        {
          headers: {
            'X-CSRFToken': csrfToken || '',
          },
          withCredentials: true,
        }
      )

      return {
        data: response.data,
        status: 'success',
        message: this.t('Фото профілю завантажено успішно'),
      }
    } catch (error) {
      console.error(this.t('Помилка завантаження фото профілю:'), error)
      throw new Error(this.t('Не вдалося завантажити фото профілю: ') + error)
    }
  }

  async deleteProfile(): Promise<void> {
    try {
      const csrfToken = await this.ensureCsrfToken()

      await apiClient.delete('/user/profile/', {
        headers: {
          'X-CSRFToken': csrfToken || '',
        },
        withCredentials: true,
      })
      tokenService.removeToken()
    } catch (error) {
      console.error(this.t('Помилка видалення профілю:'), error)
      throw new Error(this.t('Не вдалося видалити профіль') + error)
    }
  }

  async changePassword(data: {
    current_password: string
    new_password: string
    confirm_password: string
  }): Promise<ApiResponse<{ message: string }>> {
    try {
      const csrfToken = await this.ensureCsrfToken()

      const response = await apiClient.patch<{ message: string }>(
        '/user/change-password/',
        data,
        {
          headers: {
            'X-CSRFToken': csrfToken || '',
          },
          withCredentials: true,
        }
      )
      console.log(response)

      return {
        data: response.data,
        status: 'success',
        message: this.t('Пароль змінено успішно'),
      }
    } catch (error) {
      console.error(this.t('Помилка зміни паролю:'), error)
      throw new Error(this.t('Не вдалося змінити пароль') + ': ' + error)
    }
  }
}

export const profileService = new ProfileService()
