import { useEffect, useState } from 'react'
import { authService } from '@/features/auth'
import { tokenService } from '@/shared/api'
import { useI18n } from '@/shared/lib/i18n'

interface SocialAuthData {
  name: string
  surname: string
  email: string
  credential: string
  provider: 'google' | 'facebook'
}

interface UseSocialAuthProps {
  onError?: (msg: string) => void
  onSocialDataReceived?: (data: SocialAuthData) => void
  onUserExists?: (userData: {
    access?: string
    refresh?: string
    user?: any
    message?: string
  }) => void
}

export function useSocialAuth({
  onError,
  onSocialDataReceived,
  onUserExists,
}: UseSocialAuthProps) {
  const [isGoogleLoading, setIsGoogleLoading] = useState(false)
  const [isFacebookLoading, setIsFacebookLoading] = useState(false)

  const { t } = useI18n()

  const handleError = (message: string) => {
    if (onError && typeof onError === 'function') {
      onError(message)
    }
  }

  const handleSocialAuth = async (
    provider: 'google' | 'facebook',
    credential: string,
    userData?: any
  ) => {
    const loadingSetter =
      provider === 'google' ? setIsGoogleLoading : setIsFacebookLoading
    loadingSetter(true)
    handleError('')

    console.log(
      '[SocialAuth] handleSocialAuth викликано для провайдера:',
      provider
    )
    console.log('[SocialAuth] Дані користувача:', userData)

    try {
      console.log('[SocialAuth] Спроба входу з існуючим користувачем...')

      const loginRes = await authService.providerOAuth({
        credential,
        provider,
        name: userData.name,
        surname: userData.surname,
      })

      console.log('[SocialAuth] Відповідь від authService:', loginRes)

      if (loginRes.user) {
        console.log('[SocialAuth] Користувач існує, виконуємо вхід')

        if (loginRes.access) {
          tokenService.setToken(loginRes.access)
        }
        if (loginRes.refresh) {
          tokenService.setRefreshToken(loginRes.refresh)
        }

        if (onUserExists) {
          console.log('[SocialAuth] Викликаємо onUserExists callback')
          onUserExists(loginRes)
        } else {
          console.log('[SocialAuth] Перенаправляємо на /profile')
          window.location.href = '/profile'
        }
        return
      }

      console.log(
        '[SocialAuth] Користувач не існує, перенаправляємо на реєстрацію'
      )

      const params = new URLSearchParams({
        name: userData.name,
        surname: userData.surname,
        email: userData.email,
        [`${provider}_credential`]: credential,
      })

      if (onSocialDataReceived) {
        onSocialDataReceived({
          name: userData.name,
          surname: userData.surname,
          email: userData.email,
          credential,
          provider,
        })
      }

      window.location.href = `/register?${params.toString()}`
    } catch (error: any) {
      console.error('[SocialAuth] Помилка в handleSocialAuth:', error)

      if (
        error.response?.status === 400 &&
        (error.response?.data?.error?.includes('role') ||
          error.response?.data?.error?.includes('Необхідно вказати'))
      ) {
        console.log(
          '[SocialAuth] Користувач не існує, перенаправляємо на реєстрацію'
        )

        const params = new URLSearchParams({
          name: userData.name,
          surname: userData.surname,
          email: userData.email,
          [`${provider}_credential`]: credential,
        })

        if (onSocialDataReceived) {
          onSocialDataReceived({
            name: userData.name,
            surname: userData.surname,
            email: userData.email,
            credential,
            provider,
          })
        }

        window.location.href = `/register?${params.toString()}`
        return
      } else {
        handleError(
          t('Помилка авторизації через ') + provider + ': ' + error.message
        )
      }
    } finally {
      loadingSetter(false)
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

  useEffect(() => {
    const initFacebookSDK = () => {
      try {
        // @ts-ignore
        if (window.FB) {
          console.log('[FacebookAuth] Facebook SDK завантажено')
        } else {
          console.warn('[FacebookAuth] Facebook SDK не завантажено')
        }
      } catch (error: any) {
        console.error(
          '[FacebookAuth] Помилка ініціалізації Facebook SDK:',
          error
        )
      }
    }

    const checkFacebookSDK = setInterval(() => {
      // @ts-ignore
      if (window.FB) {
        initFacebookSDK()
        clearInterval(checkFacebookSDK)
      }
    }, 100)

    setTimeout(() => {
      clearInterval(checkFacebookSDK)
    }, 10000)

    return () => {
      clearInterval(checkFacebookSDK)
    }
  }, [])

  const handleGoogleResponse = async (response: any) => {
    console.log(
      '[GoogleAuth] handleGoogleResponse викликано з response:',
      response
    )

    const userData = decodeGoogleJWT(response.credential)
    console.log('[GoogleAuth] Дані користувача після декодування:', userData)

    console.log('[GoogleAuth] Викликаємо handleSocialAuth для Google...')
    await handleSocialAuth('google', response.credential, userData)
    console.log('[GoogleAuth] handleSocialAuth для Google завершено')
  }

  const decodeGoogleJWT = (credential: string) => {
    try {
      if (!credential) {
        throw new Error(t('Відсутній credential'))
      }

      const base64Url = credential.split('.')[1]
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      )
      const payload = JSON.parse(jsonPayload)

      console.log('[GoogleAuth] Успішно декодовано JWT payload:', payload)

      return {
        name: payload.given_name || '',
        surname: payload.family_name || '',
        email: payload.email || '',
      }
    } catch (jwtErr) {
      console.error('[GoogleAuth] Некоректний JWT:', credential, jwtErr)
      throw new Error(t('Некоректний токен Google. Спробуйте ще раз.'))
    }
  }

  const handleFacebookResponse = (response: any) => {
    console.log('[FacebookAuth] Facebook response:', response)

    if (response.status === 'connected') {
      // @ts-ignore
      window.FB.api(
        '/me',
        { fields: 'name,email,first_name,last_name' },
        (userInfo: any) => {
          console.log('[FacebookAuth] User info:', userInfo)

          const userData = {
            name: userInfo.first_name || userInfo.name?.split(' ')[0] || '',
            surname:
              userInfo.last_name ||
              userInfo.name?.split(' ').slice(1).join(' ') ||
              '',
            email: userInfo.email || '',
          }

          console.log('[FacebookAuth] Оброблені дані користувача:', userData)
          console.log(
            '[FacebookAuth] Викликаємо handleSocialAuth для Facebook...'
          )

          handleSocialAuth(
            'facebook',
            response.authResponse.accessToken,
            userData
          )
        }
      )
    } else {
      console.log('[FacebookAuth] Користувач не авторизувався')
      handleError(t('Facebook авторизація не вдалася'))
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
          onError(
            t('Google авторизація недоступна. Спробуйте оновити сторінку.')
          )
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
        onError(t('Помилка запуску Google авторизації'))
      }
    }
  }

  const handleFacebookClick = () => {
    try {
      // @ts-ignore
      if (window.FB) {
        console.log('[FacebookAuth] Запуск Facebook авторизації...')
        // @ts-ignore
        window.FB.login(handleFacebookResponse, {
          scope: 'email,public_profile',
          return_scopes: true,
        })
      } else {
        console.error('[FacebookAuth] Facebook SDK не завантажено')
        handleError(
          t('Facebook SDK не завантажено. Спробуйте оновити сторінку.')
        )
      }
    } catch (error: any) {
      console.error(
        '[FacebookAuth] Помилка запуску Facebook авторизації:',
        error
      )
      handleError(t('Помилка запуску Facebook авторизації'))
    }
  }

  return {
    isGoogleLoading,
    isFacebookLoading,
    handleGoogleClick,
    handleFacebookClick,
  }
}
