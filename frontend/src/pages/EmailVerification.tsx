import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Button, Alert, AlertDescription } from '@/shared/ui'
import { CheckCircle, AlertCircle, Loader2 } from 'lucide-react'

const EmailVerification = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>(
    'loading'
  )
  const [message, setMessage] = useState('')

  useEffect(() => {
    const token = searchParams.get('token')

    if (!token) {
      setStatus('error')
      setMessage('Невірний токен підтвердження')
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
            'Email успішно підтверджено! Перенаправлення на профіль...'
          )

          setTimeout(() => {
            navigate('/profile?emailVerified=true')
          }, 1000)
        } else {
          setStatus('error')
          setMessage('Помилка підтвердження email. Перевірте посилання.')
        }
      } catch (error) {
        setStatus('error')
        setMessage("Помилка з'єднання з сервером")
      }
    }

    verifyEmail()
  }, [searchParams, navigate])

  if (status === 'loading') {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin mx-auto text-brand-600" />
          <p className="mt-4 text-slate-600">Підтвердження email...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center">
      <div className="max-w-md w-full mx-4">
        <div className="bg-white rounded-lg shadow-lg p-6">
          {status === 'success' ? (
            <div className="text-center">
              <CheckCircle className="h-12 w-12 text-green-600 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-slate-900 mb-2">
                Email підтверджено!
              </h2>
              <p className="text-slate-600 mb-4">{message}</p>
              <Button
                onClick={() => navigate('/profile?emailVerified=true')}
                className="w-full bg-brand-600 hover:bg-brand-700"
              >
                Перейти до профілю
              </Button>
            </div>
          ) : (
            <div className="text-center">
              <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-slate-900 mb-2">
                Помилка підтвердження
              </h2>
              <p className="text-slate-600 mb-4">{message}</p>
              <Button
                onClick={() => navigate('/login')}
                className="w-full bg-brand-600 hover:bg-brand-700"
              >
                Перейти до входу
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default EmailVerification
