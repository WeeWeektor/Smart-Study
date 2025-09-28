import { useI18n } from '@/shared/lib'
import { Sidebar } from '@/widgets/layout'
import { CourseHeader } from '@/widgets/course'
import { ErrorProfile, LoadingProfile } from '@/shared/ui'
import { useProfileData } from '@/shared/hooks/useProfileData'

const MyCourseCatalog = () => {
  const { t } = useI18n()
  const { profileData, loading, error, refreshProfile } = useProfileData()

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
          title={t('Ваші підписки на курси')}
          description={t('Продовжуйте виконання ваших курсів')}
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

export default MyCourseCatalog
