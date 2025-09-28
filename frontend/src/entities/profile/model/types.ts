export interface ProfileData {
  user: {
    id: string
    name: string
    surname: string
    email: string
    phone_number?: string
    role: string
    is_staff: boolean
    is_superuser: boolean
    is_verified_email: boolean
  }
  settings: {
    email_notifications: boolean
    push_notifications: boolean
    deadline_reminders: boolean
    show_profile_to_others: boolean
    show_achievements: boolean
  }
  profile: {
    bio?: string
    profile_picture?: File | string | undefined
    location?: string
    organization?: string
    specialization?: string
    education_level?: string
  }
}

export interface UpdateProfileRequest {
  user?: {
    name?: string
    surname?: string
    phone_number?: string | null
  }
  settings?: {
    email_notifications?: boolean
    push_notifications?: boolean
    deadline_reminders?: boolean
    show_profile_to_others?: boolean
    show_achievements?: boolean
  }
  profile?: {
    bio?: string | null
    profile_picture?: File | string | undefined
    location?: string | null
    organization?: string | null
    specialization?: string | null
    education_level?: string
  }
}

export interface UpdateProfileResponse {
  status: 'success' | 'error'
  message: string
  profile_data: ProfileData
}
