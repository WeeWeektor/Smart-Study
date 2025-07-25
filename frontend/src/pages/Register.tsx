import { Link } from 'react-router-dom'
import { Button, Card, CardContent } from '@/shared/ui'
import { AuthLayout } from '@/widgets/auth'
import { RegisterForm } from '@/features/register'
import { SocialAuth } from '@/features/social-auth'

const Register = () => {
  return (
    <AuthLayout
      headerContent={
        <>
          <span className="text-slate-600">Вже є акаунт?</span>
          <Link to="/login">
            <Button
              variant="outline"
              className="border-brand-300 text-brand-600 hover:bg-brand-50"
            >
              Увійти
            </Button>
          </Link>
        </>
      }
    >
      <div className="text-center">
        <h2 className="text-3xl font-bold text-slate-900">Створити акаунт</h2>
        <p className="mt-2 text-slate-600">
          Приєднуйтесь до Smart Study та розпочніть своє навчання
        </p>
      </div>
      <RegisterForm />
    </AuthLayout>
  )
}

export default Register
