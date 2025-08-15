import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Button } from '@/shared/ui'
import { CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import { useI18n } from '@/shared/lib'

const EmailVerification = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>(
    'loading'
  )
  const { t } = useI18n()
  const [message, setMessage] = useState('')

  useEffect(() => {
    const token = searchParams.get('token')

    if (!token) {
      setStatus('error')
      setMessage(t('Невірний токен підтвердження'))
      return
    }

    const verifyEmail = async () => {
      try {
        const response = await fetch(`/api/auth/verify-email/?token=${token}`, {
          method: 'GET',
          credentials: 'include',
        })

        if (response.ok) {
          setStatus('success')
          setMessage(
            t('Email успішно підтверджено! Перенаправлення на профіль...')
          )

          setTimeout(() => {
            navigate('/profile?emailVerified=true')
          }, 1000)
        } else {
          setStatus('error')
          setMessage(t('Помилка підтвердження email. Перевірте посилання.'))
        }
      } catch (error) {
        setStatus('error')
        setMessage(t("Помилка з'єднання з сервером"))
      }
    }

    verifyEmail()
  }, [searchParams, navigate])

  if (status === 'loading') {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin mx-auto text-brand-600 dark:text-brand-400" />
          <p className="mt-4 text-muted-foreground">
            {t('Підтвердження email...')}
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="max-w-md w-full mx-4">
        <div className="bg-card rounded-lg shadow-lg p-6 text-card-foreground">
          {status === 'success' ? (
            <div className="text-center">
              <CheckCircle className="h-12 w-12 text-success-icon mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-foreground mb-2">
                {t('Email підтверджено!')}
              </h2>
              <p className="text-muted-foreground mb-4">{message}</p>
              <Button
                onClick={() => navigate('/profile?emailVerified=true')}
                className="w-full bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 text-white"
              >
                {t('Перейти до профілю')}
              </Button>
            </div>
          ) : (
            <div className="text-center">
              <AlertCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-foreground mb-2">
                {t('Помилка підтвердження')}
              </h2>
              <p className="text-muted-foreground mb-4">{message}</p>
              <Button
                onClick={() => navigate('/login')}
                className="w-full bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 text-white"
              >
                {t('Перейти до входу')}
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default EmailVerification
