import { Link } from 'react-router-dom'
import { Button } from '@/shared/ui'
import { AuthLayout } from '@/widgets/auth'
import { LoginForm } from '@/features/login'
import { useI18n } from '@/shared/lib'

const Login = () => {
  const { t } = useI18n()
  return (
    <AuthLayout
      headerContent={
        <>
          <span className="text-muted-foreground">{t('auth.noAccount')}</span>
          <Link to="/register">
            <Button
              variant="outline"
              className="border-brand-300 text-brand-600 dark:text-brand-400 hover:bg-brand-50 dark:hover:bg-brand-900"
            >
              {t('auth.register')}
            </Button>
          </Link>
        </>
      }
    >
      <div className="text-center">
        <h2 className="text-3xl font-bold text-foreground">
          {t('auth.greeting')}!
        </h2>
        <p className="mt-2 text-muted-foreground">
          {t('auth.loginToYourAccount')}
        </p>
      </div>
      <LoginForm />
    </AuthLayout>
  )
}

export default Login
