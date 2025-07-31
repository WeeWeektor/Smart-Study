import { useState } from 'react'
import { Link } from 'react-router-dom'
import { authService } from '@/features/auth'
import {
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Input,
  Label,
  Alert,
  AlertDescription,
} from '@/shared/ui'
import { Mail, CheckCircle, AlertCircle } from 'lucide-react'
import { EmailField } from '@/shared/ui/email-field'
import { FormAlert } from '@/shared/ui/form-alert'
import { AuthCard } from '@/shared/ui/auth-card'

export const ForgotPasswordForm = () => {
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [isSuccess, setIsSuccess] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      if (!email.includes('@')) {
        setError('Будь ласка, введіть правильну email адресу')
        return
      }

      await authService.forgotPassword({ email })
      setIsSuccess(true)
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message || 'Помилка при надсиланні інструкцій')
      } else {
        setError('Сталася невідома помилка')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleTryAgain = () => {
    setIsSuccess(false)
    setEmail('')
    setError('')
  }

  return (
    <>
      <div className="text-center">
        <div className="w-16 h-16 bg-brand-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Mail className="w-8 h-8 text-brand-600" />
        </div>
        <h2 className="text-3xl font-bold text-slate-900">Забули пароль?</h2>
        <p className="mt-2 text-slate-600">
          Не хвилюйтесь, ми допоможемо відновити доступ до вашого акаунта
        </p>
      </div>
      <AuthCard
        title="Відновлення паролю"
        description="Введіть email адресу, пов'язану з вашим акаунтом"
      >
        {!isSuccess ? (
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && <FormAlert type="error" message={error} />}
            <EmailField value={email} onChange={setEmail} required />
            <Button
              type="submit"
              className="w-full bg-brand-600 hover:bg-brand-700 text-white"
              disabled={isLoading}
            >
              {isLoading ? 'Надсилаємо...' : 'Надіслати інструкції'}
            </Button>
          </form>
        ) : (
          <div className="text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
            <h2 className="text-2xl text-slate-900 mb-2">
              Перевірте вашу пошту
            </h2>
            <p className="text-slate-600 mb-4">
              Ми надіслали інструкції з відновлення паролю на адресу:
            </p>
            <p className="text-sm font-medium text-slate-900 bg-slate-50 px-3 py-2 rounded-lg inline-block mb-4">
              {email}
            </p>
            <Button
              onClick={handleTryAgain}
              variant="outline"
              className="w-full border-slate-300 text-slate-700 mb-2"
            >
              Спробувати з іншим email
            </Button>
            <Link to="/login" className="block">
              <Button className="w-full bg-brand-600 hover:bg-brand-700 text-white">
                Повернутися до входу
              </Button>
            </Link>
          </div>
        )}
      </AuthCard>
      {!isSuccess && (
        <div className="text-center">
          <p className="text-sm text-slate-600">
            Пригадали пароль?{' '}
            <Link
              to="/login"
              className="text-brand-600 hover:text-brand-700 font-medium"
            >
              Увійти в акаунт
            </Link>
          </p>
        </div>
      )}
    </>
  )
}
