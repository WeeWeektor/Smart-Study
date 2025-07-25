import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authService } from '../../features/auth'
import { Button, Label, Checkbox } from '../../shared/ui'
import { EmailField } from '@/shared/ui/email-field'
import { PasswordField } from '@/shared/ui/password-field'
import { FormAlert } from '@/shared/ui/form-alert'
import { AuthCard } from '@/shared/ui/auth-card'
import { SocialAuth } from '@/features/social-auth'

interface LoginResponse {
  role: string
}

export const LoginForm = () => {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [rememberMe, setRememberMe] = useState(false)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  // Видалено socialError

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      if (!email || !password) {
        setError('Будь ласка, заповніть всі поля')
        return
      }

      const response = (await authService.login({
        email,
        password,
        rememberMe,
      })) as unknown as LoginResponse

      if (response) {
        const userRole = response.role

        if (userRole === 'admin') {
          navigate('/')
        } else {
          navigate('/profile')
        }
      }
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message || 'Невірний email або пароль')
      } else {
        setError('Сталася невідома помилка')
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <AuthCard
      title="Вхід в акаунт"
      description="Введіть свої дані для входу в систему"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <FormAlert type="error" message={error} />}
        <EmailField value={email} onChange={setEmail} required />
        <PasswordField
          value={password}
          onChange={setPassword}
          required
          label="Пароль"
          placeholder="Введіть ваш пароль"
        />
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Checkbox
              id="remember"
              checked={rememberMe}
              onCheckedChange={checked => setRememberMe(checked as boolean)}
            />
            <Label htmlFor="remember" className="text-sm text-slate-600">
              Запам'ятати мене
            </Label>
          </div>
          <Link
            to="/forgot-password"
            className="text-sm text-brand-600 hover:text-brand-700"
          >
            Забули пароль?
          </Link>
        </div>
        <Button
          type="submit"
          className="w-full bg-brand-600 hover:bg-brand-700 text-white"
          disabled={isLoading}
        >
          {isLoading ? 'Вхід...' : 'Увійти'}
        </Button>
      </form>
      <div className="mt-6">
        <SocialAuth onError={setError} />
      </div>
    </AuthCard>
  )
}
