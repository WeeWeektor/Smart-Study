import { Link } from 'react-router-dom'
import { Button } from '@/shared/ui'
import { AuthLayout } from '@/widgets/auth'
import { ForgotPasswordForm } from '@/features/forgot-password'
import { ArrowLeft } from 'lucide-react'
import { useI18n } from '@/shared/lib'

const ForgotPassword = () => {
  const { t } = useI18n()
  return (
    <AuthLayout
      headerContent={
        <Link to="/login">
          <Button
            variant="ghost"
            className="text-muted-foreground hover:text-brand-600 dark:hover:text-brand-400"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            {t('Назад до входу')}
          </Button>
        </Link>
      }
    >
      <div className="max-w-md mx-auto">
        <ForgotPasswordForm />
      </div>
    </AuthLayout>
  )
}

export default ForgotPassword
