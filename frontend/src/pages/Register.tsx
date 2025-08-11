import { Link } from 'react-router-dom'
import { Button } from '@/shared/ui'
import { AuthLayout } from '@/widgets/auth'
import { RegisterForm } from '@/features/register'
import { useI18n } from '@/shared/lib'

const Register = () => {
  const { t } = useI18n()
  return (
    <AuthLayout
      headerContent={
        <>
          <span className="text-muted-foreground">{t('auth.haveAccount')}</span>
          <Link to="/login">
            <Button
              variant="outline"
              className="border-brand-300 text-brand-600 dark:text-brand-400 hover:bg-brand-50 dark:hover:bg-brand-900"
            >
              {t('auth.login')}
            </Button>
          </Link>
        </>
      }
    >
      <div className="text-center">
        <h2 className="text-3xl font-bold text-foreground">
          {t('auth.createAccount')}
        </h2>
        <p className="mt-2 text-muted-foreground">
          {t('auth.signinToSmartStudy')}
        </p>
      </div>
      <RegisterForm />
    </AuthLayout>
  )
}

export default Register
