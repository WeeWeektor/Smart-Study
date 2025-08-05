import { Link } from 'react-router-dom'
import { Button } from '@/shared/ui'
import { AuthLayout } from '@/widgets/auth'
import { LoginForm } from '@/features/login'

const Login = () => {
  return (
    <AuthLayout
      headerContent={
        <>
          <span className="text-muted-foreground">Немає акаунта?</span>
          <Link to="/register">
            <Button
              variant="outline"
              className="border-brand-300 text-brand-600 dark:text-brand-400 hover:bg-brand-50 dark:hover:bg-brand-900"
            >
              Реєстрація
            </Button>
          </Link>
        </>
      }
    >
      <div className="text-center">
        <h2 className="text-3xl font-bold text-foreground">Вітаємо знову!</h2>
        <p className="mt-2 text-muted-foreground">
          Увійдіть до свого акаунта Smart Study
        </p>
      </div>
      <LoginForm />
    </AuthLayout>
  )
}

export default Login
