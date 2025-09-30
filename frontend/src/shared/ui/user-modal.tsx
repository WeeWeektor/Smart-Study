import { type FC, type JSX, useEffect, useState } from 'react'
import { useI18n } from '@/shared/lib'
import { userGetService, type UserInfoResponse } from '@/features/user-card'
import { LoadingProfile } from '@/shared/ui/loading-profile.tsx'
import { ErrorProfile } from '@/shared/ui/error-profile.tsx'
import { BookOpen, Briefcase, Info, Mail, MapPin, Phone } from 'lucide-react'

interface UserModalProps {
  isOpen: boolean
  onClose: () => void
  userName: string
  userId: string
  role: string
}

const UserField: FC<{ icon: JSX.Element; label: string; value: string }> = ({
  icon,
  label,
  value,
}) => (
  <div className="flex items-center gap-2 p-2 bg-gray-50 dark:bg-slate-700 rounded-md">
    <span className="text-gray-500 dark:text-gray-300">{icon}</span>
    <span className="font-medium">{label}:</span>
    <span className="ml-1 text-gray-700 dark:text-gray-200">{value}</span>
  </div>
)

export const UserModal: FC<UserModalProps> = ({
  isOpen,
  onClose,
  userName,
  userId,
  role,
}) => {
  const { t } = useI18n()
  const [userInfo, setUserInfo] = useState<UserInfoResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchUserInfo = async (id: string) => {
    setLoading(true)
    setError(null)
    try {
      const response = await userGetService.getUserInfo({ userId: id })
      setUserInfo(response)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err))
      setUserInfo(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (isOpen && userId) fetchUserInfo(userId)
  }, [isOpen, userId])

  if (!isOpen) return null

  const handleBackgroundClick = () => onClose()
  const handleContentClick = (e: React.MouseEvent) => e.stopPropagation()

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm"
      onClick={handleBackgroundClick}
    >
      <div
        className="bg-white dark:bg-slate-800 rounded-xl w-11/12 max-w-lg max-h-[80vh] overflow-y-auto p-6 relative shadow-2xl"
        onClick={handleContentClick}
      >
        <button
          onClick={onClose}
          className="absolute top-3 right-3 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
        >
          ✕
        </button>

        <h2 className="text-2xl font-bold mb-5 text-slate-900 dark:text-slate-100 text-center">
          {userInfo ? `${role}: ${userName}` : { role } + t(' не знайдено')}
        </h2>

        {loading && <LoadingProfile message={t('Завантаження...')} />}
        {error && (
          <ErrorProfile
            error={t('Помилка завантаження даних користувача')}
            size="medium"
          />
        )}

        {!loading && !error && userInfo && (
          <div className="space-y-4">
            {userInfo.profile_picture && (
              <img
                src={userInfo.profile_picture}
                alt={userName}
                className="w-28 h-28 object-cover rounded-full mx-auto mb-4 border-2 border-indigo-500"
              />
            )}
            {userInfo.email && (
              <UserField
                icon={<Mail size={18} />}
                label={t('Email')}
                value={userInfo.email}
              />
            )}
            {userInfo.phone_number && (
              <UserField
                icon={<Phone size={18} />}
                label={t('Телефон')}
                value={userInfo.phone_number}
              />
            )}
            {userInfo.location && (
              <UserField
                icon={<MapPin size={18} />}
                label={t('Локація')}
                value={userInfo.location}
              />
            )}
            {userInfo.organization && (
              <UserField
                icon={<Briefcase size={18} />}
                label={t('Організація')}
                value={userInfo.organization}
              />
            )}
            {userInfo.specialization && (
              <UserField
                icon={<BookOpen size={18} />}
                label={t('Спеціалізація')}
                value={userInfo.specialization}
              />
            )}
            {userInfo.education_level && (
              <UserField
                icon={<BookOpen size={18} />}
                label={t('Освіта')}
                value={userInfo.education_level}
              />
            )}
            {userInfo.bio && (
              <UserField
                icon={<Info size={18} />}
                label={t('Біо')}
                value={userInfo.bio}
              />
            )}
          </div>
        )}

        {!loading && !error && !userInfo && (
          <div className="text-center text-red-500 font-semibold mt-6">
            {t('Користувача не знайдено')}
          </div>
        )}
      </div>
    </div>
  )
}
