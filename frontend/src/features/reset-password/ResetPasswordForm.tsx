import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { authService } from '@/features/auth'
import { Button } from '@/shared/ui'
import { Lock, CheckCircle } from 'lucide-react'
import { PasswordField } from '@/shared/ui/password-field'
import { FormAlert } from '@/shared/ui/form-alert'
import { AuthCard } from '@/shared/ui/auth-card'

export const ResetPasswordForm = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')

  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const validatePassword = (password: string) => {
    if (password.length < 8) {
      return 'Пароль повинен містити щонайменше 8 символів'
    }
    if (!/(?=.*[a-z])/.test(password)) {
      return 'Пароль повинен містити щонайменше одну малу літеру'
    }
    if (!/(?=.*[A-Z])/.test(password)) {
      return 'Пароль повинен містити щонайменше одну велику літеру'
    }
    if (!/(?=.*\d)/.test(password)) {
      return 'Пароль повинен містити щонайменше одну цифру'
    }
    return ''
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    const passwordError = validatePassword(newPassword)
    if (passwordError) {
      setError(passwordError)
      return
    }

    if (newPassword !== confirmPassword) {
      setError('Паролі не співпадають')
      return
    }

    if (!token) {
      setError('Неправильне посилання для скидання пароля')
      return
    }

    setIsLoading(true)

    try {
      await authService.resetPassword(token, newPassword)
      setIsSuccess(true)

      setTimeout(() => navigate('/login'), 3000)
    } catch (error: any) {
      setError(error.message || 'Помилка при скиданні пароля')
    } finally {
      setIsLoading(false)
    }
  }

  const getPasswordStrength = (password: string) => {
    let strength = 0
    if (password.length >= 8) strength++
    if (/(?=.*[a-z])/.test(password)) strength++
    if (/(?=.*[A-Z])/.test(password)) strength++
    if (/(?=.*\d)/.test(password)) strength++
    if (/(?=.*[!@#$%^&*])/.test(password)) strength++
    return strength
  }

  const getPasswordStrengthColor = (strength: number) => {
    const colors = [
      'bg-red-200',
      'bg-red-200',
      'bg-yellow-200',
      'bg-yellow-200',
      'bg-blue-200',
      'bg-green-200',
    ]
    return colors[strength] || 'bg-slate-200'
  }

  if (isSuccess) {
    return (
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-8 h-8 text-green-600" />
          </div>
          <h2 className="text-3xl font-bold text-slate-900">
            Пароль успішно змінено!
          </h2>
          <p className="mt-2 text-slate-600">
            Ваш пароль було успішно оновлено. Зараз ви будете перенаправлені на
            сторінку входу.
          </p>
        </div>

        <AuthCard title="Скидання пароля">
          <div className="text-center">
            <p className="text-sm text-slate-500 mb-4">
              Перенаправлення через кілька секунд...
            </p>
            <Link to="/login">
              <Button className="w-full bg-brand-600 hover:bg-brand-700">
                Перейти до входу зараз
              </Button>
            </Link>
          </div>
        </AuthCard>
      </div>
    )
  }

  return (
    <>
      <div className="text-center">
        <div className="w-16 h-16 bg-brand-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Lock className="w-8 h-8 text-brand-600" />
        </div>
        <h2 className="text-3xl font-bold text-slate-900">
          Створити новий пароль
        </h2>
        <p className="mt-2 text-slate-600">
          Введіть новий пароль для вашого акаунта
        </p>
      </div>

      <AuthCard
        title="Скидання пароля"
        description="Пароль повинен бути надійним та унікальним"
      >
        {error && <FormAlert type="error" message={error} />}
        <form onSubmit={handleSubmit} className="space-y-4">
          <PasswordField
            value={newPassword}
            onChange={setNewPassword}
            required
            label="Новий пароль"
            placeholder="Введіть новий пароль"
          />
          <PasswordField
            value={confirmPassword}
            onChange={setConfirmPassword}
            required
            label="Повторіть пароль"
            placeholder="Повторіть новий пароль"
          />
          <Button
            type="submit"
            className="w-full bg-brand-600 hover:bg-brand-700"
            disabled={
              isLoading ||
              !newPassword ||
              !confirmPassword ||
              newPassword !== confirmPassword
            }
          >
            {isLoading ? 'Скидання пароля...' : 'Скинути пароль'}
          </Button>
        </form>
      </AuthCard>
    </>
  )
}
