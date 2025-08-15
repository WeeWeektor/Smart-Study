import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { authService } from '@/features/auth'
import { Button } from '@/shared/ui'
import { Lock, CheckCircle } from 'lucide-react'
import { PasswordField } from '@/shared/ui/password-field'
import { FormAlert } from '@/shared/ui/form-alert'
import { AuthCard } from '@/shared/ui/auth-card'
import { useI18n } from '@/shared/lib'

export const ResetPasswordForm = () => {
  const { t } = useI18n()
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
      return t('Пароль повинен містити щонайменше 8 символів')
    }
    if (!/(?=.*[a-z])/.test(password)) {
      return t('Пароль повинен містити щонайменше одну малу літеру')
    }
    if (!/(?=.*[A-Z])/.test(password)) {
      return t('Пароль повинен містити щонайменше одну велику літеру')
    }
    if (!/(?=.*\d)/.test(password)) {
      return t('Пароль повинен містити щонайменше одну цифру')
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
      setError(t('Паролі не співпадають'))
      return
    }

    if (!token) {
      setError(t('Неправильне посилання для скидання пароля'))
      return
    }

    setIsLoading(true)

    try {
      await authService.resetPassword(token, newPassword)
      setIsSuccess(true)

      setTimeout(() => navigate('/login'), 3000)
    } catch (error: any) {
      setError(error.message || t('Помилка при скиданні пароля'))
    } finally {
      setIsLoading(false)
    }
  }

  if (isSuccess) {
    return (
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <div className="w-16 h-16 bg-success-bg rounded-full flex items-center justify-center mx-auto mb-4">
            <CheckCircle className="w-8 h-8 text-success-icon" />
          </div>
          <h2 className="text-3xl font-bold text-foreground">
            {t('Пароль успішно змінено!')}
          </h2>
          <p className="mt-2 text-muted-foreground">
            {t(
              ' Ваш пароль було успішно оновлено. Зараз ви будете перенаправлені на сторінку входу.'
            )}
          </p>
        </div>

        <AuthCard title={t('Скидання пароля')}>
          <div className="text-center">
            <p className="text-sm text-muted-foreground mb-4">
              {t('Перенаправлення через кілька секунд...')}
            </p>
            <Link to="/login">
              <Button className="w-full bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 text-white">
                {t('Перейти до входу зараз')}
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
        <div className="w-16 h-16 bg-brand-100 dark:bg-brand-900 rounded-full flex items-center justify-center mx-auto mb-4">
          <Lock className="w-8 h-8 text-brand-600 dark:text-brand-400" />
        </div>
        <h2 className="text-3xl font-bold text-foreground">
          {t('Створити новий пароль')}
        </h2>
        <p className="mt-2 text-muted-foreground">
          {t('Введіть новий пароль для вашого акаунта')}
        </p>
      </div>

      <AuthCard
        title={t('Скидання пароля')}
        description={t('Пароль повинен бути надійним та унікальним')}
      >
        {error && <FormAlert type="error" message={error} />}
        <form onSubmit={handleSubmit} className="space-y-4">
          <PasswordField
            value={newPassword}
            onChange={setNewPassword}
            required
            label={t('Новий пароль')}
            placeholder={t('Введіть новий пароль')}
          />
          <PasswordField
            value={confirmPassword}
            onChange={setConfirmPassword}
            required
            label={t('Повторіть пароль')}
            placeholder={t('Повторіть новий пароль')}
          />
          <Button
            type="submit"
            className="w-full bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 text-white"
            disabled={
              isLoading ||
              !newPassword ||
              !confirmPassword ||
              newPassword !== confirmPassword
            }
          >
            {isLoading ? t('Скидання пароля...') : t('Скинути пароль')}
          </Button>
        </form>
      </AuthCard>
    </>
  )
}
