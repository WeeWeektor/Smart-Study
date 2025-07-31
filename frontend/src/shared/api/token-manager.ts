import { apiClient } from './api-client'

class TokenManager {
  private readonly TOKEN_KEY = 'auth_token'
  private readonly REFRESH_TOKEN_KEY = 'refresh_token'

  setToken(token: string, rememberMe: boolean = true): void {
    if (rememberMe) {
      localStorage.setItem(this.TOKEN_KEY, token)
    } else {
      sessionStorage.setItem(this.TOKEN_KEY, token)
    }
  }

  getToken(): string | null {
    return (
      localStorage.getItem(this.TOKEN_KEY) ||
      sessionStorage.getItem(this.TOKEN_KEY)
    )
  }

  setRefreshToken(refreshToken: string, rememberMe: boolean = true): void {
    if (rememberMe) {
      localStorage.setItem(this.REFRESH_TOKEN_KEY, refreshToken)
    } else {
      sessionStorage.setItem(this.REFRESH_TOKEN_KEY, refreshToken)
    }
  }

  getRefreshToken(): string | null {
    return (
      localStorage.getItem(this.REFRESH_TOKEN_KEY) ||
      sessionStorage.getItem(this.REFRESH_TOKEN_KEY)
    )
  }

  removeToken(): void {
    localStorage.removeItem(this.TOKEN_KEY)
    sessionStorage.removeItem(this.TOKEN_KEY)
    localStorage.removeItem(this.REFRESH_TOKEN_KEY)
    sessionStorage.removeItem(this.REFRESH_TOKEN_KEY)
  }

  isAuthenticated(): boolean {
    return !!this.getToken()
  }

  setupInterceptors(): void {
    apiClient.interceptors.request.use(
      config => {
        const token = this.getToken()
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      error => {
        return Promise.reject(error)
      }
    )

    apiClient.interceptors.response.use(
      response => response,
      error => {
        if (error.response?.status === 401) {
          this.removeToken()
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  initializeToken() {
    this.setupInterceptors()
  }
}

export const tokenService = new TokenManager()

export { TokenManager }

tokenService.initializeToken()
