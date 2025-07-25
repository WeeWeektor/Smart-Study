export interface User {
  id: string
  name: string
  surname: string
  phone_number?: string
  email: string
  is_verified_email: boolean
  profile_picture?: string
  role: 'student' | 'teacher' | 'admin'
  is_active: boolean
  is_staff: boolean
  created_at: string
  email_notifications: boolean
  push_notifications: boolean
}

export interface ApiResponse<T> {
  data: T
  message?: string
  status: 'success' | 'error'
}
