import { ClassTranslator, ensureCsrfToken } from '@/shared/lib'
import { apiClient } from '@/shared/api'

export interface UserInfoResponse {
  profile_picture?: string
  phone_number?: string
  email?: string
  location?: string
  organization?: string
  specialization?: string
  education_level?: string
  bio?: string
}

export interface UserInfoRequest {
  userId: string
}

class UserGetService {
  private t = ClassTranslator.translate

  async getUserInfo({ userId }: UserInfoRequest): Promise<UserInfoResponse> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      const response = await apiClient.get<UserInfoResponse>(
        `/user/user-info/${userId}/`,
        {
          headers: {
            'X-CSRFToken': csrfToken || '',
          },
          withCredentials: true,
        }
      )

      return response.data
    } catch (error) {
      throw new Error(this.t('Не вдалося завантажити користувача') + error)
    }
  }
}

export const userGetService = new UserGetService()
