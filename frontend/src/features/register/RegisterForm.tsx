import { useState, useEffect } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { authService } from '@/features/auth'
import {
  Button,
  Input,
  Label,
  Checkbox,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/shared/ui'
import { Eye, EyeOff } from 'lucide-react'
import { FormAlert } from '@/shared/ui/form-alert'
import { AuthCard } from '@/shared/ui/auth-card'
import { SocialAuth } from '@/features/social-auth'
import { tokenService } from '@/shared/api'
import { useI18n } from '@/shared/lib'

export const RegisterForm = () => {
  const { t } = useI18n()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
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
    subscribeNewsletter: true,
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isGoogleRegistration, setIsGoogleRegistration] = useState(false)
  const [googleCredential, setGoogleCredential] = useState<string>('')
  const [isFacebookRegistration, setIsFacebookRegistration] = useState(false)
  const [facebookCredential, setFacebookCredential] = useState<string>('')

  useEffect(() => {
    const googleName = searchParams.get('name')
    const googleSurname = searchParams.get('surname')
    const googleEmail = searchParams.get('email')
    const googleCredential = searchParams.get('google_credential')
    const facebookCredential = searchParams.get('facebook_credential')

    if (googleName && googleSurname && googleEmail && googleCredential) {
      console.log('[RegisterForm] Отримано Google дані з URL параметрів')
      setFormData(prev => ({
        ...prev,
        name: googleName,
        surname: googleSurname,
        email: googleEmail,
        password: generateRandomPassword(),
        confirmPassword: generateRandomPassword(),
        agreeToTerms: false,
        subscribeNewsletter: true,
      }))
      setGoogleCredential(googleCredential)
      setIsGoogleRegistration(true)
    } else if (
      googleName &&
      googleSurname &&
      googleEmail &&
      facebookCredential
    ) {
      console.log('[RegisterForm] Отримано Facebook дані з URL параметрів')
      setFormData(prev => ({
        ...prev,
        name: googleName,
        surname: googleSurname,
        email: googleEmail,
        password: generateRandomPassword(),
        confirmPassword: generateRandomPassword(),
        agreeToTerms: false,
        subscribeNewsletter: true,
      }))
      setFacebookCredential(facebookCredential)
      setIsFacebookRegistration(true)
    }
  }, [searchParams])

  const generateRandomPassword = () => {
    const chars =
      'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*'
    let password = ''
    for (let i = 0; i < 12; i++) {
      password += chars.charAt(Math.floor(Math.random() * chars.length))
    }
    return password
  }

  const handleSocialDataReceived = (data: {
    name: string
    surname: string
    email: string
    credential: string
    provider: 'google' | 'facebook'
  }) => {
    console.log(
      '[RegisterForm] handleSocialDataReceived викликано з даними:',
      data
    )

    setFormData(prev => ({
      ...prev,
      name: data.name,
      surname: data.surname,
      email: data.email,
      password: generateRandomPassword(),
      confirmPassword: generateRandomPassword(),
      agreeToTerms: false,
      subscribeNewsletter: true,
    }))

    if (data.provider === 'google') {
      console.log('[RegisterForm] Встановлюємо Google credential')
      setGoogleCredential(data.credential)
      setIsGoogleRegistration(true)
      setIsFacebookRegistration(false)
    } else {
      console.log('[RegisterForm] Встановлюємо Facebook credential')
      setFacebookCredential(data.credential)
      setIsFacebookRegistration(true)
      setIsGoogleRegistration(false)
    }
  }

  const handleUserExists = (userData: {
    access?: string
    refresh?: string
    user?: any
    message?: string
  }) => {
    console.log('[RegisterForm] handleUserExists викликано з даними:', userData)

    if (userData.access) {
      console.log('[RegisterForm] Встановлюємо access токен')
      tokenService.setToken(userData.access)
    }
    if (userData.refresh) {
      console.log('[RegisterForm] Встановлюємо refresh токен')
      tokenService.setRefreshToken(userData.refresh)
    }

    console.log('[RegisterForm] Перенаправляємо на /profile')
    navigate('/profile')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setIsLoading(true)

    if (!isGoogleRegistration && !isFacebookRegistration) {
      if (formData.password !== formData.confirmPassword) {
        setError(t('Паролі не співпадають'))
        setIsLoading(false)
        return
      }

      if (formData.password.length < 8) {
        setError(t('Пароль повинен містити принаймні 8 символів'))
        setIsLoading(false)
        return
      }
    }

    if (!formData.agreeToTerms) {
      setError(t('Необхідно погодитись з умовами використання'))
      setIsLoading(false)
      return
    }

    if (!formData.role) {
      setError(t('Необхідно вибрати роль'))
      setIsLoading(false)
      return
    }

    try {
      if (isGoogleRegistration || isFacebookRegistration) {
        const credential = isGoogleRegistration
          ? googleCredential
          : facebookCredential
        const provider = isGoogleRegistration ? 'google' : 'facebook'

        if (!credential) {
          setError(t('Відсутній credential. Спробуйте ще раз.'))
          setIsLoading(false)
          return
        }

        console.log('[RegisterForm] Відправляємо соціальну реєстрацію:', {
          provider,
          role: formData.role,
          name: formData.name,
          surname: formData.surname,
          email: formData.email,
        })

        const response = await authService.providerOAuth({
          credential,
          provider,
          role: formData.role as 'student' | 'teacher',
          name: formData.name,
          surname: formData.surname,
          phone_number: formData.phoneNumber.trim()
            ? formData.phoneNumber
            : null,
          email_notifications: formData.subscribeNewsletter,
          push_notifications: formData.subscribeNewsletter,
        })

        if (response.access) {
          tokenService.setToken(response.access)
        }
        if (response.refresh) {
          tokenService.setRefreshToken(response.refresh)
        }

        setSuccess(t('Реєстрація успішна через: ') + provider)
        navigate('/profile')
      } else {
        const registrationData: any = {
          email: formData.email,
          password: formData.password,
          name: formData.name,
          surname: formData.surname,
          role: formData.role as 'student' | 'teacher',
          email_notifications: formData.subscribeNewsletter,
          push_notifications: formData.subscribeNewsletter,
          phone_number: formData.phoneNumber.trim()
            ? formData.phoneNumber
            : null,
        }
        const response = await authService.register(registrationData)

        if (response.data.token) {
          tokenService.setToken(response.data.token)
        }

        setSuccess(t('Акаунт успішно створено!'))
        navigate('/profile')
      }
    } catch (error: any) {
      console.error('Registration error:', error)

      let errorMessage = t('Помилка при створенні акаунта')

      if (error.response) {
        if (error.response.data && error.response.data.error) {
          errorMessage = error.response.data.error
        } else if (error.response.data && error.response.data.message) {
          errorMessage = error.response.data.message
        } else if (error.response.status === 400) {
          errorMessage = t('Перевірте правильність введених даних')
        } else if (error.response.status === 409) {
          errorMessage = t('Користувач з таким email вже існує')
        } else if (error.response.status === 403) {
          errorMessage = t('Помилка CSRF перевірки. Спробуйте оновити сторінку')
        } else {
          errorMessage = `Помилка сервера: ${error.response.status}`
        }
      } else if (error.request) {
        errorMessage = t(
          "Сервер не відповідає. Перевірте з'єднання з інтернетом"
        )
      } else if (error.message) {
        errorMessage = error.message
      }

      setError(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }))
  }

  const handleReturnToNormalRegistration = () => {
    setGoogleCredential('')
    setFacebookCredential('')
    setIsGoogleRegistration(false)
    setIsFacebookRegistration(false)
    setFormData({
      name: '',
      surname: '',
      email: '',
      phoneNumber: '',
      password: '',
      confirmPassword: '',
      role: '',
      agreeToTerms: false,
      subscribeNewsletter: true,
    })
    setError('')
    setSuccess('')
  }

  return (
    <AuthCard
      title={t('Реєстрація')}
      description={t('Заповніть форму нижче для створення акаунта')}
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <FormAlert type="error" message={error} />}
        {success && <FormAlert type="success" message={success} />}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="name">{t("Ім'я")}</Label>
            <Input
              id="name"
              type="text"
              value={formData.name}
              onChange={e => handleInputChange('name', e.target.value)}
              placeholder={t("Ваше ім'я")}
              required
            />
          </div>
          <div>
            <Label htmlFor="surname">{t('Прізвище')}</Label>
            <Input
              id="surname"
              type="text"
              value={formData.surname}
              onChange={e => handleInputChange('surname', e.target.value)}
              placeholder={t('Ваше прізвище')}
              required
            />
          </div>
        </div>

        <div>
          <Label htmlFor="email">{t('Email адреса')}</Label>
          <Input
            id="email"
            type="email"
            value={formData.email}
            onChange={e => handleInputChange('email', e.target.value)}
            placeholder="your.email@example.com"
            required
          />
        </div>

        <div>
          <Label htmlFor="phoneNumber">{t('Номер телефону')}</Label>
          <Input
            id="phoneNumber"
            type="tel"
            value={formData.phoneNumber}
            onChange={e => handleInputChange('phoneNumber', e.target.value)}
            placeholder="+380 XX XXX XX XX"
          />
        </div>

        <div>
          <Label htmlFor="role">{t('Роль')}</Label>
          <Select
            value={formData.role}
            onValueChange={value => handleInputChange('role', value)}
          >
            <SelectTrigger>
              <SelectValue placeholder={t('Оберіть свою роль')} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="student">{t('Студент')}</SelectItem>
              <SelectItem value="teacher">{t('Викладач')}</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {!isGoogleRegistration && (
          <>
            <div>
              <Label htmlFor="password">{t('Пароль')}</Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={formData.password}
                  onChange={e => handleInputChange('password', e.target.value)}
                  placeholder={t('Створіть надійний пароль')}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2"
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4 text-muted-foreground" />
                  ) : (
                    <Eye className="h-4 w-4 text-muted-foreground" />
                  )}
                </button>
              </div>
            </div>

            <div>
              <Label htmlFor="confirmPassword">
                {t('Підтвердження паролю')}
              </Label>
              <div className="relative">
                <Input
                  id="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  value={formData.confirmPassword}
                  onChange={e =>
                    handleInputChange('confirmPassword', e.target.value)
                  }
                  placeholder={t('Повторіть пароль')}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2"
                >
                  {showConfirmPassword ? (
                    <EyeOff className="h-4 w-4 text-muted-foreground" />
                  ) : (
                    <Eye className="h-4 w-4 text-muted-foreground" />
                  )}
                </button>
              </div>
            </div>
          </>
        )}

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
            <Label
              htmlFor="agreeToTerms"
              className="text-sm text-muted-foreground"
            >
              {t('Я погоджуюся з')}{' '}
              <Link
                to="/terms-of-service"
                className="text-brand-600 dark:text-brand-400 hover:text-brand-700 dark:hover:text-brand-300"
              >
                {t('умовами використання')}
              </Link>{' '}
              {t('та')}{' '}
              <Link
                to="/privacy-policy"
                className="text-brand-600 dark:text-brand-400 hover:text-brand-700 dark:hover:text-brand-300"
              >
                {t('політикою конфіденційності')}
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
              className="text-sm text-muted-foreground"
            >
              {t('Отримувати новини та оновлення на email')}
            </Label>
          </div>
        </div>

        {(isGoogleRegistration || isFacebookRegistration) && (
          <div className="mb-4 flex justify-center gap-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={handleReturnToNormalRegistration}
              className="border-brand-300 text-brand-600 dark:text-brand-400 hover:bg-brand-50 dark:hover:bg-brand-900"
            >
              {t(' Повернутись до звичайної реєстрації')}
            </Button>
          </div>
        )}

        <Button
          type="submit"
          className="w-full bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 text-white"
          disabled={isLoading}
        >
          {isLoading ? t('Створення акаунта...') : t('Створити акаунт')}
        </Button>
      </form>

      <div className="mt-4">
        <SocialAuth
          onError={setError}
          onSocialDataReceived={handleSocialDataReceived}
          onUserExists={handleUserExists}
        />
      </div>
    </AuthCard>
  )
}
