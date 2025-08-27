import { BrowserRouter, Routes, Route } from 'react-router-dom'
import {
  Login,
  Register,
  ForgotPassword,
  NotFound,
  Index,
  ResetPassword,
  TermsOfService,
  PrivacyPolicy,
  Profile,
  EmailVerification,
} from '@/pages'
import { tokenService } from '@/shared/api'
import { useEffect } from 'react'
import { useTheme } from '@/shared/hooks/use-theme'
import { I18nProvider } from '@/shared/lib/i18n/context'

const App = () => {
  const [theme] = useTheme()

  useEffect(() => {
    tokenService.initializeToken()
  }, [])

  useEffect(() => {
    const root = document.documentElement
    if (theme === 'dark') {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
  }, [theme])

  return (
    <I18nProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/terms-of-service" element={<TermsOfService />} />
          <Route path="/privacy-policy" element={<PrivacyPolicy />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/verify-email" element={<EmailVerification />} />

          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </I18nProvider>
  )
}

export default App
