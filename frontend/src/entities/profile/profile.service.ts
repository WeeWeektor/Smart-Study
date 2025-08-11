import { apiClient, tokenService } from '@/shared/api'
import type { ApiResponse } from '@/shared/api'
import { type ProfileData, type UpdateProfileRequest } from './model'
import {
  DEFAULT_LANGUAGE,
  LANGUAGE_STORAGE_KEY,
  getNestedTranslation,
  interpolate,
  translations,
} from '@/shared/lib/i18n'

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
  private translate(
    key: string,
    params?: Record<string, string | number>
  ): string {
    try {
      const storedLanguage = localStorage.getItem(LANGUAGE_STORAGE_KEY)
      const language =
        storedLanguage === 'en' || storedLanguage === 'uk'
          ? storedLanguage
          : DEFAULT_LANGUAGE.code
      const template = getNestedTranslation(translations[language], key)
      return params ? interpolate(template, params) : template
    } catch {
      return key
    }
  }

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
      console.error(this.translate('errors.csrfTokenFetchError'), error)
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
        message: this.translate('profile.profileLoaded'),
      }
    } catch (error) {
      console.error(this.translate('profile.profileLoadError'), error)
      throw new Error(this.translate('profile.profileLoadError'))
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
        message: this.translate('profile.profileUpdated'),
      }
    } catch (error) {
      console.error(this.translate('profile.profileUpdateError'), error)
      throw new Error(this.translate('profile.profileUpdateError'))
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
        message: this.translate('profile.profilePictureUploaded'),
      }
    } catch (error) {
      console.error(this.translate('profile.profilePictureUploadError'), error)
      throw new Error(this.translate('profile.profilePictureUploadError'))
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
      console.error(this.translate('profile.deleteAccountError'), error)
      throw new Error(this.translate('profile.deleteAccountError'))
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
        message: this.translate('auth.passwordChanged'),
      }
    } catch (error) {
      console.error(this.translate('auth.passwordChangeError'), error)
      throw new Error(this.translate('auth.passwordChangeError'))
    }
  }
}

export const profileService = new ProfileService()
