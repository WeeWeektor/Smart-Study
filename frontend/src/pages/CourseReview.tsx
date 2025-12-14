import { useI18n } from '@/shared/lib'
import { Sidebar } from '@/widgets/layout'
import { ErrorProfile, LoadingProfile } from '@/shared/ui'
import { useProfileData } from '@/shared/hooks/useProfileData'
import { useEffect, useState } from 'react'
import { CourseSidebar } from '@/widgets/course'
import {
  type CourseStructureResponse,
  getCourseStructureService,
} from '@/features/course'
import { useParams } from 'react-router-dom'

const CourseReview = () => {
  const { t } = useI18n()
  const { id } = useParams<{ id: string }>()
  const {
    profileData,
    loading: profileLoading,
    error: profileError,
    refreshProfile,
  } = useProfileData()

  const [courseData, setCourseData] = useState<CourseStructureResponse | null>(
    null
  )
  const [courseLoading, setCourseLoading] = useState(false)
  const [courseError, setCourseError] = useState<string>('')

  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)
  const [isCourseSidebarCollapsed, setIsCourseSidebarCollapsed] =
    useState(false)

  useEffect(() => {
    const fetchStructure = async () => {
      if (!id) return

      setCourseLoading(true)
      try {
        const data = await getCourseStructureService.getCourseStructure({
          course_id: id,
        })
        setCourseData(data)
      } catch (err) {
        setCourseError(err instanceof Error ? err.message : String(err))
      } finally {
        setCourseLoading(false)
      }
    }

    fetchStructure()
  }, [id])

  if (profileLoading || (courseLoading && !courseData)) {
    return <LoadingProfile message={t('Завантаження...')} />
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
      <CourseSidebar
        isCollapsible={true}
        onCollapseChange={setIsCourseSidebarCollapsed}
        data={courseData}
      />

      <main
        className={`flex-1 transition-all duration-300 ease-in-out p-6 ${isSidebarCollapsed ? 'ml-28' : 'ml-64'} ${isCourseSidebarCollapsed ? 'mr-20' : 'mr-80'}`}
      >
        <div className="max-w-4xl mx-auto">
          <h1 className="text-2xl font-bold mb-4">Вміст уроку...</h1>
          <p>sldjk;fsl;akdjf</p>
        </div>
      </main>
    </div>
  )
}

export default CourseReview
