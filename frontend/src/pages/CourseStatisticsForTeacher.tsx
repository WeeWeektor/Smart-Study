import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useI18n } from '@/shared/lib'
import { Sidebar } from '@/widgets'
import { CourseHeader } from '@/widgets/course'
import {
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  ErrorProfile,
  LoadingProfile,
} from '@/shared/ui'
import { useProfileData } from '@/shared/hooks'
import {
  type CourseResponse,
  courseStatisticForOwnerService,
  type CourseStatistics,
  getCourseService,
} from '@/features/course'
import {
  ArrowLeft,
  BookOpen,
  CheckCircle,
  Clock,
  Search,
  Star,
  Users,
  XCircle,
} from 'lucide-react'

const CourseStatisticsForTeacher = () => {
  const { t } = useI18n()
  const navigate = useNavigate()

  const { id } = useParams<{ id: string }>()

  const [course, setCourse] = useState<CourseResponse | null>(null)
  const [stats, setStats] = useState<CourseStatistics | null>(null)

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string>('')
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)

  const [searchQuery, setSearchQuery] = useState('')

  const {
    profileData,
    loading: profileLoading,
    error: profileError,
  } = useProfileData()

  useEffect(() => {
    const fetchData = async () => {
      if (!id) return
      setLoading(true)
      try {
        const [courseData, statsData] = await Promise.all([
          getCourseService.getCourse({ course_id: id }),
          courseStatisticForOwnerService.getStatistic(id),
        ])
        setCourse(courseData)
        setStats(statsData)
      } catch (err) {
        setError(
          err instanceof Error ? err.message : t('Помилка завантаження даних')
        )
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [id, t])

  const filteredStudents = useMemo(() => {
    if (!stats?.students) return []

    const query = searchQuery.toLowerCase().trim()

    if (!query) return stats.students

    return stats.students.filter(
      student =>
        student.name.toLowerCase().includes(query) ||
        student.email.toLowerCase().includes(query)
    )
  }, [stats?.students, searchQuery])

  if (profileLoading || loading)
    return <LoadingProfile message={t('Завантаження статистики...')} />

  if (profileError || !profileData || error) {
    return (
      <ErrorProfile
        error={profileError || error}
        onRetry={() => window.location.reload()}
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
    <div className="min-h-screen bg-background flex flex-col">
      <Sidebar
        userInfo={userInfo}
        isCollapsible={true}
        onCollapseChange={setIsSidebarCollapsed}
      />

      <main
        className={`flex-1 flex flex-col transition-all duration-300 ease-in-out bg-slate-50/50 dark:bg-black/20 ${
          isSidebarCollapsed ? 'ml-28' : 'ml-64'
        }`}
      >
        <CourseHeader
          title={`${t('Статистика курсу')}: ${course?.course.title}`}
          description={t(
            'Детальна аналітика проходження та успішності студентів.'
          )}
          actionsBackPage={
            <Button
              variant="outline"
              size="icon"
              onClick={() => navigate(`/course-review/${id}`)}
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
          }
        />

        <div className="p-6 max-w-7xl mx-auto w-full space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatsCard
              title={t('Всього студентів')}
              value={stats?.total_students || 0}
              icon={<Users className="w-5 h-5 text-blue-600" />}
              description={t('Записаних на курс')}
            />

            <StatsCard
              title={t('Рейтинг курсу')}
              value={stats?.average_rating || 0}
              icon={
                <Star className="w-5 h-5 text-yellow-500 fill-yellow-500" />
              }
              description={`${stats?.total_reviews} ${t('відгуків')}`}
            />

            <StatsCard
              title={t('В процесі навчання')}
              value={stats?.total_in_progress_course_students || 0}
              icon={<Clock className="w-5 h-5 text-brand-600" />}
              description={t('Активні студенти')}
            />

            <StatsCard
              title={t('Всього завершили')}
              value={stats?.total_completed_course_students || 0}
              icon={<BookOpen className="w-5 h-5 text-purple-600" />}
              description={t('Дійшли до фіналу')}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card className="border-l-4 border-l-green-500 shadow-sm">
              <CardContent className="p-6 flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-500 mb-1">
                    {t('Успішно завершили')}
                  </p>
                  <h3 className="text-3xl font-bold text-slate-900 dark:text-slate-100">
                    {stats?.total_success_complete}
                  </h3>
                  <p className="text-xs text-green-600 mt-1 font-medium">
                    {t('Отримали сертифікат')}
                  </p>
                </div>
                <div className="p-4 bg-green-100 dark:bg-green-900/30 rounded-full">
                  <CheckCircle className="w-8 h-8 text-green-600 dark:text-green-400" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-l-4 border-l-red-500 shadow-sm">
              <CardContent className="p-6 flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-slate-500 mb-1">
                    {t('Провалили курс')}
                  </p>
                  <h3 className="text-3xl font-bold text-slate-900 dark:text-slate-100">
                    {stats?.total_failed_complete}
                  </h3>
                  <p className="text-xs text-red-600 mt-1 font-medium">
                    {t('Не набрали прохідний бал')}
                  </p>
                </div>
                <div className="p-4 bg-red-100 dark:bg-red-900/30 rounded-full">
                  <XCircle className="w-8 h-8 text-red-600 dark:text-red-400" />
                </div>
              </CardContent>
            </Card>
          </div>

          <Card className="shadow-sm border-slate-200 dark:border-slate-800">
            <CardHeader className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-4 gap-4">
              <CardTitle className="text-lg font-bold">
                {t('Список студентів')}
              </CardTitle>

              <div className="relative w-full sm:w-72">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-slate-500 dark:text-slate-400" />
                <input
                  type="text"
                  placeholder={t('Пошук за іменем або email...')}
                  className="w-full h-9 pl-9 pr-4 rounded-md border border-slate-200 bg-white px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-slate-500 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-brand-600 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-800 dark:bg-slate-950 dark:placeholder:text-slate-400 dark:focus-visible:ring-brand-400"
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                />
              </div>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                  <thead className="text-xs text-slate-500 uppercase bg-slate-50 dark:bg-slate-900/50">
                    <tr>
                      <th className="px-4 py-3 rounded-tl-lg">
                        {t('Студент')}
                      </th>
                      <th className="px-4 py-3">{t('Статус')}</th>
                      <th className="px-4 py-3 w-1/3">{t('Прогрес')}</th>
                      <th className="px-4 py-3 rounded-tr-lg">
                        {t('Дата реєстрації')}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredStudents.length > 0 ? (
                      filteredStudents.map(student => (
                        <tr
                          key={student.id}
                          className="border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-900/20 transition-colors"
                        >
                          <td className="px-4 py-3 font-medium">
                            <div className="flex flex-col">
                              <span className="text-slate-900 dark:text-slate-100 font-semibold">
                                {student.name}
                              </span>
                              <span className="text-xs text-slate-500">
                                {student.email}
                              </span>
                            </div>
                          </td>
                          <td className="px-4 py-3">
                            <StatusBadge status={student.status} t={t} />
                          </td>
                          <td className="px-4 py-3">
                            <div className="flex items-center gap-2">
                              <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2.5">
                                <div
                                  className={`h-2.5 rounded-full ${
                                    student.status === 'success'
                                      ? 'bg-green-500'
                                      : student.status === 'failed'
                                        ? 'bg-red-500'
                                        : 'bg-brand-600'
                                  }`}
                                  style={{ width: `${student.progress}%` }}
                                ></div>
                              </div>
                              <span className="text-xs font-bold w-8 text-right">
                                {student.progress}%
                              </span>
                            </div>
                          </td>
                          <td className="px-4 py-3 text-slate-500">
                            {student.joined_at}
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td
                          colSpan={4}
                          className="text-center py-8 text-slate-500"
                        >
                          {t('Студентів не знайдено за вашим запитом.')}
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}

const StatsCard = ({
  title,
  value,
  icon,
  description,
}: {
  title: string
  value: string | number
  icon: React.ReactNode
  description: string
}) => (
  <Card className="shadow-sm hover:shadow-md transition-shadow border-slate-200 dark:border-slate-800">
    <CardContent className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-slate-500 dark:text-slate-400">
          {title}
        </h3>
        <div className="p-2 bg-slate-100 dark:bg-slate-800 rounded-lg">
          {icon}
        </div>
      </div>
      <div className="text-2xl font-bold text-slate-900 dark:text-slate-100">
        {value}
      </div>
      <p className="text-xs text-slate-500 mt-1">{description}</p>
    </CardContent>
  </Card>
)

const StatusBadge = ({
  status,
  t,
}: {
  status: string
  t: (s: string) => string
}) => {
  const config = {
    success: {
      style:
        'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
      label: t('Успішно'),
    },
    failed: {
      style: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
      label: t('Провалено'),
    },
    in_progress: {
      style: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
      label: t('В процесі'),
    },
  }

  const current = config[status as keyof typeof config] || config.in_progress

  return (
    <span
      className={`px-2.5 py-0.5 rounded-full text-xs font-medium border border-transparent ${current.style}`}
    >
      {current.label}
    </span>
  )
}

export default CourseStatisticsForTeacher
