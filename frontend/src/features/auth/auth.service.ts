import type { ApiResponse, User } from '@/shared/api'
import { apiClient, tokenService } from '@/shared/api'
import axios from 'axios'
import { ClassTranslator } from '@/shared/lib/i18n/class-translator'
import { ensureCsrfToken, getCookie } from '@/shared/lib'

apiClient.interceptors.request.use(config => {
  const csrfToken = getCookie('csrftoken')
  if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken
  }
  return config
})

export interface LoginRequest {
  email: string
  password: string
  rememberMe?: boolean
}

export interface RegisterRequest {
  email: string
  password: string
  name: string
  surname: string
  phone_number?: string | null
  role: 'student' | 'teacher'
  email_notifications: boolean
  push_notifications: boolean
}

export interface AuthResponse {
  token: string
  user: User
}

export interface ForgotPasswordRequest {
  email: string
}

export interface ChangePasswordRequest {
  current_password: string
  new_password: string
  confirm_password: string
}

class AuthService {
  private t = ClassTranslator.translate

  async login(credentials: LoginRequest): Promise<ApiResponse<AuthResponse>> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      if (!csrfToken) {
        throw new Error(this.t('Не вдалося отримати CSRF токен'))
      }

      const loginResponse = await apiClient.post('/auth/login/', credentials, {
        headers: {
          'X-CSRFToken': csrfToken,
        },
        withCredentials: true,
      })

      if (loginResponse.data.token) {
        tokenService.setToken(loginResponse.data.token, credentials.rememberMe)
      }

      if (
        loginResponse.data.redirect &&
        (loginResponse.data.user.is_staff ||
          loginResponse.data.user.is_superuser)
      ) {
        window.location.href = loginResponse.data.redirect || '/profile/'
        return {
          data: {
            token: loginResponse.data.token,
            user: loginResponse.data.user,
          },
          status: 'success',
          message: this.t('Вхід успішний'),
        }
      }

      return {
        data: {
          token: loginResponse.data.token,
          user: loginResponse.data.user,
        },
        status: 'success',
        message: this.t('Вхід успішний'),
      }
    } catch (error: unknown) {
      if (axios.isAxiosError(error) && error.response) {
        if (error.response.status === 401) {
          throw new Error(this.t('Невірний email або пароль'))
        } else if (error.response.status === 400) {
          throw new Error(this.t('Перевірте правильність введених даних'))
        } else if (error.response.status === 403) {
          throw new Error(
            this.t('Помилка CSRF перевірки. Спробуйте оновити сторінку')
          )
        } else if (error.response.status === 429) {
          throw new Error(this.t('Забагато спроб входу. Спробуйте пізніше.'))
        } else {
          throw new Error(this.t('Помилка сервера: ') + error.response.status)
        }
      } else if (axios.isAxiosError(error) && error.request) {
        if (error.message.includes('ERR_CERT_AUTHORITY_INVALID')) {
          throw new Error(
            this.t(
              'Помилка валідації SSL сертифіката. Додайте сертифікат до довірених або використайте HTTP для розробки.'
            )
          )
        }
        throw new Error(
          this.t("Сервер не відповідає. Перевірте з'єднання з інтернетом")
        )
      } else {
        throw new Error(this.t('Невідома помилка при спробі входу'))
      }
    }
  }

  async register(data: RegisterRequest): Promise<ApiResponse<AuthResponse>> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      if (!csrfToken) {
        throw new Error(this.t('Не вдалося отримати CSRF токен'))
      }

      await apiClient.post('/auth/register/', data, {
        headers: {
          'X-CSRFToken': csrfToken,
        },
        withCredentials: true,
      })

      try {
        const loginResponse = await apiClient.post<{
          access: string
          refresh: string
          token?: string
          user?: User
        }>(
          '/auth/login/',
          {
            email: data.email,
            password: data.password,
          },
          {
            headers: {
              'X-CSRFToken': csrfToken,
            },
            withCredentials: true,
          }
        )

        const token =
          loginResponse.data.access || loginResponse.data.token || ''
        if (token) {
          tokenService.setToken(token)
        }

        window.location.href = '/?showEmailVerification=true'

        return {
          data: {
            token,
            user: loginResponse.data.user || ({} as User),
          },
          status: 'success',
          message: this.t('Реєстрація успішна!'),
        }
      } catch (loginError) {
        window.location.href = '/?showEmailVerification=true'

        return {
          data: { token: '', user: {} as User },
          status: 'success',
          message: this.t('Реєстрація успішна!'),
        }
      }
    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        if (error.response && error.response.status === 409) {
          throw new Error(this.t('Користувач з таким email вже існує'))
        } else if (error.response && error.response.status === 429) {
          throw new Error(
            this.t('Забагато спроб реєстрації. Спробуйте пізніше.')
          )
        } else if (error.response && error.response.status === 403) {
          throw new Error(
            this.t('Помилка CSRF перевірки. Спробуйте оновити сторінку')
          )
        } else if (
          error.response &&
          error.response.data &&
          typeof error.response.data === 'object' &&
          'message' in error.response.data
        ) {
          const message = String(error.response.data.message)
          throw new Error(message)
        }
      }

      if (error instanceof Error) {
        throw new Error(
          error.message || this.t('Помилка при реєстрації. Спробуйте ще раз.')
        )
      }

      throw new Error(this.t('Невідома помилка під час реєстрації'))
    }
  }

  async forgotPassword(
    data: ForgotPasswordRequest
  ): Promise<ApiResponse<{ message: string }>> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      if (!csrfToken) {
        throw new Error(this.t('Не вдалося отримати CSRF токен'))
      }

      const response = await apiClient.post<ApiResponse<{ message: string }>>(
        '/auth/forgot-password/',
        data,
        {
          headers: {
            'X-CSRFToken': csrfToken,
          },
          withCredentials: true,
        }
      )

      return {
        data: { message: response.data.message || '' },
        status: 'success',
        message: this.t(
          'Інструкції для скидання пароля надіслано на вашу пошту'
        ),
      }
    } catch (error: unknown) {
      if (axios.isAxiosError(error) && error.response?.status === 429) {
        throw new Error(this.t('Забагато спроб. Спробуйте пізніше.'))
      } else if (error instanceof Error) {
        throw new Error(error.message || this.t('Не вдалося скинути пароль'))
      }

      throw new Error(this.t('Невідома помилка під час скидання пароля'))
    }
  }

  async resetPassword(
    token: string,
    newPassword: string
  ): Promise<ApiResponse<{ message: string }>> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      if (!csrfToken) {
        throw new Error(this.t('Не вдалося отримати CSRF токен'))
      }

      const response = await apiClient.post<ApiResponse<{ message: string }>>(
        '/auth/reset-password/',
        {
          token,
          password: newPassword,
        },
        {
          headers: {
            'X-CSRFToken': csrfToken,
          },
          withCredentials: true,
        }
      )

      return {
        data: { message: response.data.message || '' },
        status: 'success',
        message: this.t('Пароль успішно змінено'),
      }
    } catch (error: unknown) {
      console.error('Помилка зміни паролю:', error)

      if (axios.isAxiosError(error) && error.response?.status === 429) {
        throw new Error(this.t('Забагато спроб. Спробуйте пізніше.'))
      } else if (error instanceof Error) {
        throw new Error(error.message || this.t('Не вдалося змінити пароль'))
      }
      throw new Error(this.t('Невідома помилка під час зміни пароля'))
    }
  }

  async logout(): Promise<void> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      if (!csrfToken) {
        console.warn('Не вдалося отримати CSRF токен для виходу')
      }

      await apiClient.post(
        '/auth/logout/',
        {},
        {
          headers: {
            'X-CSRFToken': csrfToken || '',
          },
          withCredentials: true,
        }
      )
    } catch (error: unknown) {
      console.error('Помилка при виході:', error)
    } finally {
      tokenService.removeToken()
    }
  }

  async providerOAuth(data: {
    credential: string
    role?: string
    surname?: string
    name?: string
    phone_number?: string | null
    password?: string
    email_notifications?: boolean
    push_notifications?: boolean
    provider: 'google' | 'facebook' | undefined
  }): Promise<{
    access?: string
    refresh?: string
    user?: User
    message?: string
  }> {
    const csrfToken = await ensureCsrfToken(this.t)
    if (!csrfToken) {
      throw new Error(this.t('Не вдалося отримати CSRF токен'))
    }

    try {
      const response = await apiClient.post(
        `/auth/${data.provider}-oauth/`,
        data,
        {
          headers: {
            'X-CSRFToken': csrfToken,
          },
          withCredentials: true,
        }
      )

      return response.data
    } catch (error: any) {
      console.error('[AuthService] Помилка в providerOAuth:', error)
      throw error
    }
  }

  isAuthenticated(): boolean {
    return tokenService.isAuthenticated()
  }

  getToken(): string | null {
    return tokenService.getToken()
  }
}

export const authService = new AuthService()
