import axios from 'axios'
import { LANGUAGE_STORAGE_KEY } from '@/shared/lib'

export const apiClient = axios.create({
  baseURL: '/api',
  withCredentials: true,
})

apiClient.interceptors.request.use(
  config => {
    const language = localStorage.getItem(LANGUAGE_STORAGE_KEY) || 'en'

    config.headers['Accept-Language'] = language
    config.headers['X-Language'] = language
    config.headers['Content-Language'] = language

    return config
  },
  error => {
    return Promise.reject(error)
  }
)

apiClient.interceptors.response.use(
  response => {
    const backendLanguage = response.headers['x-current-language']
    if (
      backendLanguage &&
      backendLanguage !== localStorage.getItem(LANGUAGE_STORAGE_KEY)
    ) {
      localStorage.setItem(LANGUAGE_STORAGE_KEY, backendLanguage)
      window.dispatchEvent(
        new CustomEvent('languageChanged', { detail: backendLanguage })
      )
    }

    return response
  },
  error => {
    if (error.response) {
      if (error.response.status === 401) {
        console.warn('Необхідна автентифікація')
      } else if (error.response.status === 403) {
        console.warn('CSRF помилка або відмовлено в доступі')
      }
    }
    return Promise.reject(error)
  }
)
