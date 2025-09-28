import { useI18n } from '@/shared/lib'
import { Sidebar } from '@/widgets/layout'
import { CourseHeader } from '@/widgets/course'
import { ErrorProfile, LoadingProfile } from '@/shared/ui'
import { useProfileData } from '@/shared/hooks/useProfileData'
import { useNavigate } from 'react-router-dom'

const MyCreatedCourseCatalog = () => {
  const { t } = useI18n()
  const navigate = useNavigate()
  const { profileData, loading, error, refreshProfile } = useProfileData()

  const handleCreateCourse = () => {
    navigate('/create-course')
  }

  if (loading) {
    return <LoadingProfile message={t('Завантаження...')} />
  }

  if (error || !profileData) {
    return (
      <ErrorProfile
        error={error || t('Помилка завантаження даних користувача')}
        onRetry={refreshProfile}
      />
    )
  }

  const userInfo = {
    name: profileData.user.name,
    surname: profileData.user.surname,
    email: profileData.user.email,
    role: profileData.user.role,
  }

  return (
    <div className="min-h-screen bg-background">
      <Sidebar userInfo={userInfo} />

      <div className="ml-64">
        <CourseHeader
          title={t('Створені вами курси')}
          description={t('Додавайте й редагуйте ваші курси')}
          action={true}
          onActionClick={handleCreateCourse}
          actionText={t('Створити')}
        />

        {/*<main className="p-6">*/}
        {/*  <div className="text-center">*/}
        {/*    <h1 className="text-2xl font-bold text-foreground mb-4">*/}
        {/*      {t('Каталог курсів')}*/}
        {/*    </h1>*/}
        {/*    <p className="text-muted-foreground">*/}
        {/*      {t('Ласкаво просимо')}, {userInfo.name} {userInfo.surname}!*/}
        {/*    </p>*/}
        {/*  </div>*/}
        {/*</main>*/}
      </div>
    </div>
  )
}

export default MyCreatedCourseCatalog
