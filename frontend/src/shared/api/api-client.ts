import axios from 'axios'

export const apiClient = axios.create({
  baseURL: 'https://localhost:8000/api',
  withCredentials: true,
})

apiClient.interceptors.request.use(
  config => {
    config.headers['Accept-Language'] =
      localStorage.getItem('smartStudy_language') || 'en'
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

apiClient.interceptors.response.use(
  response => {
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
