import { Link } from 'react-router-dom'
import { Button } from '@/shared/ui'
import { AuthLayout } from '@/widgets/auth'
import { ResetPasswordForm } from '@/features/reset-password'
import { ArrowLeft } from 'lucide-react'

const ResetPassword = () => {
  return (
    <AuthLayout
      headerContent={
        <Link to="/login">
          <Button
            variant="ghost"
            className="text-muted-foreground hover:text-brand-600 dark:hover:text-brand-400"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Назад до входу
          </Button>
        </Link>
      }
    >
      <div className="max-w-md mx-auto">
        <ResetPasswordForm />
      </div>
    </AuthLayout>
  )
}

export default ResetPassword
