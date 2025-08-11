import { useState } from 'react'
import { Link } from 'react-router-dom'
import { authService } from '@/features/auth'
import { Button } from '@/shared/ui'
import { Mail, CheckCircle } from 'lucide-react'
import { EmailField } from '@/shared/ui/email-field'
import { FormAlert } from '@/shared/ui/form-alert'
import { AuthCard } from '@/shared/ui/auth-card'
import { useI18n } from '@/shared/lib'

export const ForgotPasswordForm = () => {
  const { t } = useI18n()
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
        setError(t('validation.invalidEmail'))
        return
      }

      await authService.forgotPassword({ email })
      setIsSuccess(true)
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message || t('errors.generalError'))
      } else {
        setError(t('errors.generalError'))
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
        <div className="w-16 h-16 bg-brand-100 dark:bg-brand-900 rounded-full flex items-center justify-center mx-auto mb-4">
          <Mail className="w-8 h-8 text-brand-600 dark:text-brand-400" />
        </div>
        <h2 className="text-3xl font-bold text-foreground">
          {t('auth.forgotPassword')}
        </h2>
        <p className="mt-2 text-muted-foreground">{t('auth.resetPassword')}</p>
      </div>
      <AuthCard title={t('auth.resetPassword')} description={t('auth.email')}>
        {!isSuccess ? (
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && <FormAlert type="error" message={error} />}
            <EmailField value={email} onChange={setEmail} required />
            <Button
              type="submit"
              className="w-full bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 text-white"
              disabled={isLoading}
            >
              {isLoading ? t('common.loading') : t('common.submit')}
            </Button>
          </form>
        ) : (
          <div className="text-center">
            <div className="w-16 h-16 bg-success-bg rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-8 h-8 text-success-icon" />
            </div>
            <h2 className="text-2xl text-foreground mb-2">
              {t('auth.emailVerification')}
            </h2>
            <p className="text-muted-foreground mb-4">
              {t('auth.passwordResetSuccess')}
            </p>
            <p className="text-sm font-medium text-foreground bg-card px-3 py-2 rounded-lg inline-block mb-4">
              {email}
            </p>
            <Button
              onClick={handleTryAgain}
              variant="outline"
              className="w-full border-border text-muted-foreground mb-2"
            >
              {t('common.tryAgain')}
            </Button>
            <Link to="/login" className="block">
              <Button className="w-full bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 text-white">
                {t('auth.backToLogin')}
              </Button>
            </Link>
          </div>
        )}
      </AuthCard>
      {!isSuccess && (
        <div className="text-center">
          <p className="text-sm text-muted-foreground">
            {t('auth.rememberPassword')}?{' '}
            <Link
              to="/login"
              className="text-brand-600 dark:text-brand-400 hover:text-brand-700 dark:hover:text-brand-300 font-medium"
            >
              {t('auth.loginAccount')}
            </Link>
          </p>
        </div>
      )}
    </>
  )
}
