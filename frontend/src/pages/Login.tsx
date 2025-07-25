import { Link } from 'react-router-dom'
import { Button } from '@/shared/ui'
import { AuthLayout } from '@/widgets/auth'
import { LoginForm } from '@/features/login'

const Login = () => {
  return (
    <AuthLayout
      headerContent={
        <>
          <span className="text-slate-600">Немає акаунта?</span>
          <Link to="/register">
            <Button
              variant="outline"
              className="border-brand-300 text-brand-600 hover:bg-brand-50"
            >
              Реєстрація
            </Button>
          </Link>
        </>
      }
    >
      <div className="text-center">
        <h2 className="text-3xl font-bold text-slate-900">Вітаємо знову!</h2>
        <p className="mt-2 text-slate-600">
          Увійдіть до свого акаунта Smart Study
        </p>
      </div>
      <LoginForm />
    </AuthLayout>
  )
}

export default Login
