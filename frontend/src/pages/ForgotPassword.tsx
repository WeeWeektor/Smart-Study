import { Link } from 'react-router-dom'
import { Button } from '@/shared/ui'
import { AuthLayout } from '@/widgets/auth'
import { ForgotPasswordForm } from '@/features/forgot-password'
import { ArrowLeft } from 'lucide-react'

const ForgotPassword = () => {
  return (
    <AuthLayout
      headerContent={
        <Link to="/login">
          <Button
            variant="ghost"
            className="text-slate-700 hover:text-brand-600"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Назад до входу
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
