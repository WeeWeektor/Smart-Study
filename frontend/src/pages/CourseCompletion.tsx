import { useEffect, useState } from 'react'
import {
  courseReviewService,
  type Review,
  userCourseCertificateService,
  userCourseEnrollmentService,
} from '@/features/course'
import { useI18n } from '@/shared/lib'
import { useNavigate, useParams } from 'react-router-dom'
import {
  AddCourseReviewModal,
  Button,
  ErrorProfile,
  LoadingProfile,
} from '@/shared/ui'
import { useProfileData } from '@/shared/hooks'
import { Sidebar } from '@/widgets'
import { CourseHeader } from '@/widgets/course'
import {
  CourseFailed,
  CourseInProgress,
  CourseSuccess,
} from './course-completion'
import { updateReviewsList, useReviewStats } from '@/entities/review'
import { ReviewsSection, StarSection } from './course-review'
import { LayoutGrid, UserCircle } from 'lucide-react'
import { downloadBlob } from '@/shared/lib/utils/'

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
  const [errorResavedData, setErrorResavedData] = useState<string>('')
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

  const [reviews, setReviews] = useState<Review[]>([])
  const [reviewsLoading, setReviewsLoading] = useState(true)
  const [isReviewsExpanded, setIsReviewsExpanded] = useState(false)
  const [isAddReviewModalOpen, setIsAddReviewModalOpen] = useState(false)

  const [previewUrl, setPreviewUrl] = useState<string | null>(null)

  useEffect(() => {
    if (error || errorResavedData) {
      const timer = setTimeout(() => {
        setError('')
        setErrorResavedData('')
      }, 15000)
      return () => clearTimeout(timer)
    }
  }, [error, errorResavedData])

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

  useEffect(() => {
    let objectUrl: string | null = null

    const loadPreview = async () => {
      if (!certificateUrl) return

      try {
        const blob = await userCourseCertificateService.downloadCertificateFile(
          certificateUrl,
          'png'
        )
        objectUrl = URL.createObjectURL(blob)
        setPreviewUrl(objectUrl)
      } catch (e) {
        setErrorResavedData(
          t("Не вдалося завантажити прев'ю сертифікату") +
            ' ' +
            (e instanceof Error ? e.message : '')
        )
      }
    }

    loadPreview()

    return () => {
      if (objectUrl) URL.revokeObjectURL(objectUrl)
    }
  }, [certificateUrl, t])

  useEffect(() => {
    const fetchReviews = async () => {
      if (!id) return
      try {
        setReviewsLoading(true)
        const reviewsData = await courseReviewService.getReviews(id)
        setReviews(reviewsData)
      } catch (e) {
        setErrorResavedData(
          e instanceof Error ? e.message : t('Помилка отримання відгуків')
        )
      } finally {
        setReviewsLoading(false)
      }
    }
    fetchReviews()
  }, [id, t])

  const { averageRating, distribution } = useReviewStats(reviews)

  const handleReviewAdded = (incomingReview: Review) => {
    setReviews(prevReviews => updateReviewsList(prevReviews, incomingReview))
  }

  const handleDownloadCertificate = async (
    format: 'pdf' | 'png' | 'view' = 'view'
  ) => {
    if (!certificateUrl) return

    try {
      if (format === 'view') {
        const blob = await userCourseCertificateService.downloadCertificateFile(
          certificateUrl,
          'pdf'
        )
        const url = URL.createObjectURL(blob)
        window.open(url, '_blank')

        return
      }

      const blob = await userCourseCertificateService.downloadCertificateFile(
        certificateUrl,
        format
      )

      const filename = `Certificate_${courseInfo.title.replace(/\s+/g, '_')}_${format.toUpperCase()}.${format}`
      downloadBlob(blob, filename)
    } catch (e) {
      setErrorResavedData(
        t('Не вдалося завантажити файл. Спробуйте пізніше.') +
          ' ' +
          (e instanceof Error ? e.message : '')
      )
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
      setErrorResavedData(
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

  const renderBackButtons = () => {
    return (
      <div className="w-full border-t border-slate-100 dark:border-slate-800 pt-6 mt-2 flex items-center justify-center">
        <div className="flex-1 flex justify-end px-4">
          <Button
            variant="ghost"
            onClick={() => navigate('/my-courses-subscriptions')}
            className="text-slate-500 hover:text-brand-600 gap-2"
          >
            <LayoutGrid className="w-4 h-4" />
            {t('До каталогу курсів')}
          </Button>
        </div>

        <div className="hidden sm:block w-px h-8 bg-slate-200 dark:bg-slate-700 flex-shrink-0" />

        <div className="flex-1 flex justify-start px-4">
          <Button
            variant="ghost"
            onClick={() => navigate('/profile')}
            className="text-slate-500 hover:text-brand-600 gap-2"
          >
            <UserCircle className="w-4 h-4" />
            {t('Мій профіль')}
          </Button>
        </div>
      </div>
    )
  }

  const renderContent = () => {
    if (courseIsFailed) {
      return (
        <CourseFailed
          courseId={id!}
          onReturn={handleReturnToCourse}
          onLeaveReview={() => setIsAddReviewModalOpen(true)}
          returnButtons={renderBackButtons}
        />
      )
    }

    if (isFullyCompleted) {
      return (
        <CourseSuccess
          courseId={id!}
          certificateUrl={previewUrl}
          isGenerating={generatingLoading}
          onDownload={handleDownloadCertificate}
          onGenerate={handleGenerationCertificate}
          onLeaveReview={() => setIsAddReviewModalOpen(true)}
          returnButtons={renderBackButtons}
        />
      )
    }

    return <CourseInProgress onContinue={handleReturnToCourse} />
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Sidebar userInfo={userInfo} onCollapseChange={setIsSidebarCollapsed} />
      <main
        className={`flex-1 flex flex-col transition-all duration-300 ease-in-out ${isSidebarCollapsed ? 'ml-28' : 'ml-64'}`}
      >
        <CourseHeader
          title={`${t('Курс')} - ${courseInfo.title} ${courseIsFailed ? `- ${t('Завершено')}` : isFullyCompleted ? `- ${t('Пройдений')}` : `- ${t('Не завершено')}`}`}
          description={`${courseIsFailed ? t('На жаль, ви не пройшли цей курс. Ви можете переглянути результати проходження.') : isFullyCompleted ? t('Вітаємо! Ви успішно завершили цей курс. Ви можете завантажити свій сертифікат нижче.') : t('Ви ще не завершили цей курс. Продовжуйте навчання, щоб отримати сертифікат.')}`}
        />
        <div className="p-6 max-w-4xl mx-auto w-full space-y-8">
          {errorResavedData && (
            <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md text-sm font-medium border border-red-200">
              {errorResavedData}
            </div>
          )}

          <section>{renderContent()}</section>

          {(isFullyCompleted || courseIsFailed) && !reviewsLoading && (
            <div className="space-y-8 animate-in fade-in duration-700">
              <StarSection
                reviews={reviews}
                averageRating={averageRating}
                distribution={distribution}
              />

              <ReviewsSection
                reviews={reviews}
                isReviewsExpanded={isReviewsExpanded}
                setIsReviewsExpanded={setIsReviewsExpanded}
                setIsAddReviewModalOpen={setIsAddReviewModalOpen}
              />
            </div>
          )}
        </div>
      </main>
      {id && (
        <AddCourseReviewModal
          isOpen={isAddReviewModalOpen}
          onClose={() => setIsAddReviewModalOpen(false)}
          courseId={id}
          onReviewAdded={handleReviewAdded}
        />
      )}
    </div>
  )
}

export default CourseCompletion
