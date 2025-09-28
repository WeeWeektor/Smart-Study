import { useEffect, useState } from 'react'
import { useI18n } from '@/shared/lib'
import { Sidebar } from '@/widgets/layout'
import { profileService } from '@/entities/profile'
import { CourseHeader } from '@/widgets/course'

const CoursesCatalog = () => {
  const { t } = useI18n()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string>('')
  const [userInfo, setUserInfo] = useState<{
    name: string
    surname: string
    email: string
    role: string
  } | null>(null)

  useEffect(() => {
    const loadProfile = async () => {
      try {
        setLoading(true)
        const response = await profileService.getProfile()
        if (response.status === 'success' && response.data) {
          const user = response.data.user
          setUserInfo({
            name: user.name,
            surname: user.surname,
            email: user.email,
            role: user.role,
          })
          console.log('Завантажені дані профілю:', response)
        } else {
          setError(t('Не вдалося завантажити дані користувача'))
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : t('Помилка завантаження'))
      } finally {
        setLoading(false)
      }
    }

    loadProfile()
  }, [])

  if (loading) return <div>{t('Завантаження')}...</div>
  if (error || !userInfo)
    return (
      <div>
        {t('Помилка:')} {error}
      </div>
    )

  return (
    <div className="min-h-screen bg-background">
      <Sidebar userInfo={userInfo} />

      <div className="ml-64">
        <CourseHeader />
      </div>
    </div>
  )
}

export default CoursesCatalog
