import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authService } from '../../features/auth'
import {
  Button,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Input,
  Label,
  Checkbox,
  Alert,
  AlertDescription,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../../shared/ui'
import { Eye, EyeOff, AlertCircle, CheckCircle } from 'lucide-react'
import { UserFields } from '@/shared/ui/user-fields'
import { EmailField } from '@/shared/ui/email-field'
import { PasswordField } from '@/shared/ui/password-field'
import { FormAlert } from '@/shared/ui/form-alert'
import { AuthCard } from '@/shared/ui/auth-card'
import { SocialAuth } from '@/features/social-auth'

export const RegisterForm = () => {
  const navigate = useNavigate()
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    surname: '',
    email: '',
    phoneNumber: '',
    password: '',
    confirmPassword: '',
    role: '',
    agreeToTerms: false,
    subscribeNewsletter: false,
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  // Видалено socialError

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setIsLoading(true)

    if (formData.password !== formData.confirmPassword) {
      setError('Паролі не співпадають')
      setIsLoading(false)
      return
    }

    if (formData.password.length < 8) {
      setError('Пароль повинен містити принаймні 8 символів')
      setIsLoading(false)
      return
    }

    if (!formData.agreeToTerms) {
      setError('Необхідно погодитись з умовами використання')
      setIsLoading(false)
      return
    }

    try {
      const response = await authService.register({
        email: formData.email,
        password: formData.password,
        name: formData.name,
        surname: formData.surname,
        phone_number: formData.phoneNumber || null,
        role: formData.role as 'student' | 'teacher',
        email_notifications: formData.subscribeNewsletter,
        push_notifications: formData.subscribeNewsletter,
      })

      setSuccess('Акаунт успішно створено!')

      if (response.data.user) {
        const userRole = response.data.user.role

        if (userRole === 'teacher') {
          navigate('/dashboard/teacher')
        } else {
          navigate('/dashboard/student')
        }
      }
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message || 'Помилка при створенні акаунта')
      } else {
        setError('Сталася невідома помилка')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  return (
    <AuthCard
      title="Реєстрація"
      description="Заповніть форму нижче для створення акаунта"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <FormAlert type="error" message={error} />}
        {success && <FormAlert type="success" message={success} />}
        <UserFields
          formData={{
            name: formData.name,
            surname: formData.surname,
            phone: formData.phoneNumber,
            email: formData.email,
            role: formData.role,
          }}
          onChange={(field, value) =>
            handleInputChange(field === 'phone' ? 'phoneNumber' : field, value)
          }
          isEditing={true}
          showEmail={true}
          showRole={true}
          requiredFields={['name', 'surname', 'email', 'role']}
        />
        <PasswordField
          value={formData.password}
          onChange={value => handleInputChange('password', value)}
          required
          label="Пароль"
          placeholder="Створіть надійний пароль"
        />
        <PasswordField
          value={formData.confirmPassword}
          onChange={value => handleInputChange('confirmPassword', value)}
          required
          label="Підтвердження паролю"
          placeholder="Повторіть пароль"
        />
        <div className="space-y-3">
          <div className="flex items-center space-x-2">
            <Checkbox
              id="agreeToTerms"
              checked={formData.agreeToTerms}
              onCheckedChange={checked =>
                handleInputChange('agreeToTerms', checked as boolean)
              }
              required
            />
            <Label htmlFor="agreeToTerms" className="text-sm text-slate-600">
              Я погоджуюся з{' '}
              <Link
                to="/terms-of-service"
                className="text-brand-600 hover:text-brand-700"
              >
                умовами використання
              </Link>{' '}
              та{' '}
              <Link
                to="/privacy-policy"
                className="text-brand-600 hover:text-brand-700"
              >
                політикою конфіденційності
              </Link>
            </Label>
          </div>
          <div className="flex items-center space-x-2">
            <Checkbox
              id="subscribeNewsletter"
              checked={formData.subscribeNewsletter}
              onCheckedChange={checked =>
                handleInputChange('subscribeNewsletter', checked as boolean)
              }
            />
            <Label
              htmlFor="subscribeNewsletter"
              className="text-sm text-slate-600"
            >
              Отримувати новини та оновлення на email
            </Label>
          </div>
        </div>
        <Button
          type="submit"
          className="w-full bg-brand-600 hover:bg-brand-700 text-white"
          disabled={isLoading}
        >
          {isLoading ? 'Створення акаунта...' : 'Створити акаунт'}
        </Button>
      </form>
      <div className="mt-6">
        <SocialAuth onError={setError} />
      </div>
    </AuthCard>
  )
}
