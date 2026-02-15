import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useI18n } from '@/shared/lib'
import { Sidebar } from '@/widgets'
import { CourseHeader } from '@/widgets/course'
import { Button, ErrorProfile, LoadingProfile } from '@/shared/ui'
import { useProfileData } from '@/shared/hooks'
import { type CourseResponse, getCourseService } from '@/features/course'
import { ArrowLeft } from 'lucide-react'

const CourseStatisticsForTeacher = () => {
  const { t } = useI18n()
  const navigate = useNavigate()

  const { id } = useParams<{ id: string }>()

  const [course, setCourse] = useState<CourseResponse | null>(null)
  const [courseLoading, setCourseLoading] = useState(true)
  const [courseError, setCourseError] = useState<string>('')

  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)

  const {
    profileData,
    loading: profileLoading,
    error: profileError,
    refreshProfile,
  } = useProfileData()

  useEffect(() => {
    const fetchCourseData = async () => {
      if (!id) return

      setCourseLoading(true)
      setCourseError('')

      try {
        const data = await getCourseService.getCourse({ course_id: id })
        setCourse(data)
      } catch (error) {
        setCourseError(
          error instanceof Error
            ? error.message
            : t('Не вдалося завантажити інформацію про курс')
        )
      } finally {
        setCourseLoading(false)
      }
    }

    fetchCourseData()
  }, [id, t])

  if (profileLoading || courseLoading) {
    return <LoadingProfile message={t('Завантаження статистики...')} />
  }

  if (profileError || !profileData || courseError) {
    return (
      <ErrorProfile
        error={profileError || courseError || t('Помилка завантаження даних')}
        onRetry={() => {
          if (profileError) refreshProfile()
          if (courseError && id) window.location.reload()
        }}
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
        className={`flex-1 flex flex-col transition-all duration-300 ease-in-out ${
          isSidebarCollapsed ? 'ml-28' : 'ml-64'
        }`}
      >
        <CourseHeader
          title={`${t('Статистика курсу')}: ${course?.course.title || ''}`}
          description={t(
            'Переглядайте аналітику, успішність студентів та рейтинги вашого курсу.'
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

        <div className="p-6">
          <p className="text-gray-500">Тут будуть графіки та таблиці...</p>
        </div>
      </main>
    </div>
  )
}

export default CourseStatisticsForTeacher
