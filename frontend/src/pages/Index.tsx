import { useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useI18n } from '@/shared/lib'
import { Button, LoadingProfile, StatCard } from '@/shared/ui'
import { CourseHeader } from '@/widgets/course'
import { Sidebar } from '@/widgets/layout'
import { useProfileData } from '@/shared/hooks/useProfileData'
import {
  ArrowRight,
  BookOpen,
  CalendarCheck,
  CheckCircle,
  ExternalLink,
  FileText,
  Github,
  GraduationCap,
  Lock,
  ShieldCheck,
  Trophy,
  Zap,
} from 'lucide-react'
import { useUrlParamNotification } from '@/shared/hooks/use-url-param-notification'
import { EmailVerificationNotification } from '@/features/email-verification-notification'
import { LogoutSuccessNotification } from '@/features/logout'
import { DeleteAccountSuccessNotification } from '@/features/delete-account'
import { useUserCoursesStatus } from '@/shared/hooks/useUserCoursesStatus'

const Index = () => {
  const { t } = useI18n()
  const navigate = useNavigate()
  const { profileData, loading, learningStats } = useProfileData()
  const { loading: loading_course_status, rawStats } = useUserCoursesStatus()
  const isAuthorized = !!profileData

  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)

  const [showEmailVerification, hideEmailVerification] =
    useUrlParamNotification('showEmailVerification')
  const [showLogoutSuccess, hideLogoutSuccess] =
    useUrlParamNotification('showLogoutSuccess')
  const [showDeleteAccountSuccess, hideDeleteAccountSuccess] =
    useUrlParamNotification('showDeleteAccountSuccess')

  // TODO якщо робитиму useCalendar то можна буде юзати його для отримання курсових подій і показувати їх в календарі на головній
  // TODO типу події на сьогодні (+ кнопка на завтра)

  const displayCourses = useMemo(() => {
    if (!rawStats) return []

    const enrolled = (rawStats.enrolled_list || []).map(item => ({
      id: item.course.id,
      title: item.course.title,
      progress: Math.round(item.course.user_status?.progress || 0),
      isCompleted: false,
    }))

    const completed = (rawStats.completed_list || []).map(item => ({
      id: item.course.id,
      title: item.course.title,
      progress: 100,
      isCompleted: true,
    }))

    return [...enrolled, ...completed].slice(0, 3)
  }, [rawStats])

  if (loading) return <LoadingProfile message={t('Завантаження...')} />

  const renderFooter = (t: any) => (
    <footer className="border-t border-border bg-card/50 py-12 mt-auto">
      <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-3 gap-10 text-left">
        <div className="space-y-4">
          <h3 className="font-bold text-lg flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-brand-600" />
            Smart Study
          </h3>
          <p className="text-sm text-muted-foreground leading-relaxed">
            {t(
              'Проєкт розроблено для студентів КПІ з метою покращення досвіду дистанційного навчання.'
            )}
          </p>
        </div>

        <div className="space-y-4">
          <h3 className="font-bold text-lg text-foreground">
            {t('Юридична інформація')}
          </h3>
          <nav className="flex flex-col gap-2">
            <button
              onClick={() => navigate('/terms-of-service')}
              className="text-left text-sm text-muted-foreground hover:text-brand-600 flex items-center gap-2 transition-colors"
            >
              <FileText className="w-4 h-4" /> {t('Умови використання')}
            </button>
            <button
              onClick={() => navigate('/privacy-policy')}
              className="text-left text-sm text-muted-foreground hover:text-brand-600 flex items-center gap-2 transition-colors"
            >
              <Lock className="w-4 h-4" /> {t('Політика конфіденційності')}
            </button>
          </nav>
        </div>

        <div className="space-y-4">
          <h3 className="font-bold text-lg text-foreground">{t('Контакти')}</h3>
          <div className="flex gap-4">
            <Button
              variant="ghost"
              size="icon"
              className="rounded-full bg-slate-100 dark:bg-slate-800"
            >
              <Github className="w-5 h-5" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="rounded-full bg-slate-100 dark:bg-slate-800"
            >
              <ExternalLink className="w-5 h-5" />
            </Button>
          </div>
          <p className="text-xs text-muted-foreground mt-4 italic">
            © 2026 Smart Study Team. {t('Всі права захищено.')}
          </p>
        </div>
      </div>
    </footer>
  )

  if (isAuthorized) {
    if (loading_course_status && !rawStats) {
      return <LoadingProfile message={t('Оновлення прогресу...')} />
    }

    const userInfo = {
      name: profileData.user.name,
      surname: profileData.user.surname,
      email: profileData.user.email,
      role: profileData.user.role,
    }

    return (
      <div className="flex h-screen w-full bg-background overflow-hidden">
        <Sidebar
          userInfo={userInfo}
          isCollapsible={true}
          onCollapseChange={setIsSidebarCollapsed}
        />

        <div
          className={`flex-1 flex flex-col transition-all duration-300 ${isSidebarCollapsed ? 'ml-28' : 'ml-64'}`}
        >
          <CourseHeader
            title={t('Головна')}
            description={t('Вітаємо у вашому навчальному центрі!')}
          />

          <main className="pl-8 flex-1 overflow-y-auto">
            <div
              className="w-full flex-1 h-full overflow-y-auto "
              style={{ colorScheme: 'dark' }}
            >
              <div className="mr-6">
                <h2 className="text-3xl font-bold mb-6 mt-6 ">
                  {t('З поверненням, {name}!', { name: userInfo.name })}
                </h2>

                <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
                  <StatCard
                    icon={BookOpen}
                    value={learningStats?.coursesInProgress || 0}
                    label={t('Курси в процесі')}
                    iconBgClassName="bg-blue-500/10"
                    iconClassName="text-blue-600"
                    className="border-none shadow-lg shadow-blue-500/5 bg-white dark:bg-slate-900/50 backdrop-blur-md"
                  />
                  <StatCard
                    icon={Trophy}
                    value={learningStats?.totalTests || 0}
                    label={t('Здано тестів')}
                    iconBgClassName="bg-yellow-500/10"
                    iconClassName="text-yellow-600"
                    className="border-none shadow-lg shadow-yellow-500/5 bg-white dark:bg-slate-900/50 backdrop-blur-md"
                  />
                  <StatCard
                    icon={CheckCircle}
                    value={learningStats?.completedTopics || 0}
                    label={t('Вивчено тем')}
                    iconBgClassName="bg-green-500/10"
                    iconClassName="text-green-600"
                    className="border-none shadow-lg shadow-green-500/5 bg-white dark:bg-slate-900/50 backdrop-blur-md"
                  />
                  <StatCard
                    icon={GraduationCap}
                    value={learningStats?.certificates || 0}
                    label={t('Сертифікати')}
                    iconBgClassName="bg-purple-500/10"
                    iconClassName="text-purple-600"
                    className="border-none shadow-lg shadow-purple-500/5 bg-white dark:bg-slate-900/50 backdrop-blur-md"
                  />
                </div>

                {/* Секція курсів (Топ-3) */}
                <div className="space-y-4 mb-10">
                  {displayCourses.length > 0 ? (
                    displayCourses.map(course => (
                      <div
                        key={course.id}
                        className="p-6 rounded-2xl border border-brand-500/20 bg-brand-500/5 flex justify-between items-center transition-all hover:border-brand-500/40"
                      >
                        <div className="flex-1 mr-4">
                          <h3 className="text-sm font-bold uppercase tracking-wider text-brand-600 mb-1">
                            {course.isCompleted
                              ? t('Завершено:')
                              : t('Продовжити:')}
                          </h3>
                          <h2 className="text-2xl font-bold text-foreground line-clamp-1">
                            {course.title}
                          </h2>
                          <div className="flex items-center gap-4 mt-3">
                            <div className="w-48 h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                              <div
                                className={`h-full ${course.isCompleted ? 'bg-green-500' : 'bg-brand-600'} transition-all duration-500`}
                                style={{ width: `${course.progress}%` }}
                              />
                            </div>
                            <span className="text-sm font-bold">
                              {course.progress}%
                            </span>
                          </div>
                        </div>

                        <Button
                          variant={course.isCompleted ? 'outline' : 'default'}
                          className={
                            course.isCompleted
                              ? 'border-green-600 text-green-600 hover:bg-green-50'
                              : ''
                          }
                          onClick={() =>
                            navigate(
                              course.isCompleted
                                ? `/course-completion/${course.id}`
                                : `/course-review/${course.id}`
                            )
                          }
                        >
                          {course.isCompleted ? (
                            <>
                              <GraduationCap className="mr-2 w-4 h-4" />
                              {t('Отримати сертифікат')}
                            </>
                          ) : (
                            <>
                              {t('Вчитися')}
                              <ArrowRight className="ml-2 w-4 h-4" />
                            </>
                          )}
                        </Button>
                      </div>
                    ))
                  ) : (
                    <div className="mb-10 p-6 rounded-2xl border border-dashed border-border flex justify-center items-center text-muted-foreground">
                      {t('У вас поки немає активних або завершених курсів')}
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <Button
                    className="h-32 text-xl bg-brand-600"
                    onClick={() => navigate('/my-courses-subscriptions')}
                  >
                    <BookOpen className="mr-4 w-8 h-8" />
                    {t('Мої курси')}
                  </Button>
                  <Button
                    variant="outline"
                    className="h-32 text-xl border-brand-600 text-brand-600"
                    onClick={() => navigate('/find-new-courses')}
                  >
                    <Zap className="mr-4 w-8 h-8" />
                    {t('Знайти нове')}
                  </Button>
                  <Button
                    className="h-32 text-xl bg-brand-600"
                    onClick={() => navigate('/calendar')}
                  >
                    <CalendarCheck className="mr-4 w-8 h-8" />
                    {t('Мій календар')}
                  </Button>
                </div>
                <div className="mt-12 w-full">{renderFooter(t)}</div>
              </div>
            </div>
          </main>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background flex flex-col transition-colors duration-300">
      <CourseHeader
        user_is_login={false}
        title="Smart Study"
        description={t('Платформа для розумного навчання та аналізу прогресу')}
        action={true}
        onActionClick={() => navigate('/register')}
        actionText={t('Почати зараз')}
        icon={
          <div className="h-12 flex items-center">
            <Link
              to="/"
              className="flex items-center overflow-hidden flex-1 min-w-0"
            >
              <div className="w-8 h-8 bg-brand-600 dark:bg-brand-500 rounded-lg flex items-center justify-center shrink-0">
                <GraduationCap className="w-5 h-5 text-white" />
              </div>
            </Link>
          </div>
        }
      />

      <main className="flex-1 flex flex-col items-center justify-center px-6 py-20 text-center relative overflow-hidden">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-brand-500/10 rounded-full blur-[100px] -z-10" />

        <h2 className="text-5xl md:text-7xl font-black tracking-tighter text-foreground mb-6 uppercase">
          {t('Навчайся')} <span className="text-brand-600">SMART</span>
        </h2>

        <p className="text-xl text-muted-foreground max-w-2xl mb-12 italic">
          {t(
            'Створюй власні курси, плануй навчання в календарі та отримуй детальну статистику своїх досягнень.'
          )}
        </p>

        <div className="flex flex-col sm:flex-row gap-4 w-full max-w-md">
          <Button
            size="lg"
            className="flex-1 h-16 text-xl bg-brand-600 hover:bg-brand-700 shadow-lg shadow-brand-500/20"
            onClick={() => navigate('/register')}
          >
            {t('Реєстрація')}
            <ArrowRight className="ml-2 w-6 h-6" />
          </Button>
          <Button
            size="lg"
            variant="outline"
            className="flex-1 h-16 text-xl border-slate-300 dark:border-slate-800"
            onClick={() => navigate('/login')}
          >
            {t('Увійти')}
          </Button>
        </div>

        <div className="mt-12 w-full max-w-xl">
          {showEmailVerification && (
            <EmailVerificationNotification onClose={hideEmailVerification} />
          )}
          {showLogoutSuccess && (
            <LogoutSuccessNotification onClose={hideLogoutSuccess} />
          )}
          {showDeleteAccountSuccess && (
            <DeleteAccountSuccessNotification
              onClose={hideDeleteAccountSuccess}
            />
          )}
        </div>
      </main>
      {renderFooter(t)}
    </div>
  )
}

export default Index
