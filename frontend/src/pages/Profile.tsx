import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { profileService } from '@/entities/profile'
import { type ProfileData, type UpdateProfileRequest } from '@/entities/profile'
import { authService } from '@/features/auth'
import { Button, Alert, AlertDescription } from '@/shared/ui'
import { CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import { Sidebar } from '@/widgets/layout'
import {
  ProfileHeader,
  ProfileInfoCard,
  LearningStats,
  ProfileTabs,
} from '@/widgets/profile'
import { learningStats } from '@/shared/lib/mock-data'
import { useI18n } from '@/shared/lib'

const Profile = () => {
  const navigate = useNavigate()
  const { t } = useI18n()
  const [searchParams] = useSearchParams()
  const [isEditing, setIsEditing] = useState(false)
  const [profileData, setProfileData] = useState<ProfileData | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string>('')
  const [success, setSuccess] = useState<string>('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string>('')

  const [formData, setFormData] = useState({
    name: '',
    surname: '',
    phone: '',
    location: '',
    organization: '',
    specialization: '',
    bio: '',
    profile_picture: '' as string,
    education_level: '',
    email_notifications: true,
    push_notifications: true,
    deadline_reminders: true,
    show_profile_to_others: true,
    show_achievements: true,
  })

  const [initialFormData, setInitialFormData] = useState(formData)

  useEffect(() => {
    loadProfile()
  }, [])

  useEffect(() => {
    const emailVerified = searchParams.get('emailVerified')
    if (emailVerified === 'true') {
      setSuccess(t('Email успішно підтверджено!'))
      navigate('/profile', { replace: true })
    }
  }, [searchParams, navigate])

  useEffect(() => {
    return () => {
      if (previewUrl && previewUrl.startsWith('blob:')) {
        URL.revokeObjectURL(previewUrl)
      }
    }
  }, [previewUrl])

  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => setSuccess(''), 15000)
      return () => clearTimeout(timer)
    }
  }, [success])

  const loadProfile = async () => {
    try {
      setLoading(true)
      setError('')

      const response = await profileService.getProfile()
      console.log('Завантажені дані профілю:', response)

      if (response.status === 'success' && response.data) {
        setProfileData(response.data)

        setFormData({
          name: response.data.user.name,
          surname: response.data.user.surname,
          phone: response.data.user?.phone_number || '',
          location: response.data.profile?.location || '',
          organization: response.data.profile?.organization || '',
          specialization: response.data.profile?.specialization || '',
          bio: response.data.profile?.bio || '',
          profile_picture:
            typeof response.data.profile?.profile_picture === 'string'
              ? response.data.profile.profile_picture
              : '',
          education_level: response.data.profile?.education_level || '',
          email_notifications: response.data.settings.email_notifications,
          push_notifications: response.data.settings.push_notifications,
          deadline_reminders: response.data.settings.deadline_reminders,
          show_profile_to_others: response.data.settings.show_profile_to_others,
          show_achievements: response.data.settings.show_achievements,
        })
      }
    } catch (error) {
      console.error('Помилка завантаження профілю:', error)
      setError(
        error instanceof Error ? error.message : 'Помилка завантаження профілю'
      )
    } finally {
      setLoading(false)
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      if (!file.type.startsWith('image/')) {
        setError(t('Будь ласка, оберіть файл зображення'))
        return
      }

      if (file.size > 5 * 1024 * 1024) {
        setError(t('Розмір файлу не повинен перевищувати 5MB'))
        return
      }

      if (previewUrl && previewUrl.startsWith('blob:')) {
        URL.revokeObjectURL(previewUrl)
      }

      setSelectedFile(file)

      const url = URL.createObjectURL(file)
      setPreviewUrl(url)
      setFormData(prev => ({
        ...prev,
        profile_picture: url as string,
      }))
    }
  }

  const handleSave = async () => {
    try {
      setSaving(true)
      setError('')
      setSuccess('')

      if (!formData.name.trim() || !formData.surname.trim()) {
        setError(t("Ім'я та прізвище є обов'язковими полями"))
        return
      }

      let profilePictureUrl = formData.profile_picture
      if (selectedFile) {
        const uploadResponse =
          await profileService.uploadProfilePicture(selectedFile)
        if (uploadResponse.status === 'success' && uploadResponse.data?.url) {
          profilePictureUrl = uploadResponse.data.url
        } else {
          setError(t('Помилка завантаження фото'))
          return
        }
      }
      if (typeof profilePictureUrl !== 'string') {
        profilePictureUrl = ''
      }
      const updateData: UpdateProfileRequest = {
        user: {
          name: formData.name.trim(),
          surname: formData.surname.trim(),
          phone_number:
            formData.phone.trim() === '' ? '' : formData.phone.trim(),
        },
        settings: {
          email_notifications: formData.email_notifications,
          push_notifications: formData.push_notifications,
          deadline_reminders: formData.deadline_reminders,
          show_profile_to_others: formData.show_profile_to_others,
          show_achievements: formData.show_achievements,
        },
        profile: {
          bio: formData.bio.trim() === '' ? undefined : formData.bio.trim(),
          profile_picture: profilePictureUrl || undefined,
          location:
            formData.location.trim() === ''
              ? undefined
              : formData.location.trim(),
          organization:
            formData.organization.trim() === ''
              ? undefined
              : formData.organization.trim(),
          specialization:
            formData.specialization.trim() === ''
              ? undefined
              : formData.specialization.trim(),
          education_level:
            formData.education_level === 'not_specified'
              ? undefined
              : formData.education_level,
        },
      }

      const response = await profileService.updateProfile(updateData)

      if (response.status === 'success') {
        setSuccess(t('Профіль успішно оновлено!'))
        setIsEditing(false)
        setSelectedFile(null)
        await loadProfile()

        if (previewUrl && previewUrl.startsWith('blob:')) {
          URL.revokeObjectURL(previewUrl)
          setPreviewUrl('')
        }
      }
    } catch (error) {
      console.error('Помилка оновлення профілю:', error)
      setError(
        error instanceof Error ? error.message : t('Помилка оновлення профілю')
      )
    } finally {
      setSaving(false)
    }
  }

  const handleDeleteAccount = async () => {
    if (
      window.confirm(
        t('Ви впевнені, що хочете видалити свій акаунт? Ця дія незворотна.')
      )
    ) {
      try {
        await profileService.deleteProfile()
        await authService.logout()
        navigate('/?showDeleteAccountSuccess=true')
      } catch (error) {
        console.error('Помилка видалення акаунта:', error)
        setError(
          error instanceof Error
            ? error.message
            : t('Помилка видалення акаунта')
        )
        navigate('/?showDeleteAccountSuccess=true')
      }
    }
  }

  const handleFormChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleSettingsChange = (field: string, value: boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const isFormChanged = () => {
    const keys: (keyof typeof formData)[] = [
      'name',
      'surname',
      'phone',
      'location',
      'organization',
      'specialization',
      'bio',
      'profile_picture',
      'education_level',
      'email_notifications',
      'push_notifications',
      'deadline_reminders',
      'show_profile_to_others',
      'show_achievements',
    ]
    for (const key of keys) {
      if (formData[key] !== initialFormData[key]) return true
    }
    return false
  }
  const isSaveDisabled =
    !isFormChanged() || !formData.name.trim() || !formData.surname.trim()

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin mx-auto text-brand-600 dark:text-brand-400" />
          <p className="mt-4 text-muted-foreground">
            {t('Завантаження профілю...')}
          </p>
        </div>
      </div>
    )
  }

  if (!profileData) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
          <p className="text-destructive mb-4">
            {t('Помилка завантаження профілю')}
          </p>
          <Button
            onClick={loadProfile}
            className="bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 text-white"
          >
            {t('Спробувати знову')}
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <Sidebar
        userInfo={{
          name: profileData.user.name,
          surname: profileData.user.surname,
          email: profileData.user.email,
          is_admin: profileData.user.role,
        }}
      />

      <div className="ml-64">
        <ProfileHeader
          isEditing={isEditing}
          isSaving={saving}
          onEdit={() => {
            setIsEditing(true)
            setInitialFormData(formData)
          }}
          onSave={handleSave}
          onCancel={() => setIsEditing(false)}
          disabledSave={isSaveDisabled}
        />

        <main className="p-6">
          {error && (
            <Alert className="mb-6 border-destructive bg-destructive/10">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription className="text-destructive">
                {error}
              </AlertDescription>
            </Alert>
          )}
          {success && (
            <Alert className="mb-6 border-success-icon bg-success-bg/10">
              <CheckCircle className="h-4 w-4" />
              <AlertDescription className="text-success-text">
                {success}
              </AlertDescription>
            </Alert>
          )}

          <div className="grid lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1 space-y-6">
              <ProfileInfoCard
                profileData={{
                  user: profileData.user,
                  profile: {
                    ...profileData.profile,
                    profile_picture:
                      typeof formData.profile_picture === 'string'
                        ? formData.profile_picture
                        : profileData.profile.profile_picture &&
                            typeof profileData.profile.profile_picture ===
                              'string'
                          ? profileData.profile.profile_picture
                          : undefined,
                    location: profileData.profile.location ?? undefined,
                    organization: profileData.profile.organization ?? undefined,
                  },
                }}
                previewUrl={previewUrl}
                onFileSelect={handleFileSelect}
                isEditing={isEditing}
              />
              <LearningStats stats={learningStats} />
            </div>

            <div className="lg:col-span-2">
              <ProfileTabs
                formData={formData}
                isEditing={isEditing}
                onFormChange={handleFormChange}
                onSettingsChange={handleSettingsChange}
                onDeleteAccount={handleDeleteAccount}
              />
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}

export default Profile
