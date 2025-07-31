import { apiClient, tokenService } from '@/shared/api'
import type { ApiResponse } from '@/shared/api'
import { type ProfileData, type UpdateProfileRequest } from './model'

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
      console.error('Помилка отримання CSRF токена:', error)
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
        message: 'Профіль завантажено успішно',
      }
    } catch (error) {
      console.error('Помилка завантаження профілю:', error)
      throw new Error('Не вдалося завантажити профіль')
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
        message: 'Профіль оновлено успішно',
      }
    } catch (error) {
      console.error('Помилка оновлення профілю:', error)
      throw new Error('Не вдалося оновити профіль')
    }
  }

  async uploadProfilePicture(
    file: File
  ): Promise<ApiResponse<{ url: string }>> {
    console.log('Викликано uploadProfilePicture, file:', file)
    try {
      const csrfToken = await this.ensureCsrfToken()

      const formData = new FormData()
      formData.append('profile_picture', file)
      console.log('formData entries:', [...formData.entries()])

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
        message: 'Фото профілю завантажено успішно',
      }
    } catch (error) {
      console.error('Помилка завантаження фото профілю:', error)
      throw new Error('Не вдалося завантажити фото профілю')
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
      console.error('Помилка видалення профілю:', error)
      throw new Error('Не вдалося видалити профіль')
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
        message: 'Пароль змінено успішно',
      }
    } catch (error) {
      console.error('Помилка зміни паролю:', error)
      throw new Error('Не вдалося змінити пароль')
    }
  }
}

export const profileService = new ProfileService()
