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
          <span className="text-muted-foreground">{t('Вже є акаунт?')}</span>
          <Link to="/login">
            <Button
              variant="outline"
              className="border-brand-300 text-brand-600 dark:text-brand-400 hover:bg-brand-50 dark:hover:bg-brand-900"
            >
              {t('Увійти')}
            </Button>
          </Link>
        </>
      }
    >
      <div className="text-center">
        <h2 className="text-3xl font-bold text-foreground">
          {t('Створити акаунт')}
        </h2>
        <p className="mt-2 text-muted-foreground">
          {t('Приєднуйтесь до Smart Study та розпочніть своє навчання')}
        </p>
      </div>
      <RegisterForm />
    </AuthLayout>
  )
}

export default Register
