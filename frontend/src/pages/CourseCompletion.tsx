import { useEffect, useState } from 'react'
import {
  userCourseCertificateService,
  userCourseEnrollmentService,
} from '@/features/course'
import { useI18n } from '@/shared/lib'
import { useNavigate, useParams } from 'react-router-dom'
import { ErrorProfile, LoadingProfile } from '@/shared/ui'
import { useProfileData } from '@/shared/hooks'
import { Sidebar } from '@/widgets'
import { CourseHeader } from '@/widgets/course'
import {
  CourseFailed,
  CourseInProgress,
  CourseSuccess,
} from './course-completion'

const CourseCompletion = () => {
  const { t } = useI18n()
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const {
    profileData,
    loading: profileLoading,
    error: profileError,
    refreshProfile,
  } = useProfileData()

  const [error, setError] = useState<string>('')
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)

  const [courseIsFailed, setCourseIsFailed] = useState<boolean>(false)
  const [certificateUrl, setCertificateUrl] = useState<string | null>(null)
  const [isFullyCompleted, setIsFullyCompleted] = useState<boolean>(false)
  const [courseInfo, setCourseInfo] = useState<{
    title: string
    description: string
  }>({ title: '', description: '' })

  const [statusLoading, setStatusLoading] = useState(true)
  const [generatingLoading, setGeneratingLoading] = useState(false)

  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(''), 15000)
      return () => clearTimeout(timer)
    }
  }, [error])

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await userCourseEnrollmentService.getEnrollmentStatus(
          id as string
        )
        const {
          is_failed,
          certificate_url,
          is_fully_completed,
          course_title,
          course_description,
        } = response

        setCourseIsFailed(is_failed)
        setCertificateUrl(certificate_url)
        setIsFullyCompleted(is_fully_completed)
        setCourseInfo({
          title: course_title || t('Курс'),
          description: course_description || t(''),
        })
      } catch (e) {
        setError(
          e instanceof Error
            ? e.message
            : t('Помилка отримання статусу прогресу')
        )
      } finally {
        setStatusLoading(false)
      }
    }

    if (id) {
      fetchStatus()
    }
  }, [id, t])

  const handleDownloadCertificate = () => {
    if (certificateUrl) {
      // TODO Відкривати в новій вкладці або робим завантаження
      window.open(certificateUrl, '_blank')
    }
  }

  const handleReturnToCourse = () => {
    navigate(`/course-review/${id}`)
  }

  const handleGenerationCertificate = async () => {
    if (!id) return

    setGeneratingLoading(true)
    setError('')
    try {
      const response = await userCourseCertificateService.createCertificate(id)

      if (response && response.certificate_id) {
        setCertificateUrl(response.certificate_id)
      }
    } catch (e) {
      setError(
        e instanceof Error ? e.message : t('Помилка створення сертифікату')
      )
    } finally {
      setGeneratingLoading(false)
    }
  }

  if (profileLoading || statusLoading) {
    return <LoadingProfile message={t('Завантаження...')} />
  }

  if (profileError || !profileData || error) {
    return (
      <ErrorProfile
        error={profileError || error || t('Помилка завантаження даних')}
        onRetry={() => {
          if (profileError) refreshProfile()
          if (error && id) window.location.reload()
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

  const renderContent = () => {
    if (courseIsFailed) {
      return (
        <CourseFailed courseId={id as string} onReturn={handleReturnToCourse} />
      )
    }

    if (isFullyCompleted) {
      return (
        <CourseSuccess
          courseId={id as string}
          certificateUrl={certificateUrl}
          isGenerating={generatingLoading}
          onDownload={handleDownloadCertificate}
          onGenerate={handleGenerationCertificate}
        />
      )
    }

    return <CourseInProgress onContinue={handleReturnToCourse} />
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Sidebar
        userInfo={userInfo}
        isCollapsible={true}
        onCollapseChange={setIsSidebarCollapsed}
      />
      <main
        className={`flex-1 flex flex-col transition-all duration-300 ease-in-out ${isSidebarCollapsed ? 'ml-28' : 'ml-64'}`}
      >
        <CourseHeader
          title={`${t('Курс')} - ${courseInfo.title} ${courseIsFailed ? `- ${t('Завершено')}` : isFullyCompleted ? `- ${t('Пройдений')}` : `- ${t('Не завершено')}`}`}
          description={`${courseIsFailed ? t('На жаль, ви не пройшли цей курс. Ви можете переглянути результати проходження.') : isFullyCompleted ? t('Вітаємо! Ви успішно завершили цей курс. Ви можете завантажити свій сертифікат нижче.') : t('Ви ще не завершили цей курс. Продовжуйте навчання, щоб отримати сертифікат.')}`}
        />
        <div className="p-6 max-w-4xl mx-auto w-full">{renderContent()} </div>
      </main>
    </div>
  )
}

export default CourseCompletion
