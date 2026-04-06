import type { ApiResponse } from '@/shared/api'
import { apiClient, tokenService } from '@/shared/api'
import {
  type ProfileData,
  type UpdateProfileRequest,
  type UpdateProfileResponse,
} from './model'
import { ClassTranslator } from '@/shared/lib/i18n'
import { ensureCsrfToken } from '@/shared/lib'

class ProfileService {
  private t = ClassTranslator.translate

  async getProfile(): Promise<ApiResponse<ProfileData | null>> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

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
    } catch (error: any) {
      if (error.response?.status === 401) {
        return {
          data: null as any,
          status: 'error',
          message: 'Unauthorized',
        }
      }
      throw new Error(this.t('Не вдалося завантажити профіль') + error)
    }
  }

  async updateProfile(
    data: UpdateProfileRequest
  ): Promise<ApiResponse<ProfileData>> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      const response = await apiClient.patch<UpdateProfileResponse>(
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
        data: response.data.profile_data,
        status: 'success',
        message: this.t('Профіль оновлено успішно'),
      }
    } catch (error) {
      throw new Error(this.t('Не вдалося оновити профіль') + error)
    }
  }

  async uploadProfilePicture(
    file: File
  ): Promise<ApiResponse<{ url: string }>> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

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
      throw new Error(this.t('Не вдалося завантажити фото профілю: ') + error)
    }
  }

  async deleteProfile(): Promise<void> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      await apiClient.delete('/user/profile/', {
        headers: {
          'X-CSRFToken': csrfToken || '',
        },
        withCredentials: true,
      })
      tokenService.removeToken()
    } catch (error) {
      throw new Error(this.t('Не вдалося видалити профіль') + error)
    }
  }

  async changePassword(data: {
    current_password: string
    new_password: string
    confirm_password: string
  }): Promise<ApiResponse<{ message: string }>> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

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

      return {
        data: response.data,
        status: 'success',
        message: this.t('Пароль змінено успішно'),
      }
    } catch (error) {
      throw new Error(this.t('Не вдалося змінити пароль') + ': ' + error)
    }
  }

  async getLearningStats(): Promise<
    ApiResponse<{
      coursesCompleted: number
      coursesInProgress: number
      totalTests: number
      completedTopics: number
      certificates: number
    }>
  > {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      const response = await apiClient.get('/user/profile/learning-stats/', {
        headers: {
          'X-CSRFToken': csrfToken || '',
        },
        withCredentials: true,
      })

      return {
        data: response.data,
        status: 'success',
        message: this.t('Статистику завантажено успішно'),
      }
    } catch (error) {
      throw new Error(
        this.t('Не вдалося завантажити статистику навчання') + error
      )
    }
  }
}

export const profileService = new ProfileService()
