import { apiClient, tokenService } from '@/shared/api'
import type { User, ApiResponse } from '@/shared/api'
import axios from 'axios'
import {
  DEFAULT_LANGUAGE,
  LANGUAGE_STORAGE_KEY,
  translations,
} from '@/shared/lib/i18n'
import { getNestedTranslation, interpolate } from '@/shared/lib/i18n/utils'

function getCookie(name: string): string | undefined {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) {
    const part = parts.pop()
    return part ? part.split(';').shift() : undefined
  }
  return undefined
}

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

      console.log('CSRF токен:', csrfToken || 'не знайдено')
      return csrfToken || null
    } catch (error) {
      console.error(this.translate('errors.csrfTokenFetchError'), error)
      return null
    }
  }

  async login(credentials: LoginRequest): Promise<ApiResponse<AuthResponse>> {
    try {
      const csrfToken = await this.ensureCsrfToken()

      if (!csrfToken) {
        throw new Error(this.translate('errors.csrfTokenFetchError'))
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
          message: this.translate('auth.loginSuccess'),
        }
      }

      return {
        data: {
          token: loginResponse.data.token,
          user: loginResponse.data.user,
        },
        status: 'success',
        message: this.translate('auth.loginSuccess'),
      }
    } catch (error: unknown) {
      console.error('Помилка входу:', error)

      if (axios.isAxiosError(error) && error.response) {
        console.error('Дані відповіді:', error.response.data)
        console.error('Статус відповіді:', error.response.status)

        if (error.response.status === 401) {
          throw new Error(this.translate('errors.unauthorized'))
        } else if (error.response.status === 400) {
          throw new Error(this.translate('validation.invalidData'))
        } else if (error.response.status === 403) {
          throw new Error(this.translate('errors.csrfError'))
        } else {
          throw new Error(this.translate('errors.serverError'))
        }
      } else if (axios.isAxiosError(error) && error.request) {
        if (error.message.includes('ERR_CERT_AUTHORITY_INVALID')) {
          throw new Error(this.translate('errors.serverError'))
        }
        throw new Error(this.translate('errors.networkError'))
      } else {
        throw new Error(this.translate('errors.generalError'))
      }
    }
  }

  async register(data: RegisterRequest): Promise<ApiResponse<AuthResponse>> {
    try {
      const csrfToken = await this.ensureCsrfToken()

      if (!csrfToken) {
        throw new Error(this.translate('errors.csrfTokenFetchError'))
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
          message: this.translate('auth.registerSuccess'),
        }
      } catch (loginError) {
        window.location.href = '/?showEmailVerification=true'

        return {
          data: { token: '', user: {} as User },
          status: 'success',
          message: this.translate('auth.registerSuccess'),
        }
      }
    } catch (error: unknown) {
      console.error('Помилка реєстрації:', error)

      if (axios.isAxiosError(error)) {
        if (error.response && error.response.status === 409) {
          throw new Error(this.translate('auth.userExists'))
        } else if (
          error.response &&
          error.response.data &&
          typeof error.response.data === 'object' &&
          'message' in error.response.data
        ) {
          const message = String(error.response.data.message)
          throw new Error(message)
        } else if (error.response && error.response.status === 403) {
          throw new Error(this.translate('errors.csrfError'))
        }
      }

      if (error instanceof Error) {
        throw new Error(error.message || this.translate('errors.generalError'))
      }

      throw new Error(this.translate('errors.generalError'))
    }
  }

  async forgotPassword(
    data: ForgotPasswordRequest
  ): Promise<ApiResponse<{ message: string }>> {
    try {
      const csrfToken = await this.ensureCsrfToken()

      if (!csrfToken) {
        throw new Error(this.translate('errors.csrfTokenFetchError'))
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
        message: this.translate('auth.forgotPasswordInstructionsSent'),
      }
    } catch (error: unknown) {
      console.error('Помилка відновлення паролю:', error)
      if (error instanceof Error) {
        throw new Error(
          error.message || this.translate('auth.passwordChangeError')
        )
      }
      throw new Error(this.translate('errors.generalError'))
    }
  }

  async resetPassword(
    token: string,
    newPassword: string
  ): Promise<ApiResponse<{ message: string }>> {
    try {
      const csrfToken = await this.ensureCsrfToken()

      if (!csrfToken) {
        throw new Error(this.translate('errors.csrfTokenFetchError'))
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
        message: this.translate('auth.passwordChanged'),
      }
    } catch (error: unknown) {
      console.error('Помилка зміни паролю:', error)
      if (error instanceof Error) {
        throw new Error(
          error.message || this.translate('auth.passwordChangeError')
        )
      }
      throw new Error(this.translate('errors.generalError'))
    }
  }

  async logout(): Promise<void> {
    try {
      const csrfToken = await this.ensureCsrfToken()

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
    console.log('[AuthService] providerOAuth викликано з даними:', {
      provider: data.provider,
      hasCredential: !!data.credential,
      role: data.role,
      name: data.name,
      surname: data.surname,
    })

    const csrfToken = await this.ensureCsrfToken()
    if (!csrfToken) {
      console.error('[AuthService] Не вдалося отримати CSRF токен')
      throw new Error(this.translate('errors.csrfTokenFetchError'))
    }

    console.log(
      '[AuthService] CSRF токен отримано, робимо запит до:',
      `/auth/${data.provider}-oauth/`
    )

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

      console.log('[AuthService] Відповідь сервера:', response.data)
      return response.data
    } catch (error: any) {
      console.error('[AuthService] Помилка в providerOAuth:', error)
      console.error('[AuthService] Деталі помилки:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message,
      })
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
