export const API_BASE_URL = 'https://localhost:8000/api'

export const APP_CONFIG = {
  name: 'Smart Study',
  version: '1.0.0',
  api: {
    baseUrl: API_BASE_URL,
    timeout: 10000,
  },
} as const
