import { useEffect, useState } from 'react'
import { authService } from '@/features/auth'
import { tokenService } from '@/shared/api'

interface UseSocialAuthProps {
  onError?: (msg: string) => void
  onGoogleDataReceived?: (data: {
    name: string
    surname: string
    email: string
    credential: string
    password?: string
  }) => void
  onUserExists?: (userData: {
    access?: string
    refresh?: string
    user?: any
    message?: string
  }) => void
}

export function useSocialAuth({
  onError,
  onGoogleDataReceived,
  onUserExists,
}: UseSocialAuthProps) {
  const [isGoogleLoading, setIsGoogleLoading] = useState(false)

  const handleError = (message: string) => {
    if (onError && typeof onError === 'function') {
      onError(message)
    }
  }

  useEffect(() => {
    try {
      // @ts-ignore
      if (window.google && window.google.accounts) {
        // @ts-ignore
        window.google.accounts.id.initialize({
          client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
          callback: handleGoogleResponse,
        })
      } else {
        console.warn('Google API не завантажено')
      }
    } catch (error: any) {
      console.error('Помилка ініціалізації Google Sign-In:', error)
    }
    // eslint-disable-next-line
  }, [])

  const handleGoogleResponse = async (response: any) => {
    setIsGoogleLoading(true)
    handleError('')

    console.log('[GoogleAuth] response:', response)

    let googleData: {
      name: string
      surname: string
      email: string
      credential: string
    } = {
      name: '',
      surname: '',
      email: '',
      credential: response.credential,
    }

    try {
      if (!response.credential) {
        handleError(
          'Google не повернув токен. Спробуйте ще раз або використайте інший спосіб входу.'
        )
        console.error('[GoogleAuth] Відсутній credential у response:', response)
        return
      }

      let payload
      try {
        const base64Url = response.credential.split('.')[1]
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
        const jsonPayload = decodeURIComponent(
          atob(base64)
            .split('')
            .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
            .join('')
        )
        payload = JSON.parse(jsonPayload)
        console.log('[GoogleAuth] Успішно декодовано JWT payload:', payload)
      } catch (jwtErr) {
        handleError('Некоректний токен Google. Спробуйте ще раз.')
        console.error(
          '[GoogleAuth] Некоректний JWT:',
          response.credential,
          jwtErr
        )
        return
      }
      googleData = {
        name: payload.given_name || '',
        surname: payload.family_name || '',
        email: payload.email || '',
        credential: response.credential,
      }
      console.log('[GoogleAuth] Отримані дані з Google:', googleData)

      try {
        const loginRes = await authService.googleOAuth({
          credential: response.credential,
        })
        console.log('[GoogleAuth] Відповідь сервера на googleOAuth:', loginRes)
        if (loginRes.access) {
          if (onUserExists) {
            onUserExists(loginRes)
            return
          }
          tokenService.setToken(loginRes.access)
          if (loginRes.refresh) {
            tokenService.setRefreshToken(loginRes.refresh)
          }
          window.location.href = '/profile'
          return
        }
        if (
          loginRes.user &&
          loginRes.message?.includes('Успішна авторизація')
        ) {
          console.log(
            '[GoogleAuth] Успішна авторизація без access токена, перенаправляємо на профіль'
          )
          if (onUserExists) {
            console.log(
              '[GoogleAuth] Викликаємо onUserExists callback з даними:',
              loginRes
            )
            onUserExists(loginRes)
            return
          }
          console.log('[GoogleAuth] Перенаправляємо на /profile')
          window.location.href = '/profile'
          return
        }
      } catch (loginError: any) {
        console.error(
          '[GoogleAuth] Помилка googleOAuth:',
          loginError,
          loginError?.response
        )

        if (onGoogleDataReceived) {
          onGoogleDataReceived(googleData)
          return
        }

        if (
          loginError.response?.status === 409 ||
          loginError.response?.data?.error?.includes('already exists')
        ) {
          handleError(
            'Користувач з цією поштою вже існує. Будь ласка, увійдіть через Google.'
          )
          return
        }

        if (
          loginError.response?.status === 404 ||
          loginError.response?.status === 401 ||
          loginError.response?.data?.error?.includes('not found') ||
          loginError.response?.data?.error?.includes('does not exist')
        ) {
          console.log(
            '[GoogleAuth] Акаунт не існує, перенаправляємо на реєстрацію з даними:',
            googleData
          )
          if (onGoogleDataReceived) {
            onGoogleDataReceived(googleData)
            return
          }
          const params = new URLSearchParams({
            name: googleData.name,
            surname: googleData.surname,
            email: googleData.email,
            google_credential: googleData.credential,
          })
          window.location.href = `/register?${params.toString()}`
          return
        }

        if (onError && typeof onError === 'function') {
          onError(
            loginError.response?.data?.error ||
              `Помилка Google авторизації: ${loginError.message}`
          )
        }
        return
      }
    } catch (e: any) {
      console.error('[GoogleAuth] Загальна помилка:', e)
      if (e.name === 'AbortError' || e.message?.includes('AbortError')) {
        if (onError) {
          onError('')
        }
        return
      }
      if (e.message?.includes('The request has been aborted')) {
        if (onError) {
          onError('')
        }
        return
      }
      if (e.message?.includes('FedCM')) {
        if (onError) {
          onError('')
        }
        return
      }
      if (onError) {
        onError('Помилка отримання даних з Google: ' + (e.message || ''))
      }
    } finally {
      setIsGoogleLoading(false)
    }
  }

  const handleGoogleClick = () => {
    try {
      // @ts-ignore
      if (window.google && window.google.accounts) {
        // @ts-ignore
        window.google.accounts.id.prompt()
      } else {
        if (onError) {
          onError('Google авторизація недоступна. Спробуйте оновити сторінку.')
        }
      }
    } catch (error: any) {
      if (
        error.name === 'AbortError' ||
        error.message?.includes('AbortError')
      ) {
        return
      }
      if (error.message?.includes('The request has been aborted')) {
        return
      }
      if (error.message?.includes('FedCM')) {
        return
      }

      if (onError) {
        onError('Помилка запуску Google авторизації')
      }
    }
  }

  const handleFacebookClick = () => {
    if (onError) {
      onError('Facebook авторизація ще не реалізована')
    }
  }

  return {
    isGoogleLoading,
    handleGoogleClick,
    handleFacebookClick,
  }
}
