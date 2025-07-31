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

const App = () => {
  useEffect(() => {
    tokenService.initializeToken()
  }, [])

  return (
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
  )
}

export default App
