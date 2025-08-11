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
      return t('validation.passwordMinLength', { min: 8 })
    }
    if (!/(?=.*[a-z])/.test(password)) {
      return t('auth.passwordLowercaseRequired')
    }
    if (!/(?=.*[A-Z])/.test(password)) {
      return t('auth.passwordUppercaseRequired')
    }
    if (!/(?=.*\d)/.test(password)) {
      return t('auth.passwordDigitRequired')
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
      setError(t('validation.passwordMismatch'))
      return
    }

    if (!token) {
      setError(t('auth.invalidResetLink'))
      return
    }

    setIsLoading(true)

    try {
      await authService.resetPassword(token, newPassword)
      setIsSuccess(true)

      setTimeout(() => navigate('/login'), 3000)
    } catch (error: any) {
      setError(error.message || t('errors.generalError'))
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
            {t('auth.passwordChanged')}
          </h2>
          <p className="mt-2 text-muted-foreground">
            {t('auth.passwordResetSuccess')}
          </p>
        </div>

        <AuthCard title={t('auth.resetPassword')}>
          <div className="text-center">
            <p className="text-sm text-muted-foreground mb-4">
              {t('common.next')}
            </p>
            <Link to="/login">
              <Button className="w-full bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 text-white">
                {t('auth.login')}
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
          {t('auth.createNewPassword')}
        </h2>
        <p className="mt-2 text-muted-foreground">
          {t('auth.enterAnewPassword')}
        </p>
      </div>

      <AuthCard
        title={t('auth.resetPassword')}
        description={t('auth.passwordMustBeUnique')}
      >
        {error && <FormAlert type="error" message={error} />}
        <form onSubmit={handleSubmit} className="space-y-4">
          <PasswordField
            value={newPassword}
            onChange={setNewPassword}
            required
            label={t('auth.newPassword')}
            placeholder={t('auth.enterNewPassword')}
          />
          <PasswordField
            value={confirmPassword}
            onChange={setConfirmPassword}
            required
            label={t('auth.confirmPassword')}
            placeholder={t('auth.confirmNewPassword')}
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
            {isLoading ? t('auth.resetPassword1') : t('auth.resetPassword')}
          </Button>
        </form>
      </AuthCard>
    </>
  )
}
