import { useI18n } from '@/shared/lib'
import { Sidebar } from '@/widgets/layout'
import { AddCourseReviewModal, ErrorProfile, LoadingProfile } from '@/shared/ui'
import { useProfileData } from '@/shared/hooks/useProfileData'
import React, { useEffect, useMemo, useState } from 'react'
import { CourseHeader, CourseSidebar } from '@/widgets/course'
import {
  addCourseToWishlistService,
  type BackendCourseItem,
  type BackendModuleContentItem,
  type CourseOwnerProfileResponse,
  type CourseResponse,
  courseReviewService,
  type CourseStructureResponse,
  deleteCourseService,
  type ElementOfCourseResponse,
  elementOfCourseService,
  getCourseService,
  publishCourseService,
  type Review,
  userCourseEnrollmentService,
} from '@/features/course'
import { useNavigate, useParams } from 'react-router-dom'
import { useUserCoursesStatus } from '@/shared/hooks/useUserCoursesStatus'
import {
  ActiveCourseElement,
  AuthorSection,
  CourseFooterSection,
  CourseInfoSection,
  ReviewsSection,
  StarSection,
} from '@/pages/course-review'
import { runFireworks } from '@/shared/lib/utils/'
import { updateReviewsList, useReviewStats } from '@/entities/review'

const CourseReview = () => {
  const { t } = useI18n()
  const { id } = useParams<{ id: string }>()

  const { getItemStatus, refresh: refreshStatuses } = useUserCoursesStatus()
  const { status: userStatus, inWishlist: inWishlist } = getItemStatus(id || '')

  const navigate = useNavigate()

  const {
    profileData,
    loading: profileLoading,
    error: profileError,
    refreshProfile,
  } = useProfileData()

  const [courseStructureData, setCourseStructureData] =
    useState<CourseStructureResponse | null>(null)
  const [ownerData, setOwnerData] = useState<CourseOwnerProfileResponse | null>(
    null
  )
  const [course, setCourse] = useState<CourseResponse | null>(null)

  const [isEnrolling, setIsEnrolling] = useState(false)

  const [reviews, setReviews] = useState<Review[]>([])
  const [isReviewsExpanded, setIsReviewsExpanded] = useState(false)
  const [isAddReviewModalOpen, setIsAddReviewModalOpen] = useState(false)

  const [courseLoading, setCourseLoading] = useState(true)
  const [courseError, setCourseError] = useState<string>('')

  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)
  const [isCourseSidebarCollapsed, setIsCourseSidebarCollapsed] =
    useState(false)
  const [isConfirmDelOpen, setIsConfirmDelOpen] = React.useState(false)
  const [showPublishModal, setShowPublishModal] = useState(false)

  const [activeElement, setActiveElement] =
    useState<ElementOfCourseResponse | null>(null)
  const [isElementLoading, setIsElementLoading] = useState(false)

  const [completedElements, setCompletedElements] = useState<string[]>([])

  const [myCerButtInCS, setMyCerButtInCS] = useState<boolean>(false)
  const [courseCompletedSuccessfully, setCourseCompletedSuccessfully] =
    useState<boolean | null>(null)

  const isOwner = useMemo(() => {
    if (!profileData?.user?.id || !course?.course?.owner[0].owner.id) {
      return false
    }

    const userId = String(profileData.user.id)
    const ownerId = String(course.course.owner[0].owner.id)

    return userId === ownerId
  }, [profileData, course])

  const isUserEnrolled = useMemo(() => {
    return userStatus === 'in_progress' || userStatus === 'completed' || isOwner
  }, [userStatus, isOwner])

  useEffect(() => {
    if (courseError) {
      const timer = setTimeout(() => setCourseError(''), 15000)
      return () => clearTimeout(timer)
    }
  }, [courseError])

  useEffect(() => {
    const fetchCourseAllData = async () => {
      if (!id) return

      setCourseLoading(true)
      setCourseStructureData(null)
      setOwnerData(null)
      setCourse(null)

      try {
        const [response, reviewsData] = await Promise.all([
          getCourseService.getCourse({ course_id: id }),
          courseReviewService.getReviews(id),
        ])
        setCourseStructureData(response.course.structure)
        setOwnerData({
          userData: response.course.owner[0],
        } as unknown as CourseOwnerProfileResponse)
        setCourse(response)
        setReviews(reviewsData)
      } catch (err) {
        setCourseError(err instanceof Error ? err.message : String(err))
      } finally {
        setCourseLoading(false)
      }
    }

    fetchCourseAllData()
  }, [id])

  useEffect(() => {
    const fetchEnrollment = async () => {
      if (!id || !isUserEnrolled || isOwner) return

      try {
        const data = await userCourseEnrollmentService.getEnrollment(
          id as string
        )

        if (data.completed_elements) {
          setCompletedElements(data.completed_elements)
        }

        if (data.last_visited_element_id && !activeElement) {
          handleSidebarItemClick(
            data.last_visited_element_id,
            data.last_visited_element_type as string
          )
        }
      } catch (error) {
        setCourseError(
          'Не вдалося завантажити дані про реєстрацію: ' +
            (error instanceof Error ? error.message : String(error))
        )
      }
    }

    fetchEnrollment()
  }, [id, isUserEnrolled, isOwner])

  const { averageRating, distribution } = useReviewStats(reviews)

  const flatCourseElements = useMemo(() => {
    if (!courseStructureData) return []

    const elements: { id: string; type: string; title: string }[] = []

    const data = courseStructureData

    if (data.courseStructure && Array.isArray(data.courseStructure)) {
      const sortedStructure = [...data.courseStructure].sort(
        (a: BackendCourseItem, b: BackendCourseItem) => a.order - b.order
      )

      sortedStructure.forEach((element: BackendCourseItem) => {
        if (element.type === 'module') {
          const moduleKey = `moduleStructure_order_${element.order}`
          const moduleItems = data[moduleKey] as
            | BackendModuleContentItem[]
            | undefined

          if (moduleItems && Array.isArray(moduleItems)) {
            const sortedModuleItems = [...moduleItems].sort(
              (a: BackendModuleContentItem, b: BackendModuleContentItem) =>
                a.order - b.order
            )

            sortedModuleItems.forEach(
              (modElement: BackendModuleContentItem) => {
                if (modElement.type === 'lesson' && modElement.lesson_id) {
                  elements.push({
                    id: modElement.lesson_id,
                    type: 'lesson',
                    title: modElement.title,
                  })
                } else if (modElement.type === 'test' && modElement.test_id) {
                  elements.push({
                    id: modElement.test_id,
                    type: 'module-test',
                    title: modElement.title,
                  })
                }
              }
            )
          }
        } else if (element.type === 'test' && element.test_id) {
          elements.push({
            id: element.test_id,
            type: 'course-test',
            title: element.title,
          })
        }
      })
    }

    return elements
  }, [courseStructureData])

  const isCourseCompleted = useMemo(() => {
    if (flatCourseElements.length === 0) return false

    return flatCourseElements.every(element =>
      completedElements.includes(element.id)
    )
  }, [flatCourseElements, completedElements])

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await userCourseEnrollmentService.getEnrollmentStatus(
          id as string
        )
        const { is_failed, certificate_url, is_fully_completed } = response

        if (certificate_url || is_fully_completed) {
          setMyCerButtInCS(true)
          setCourseCompletedSuccessfully(true)
        } else if (is_failed) {
          setMyCerButtInCS(true)
          setCourseCompletedSuccessfully(false)
        } else {
          setMyCerButtInCS(false)
          setCourseCompletedSuccessfully(null)
        }
      } catch (e) {
        setCourseError(
          e instanceof Error
            ? e.message
            : t('Помилка отримання статусу прогресу')
        )
      }
    }

    fetchStatus()
  }, [id, t])

  const activeElementId = useMemo(() => {
    if (!activeElement) return null

    if ('lesson' in activeElement && activeElement.lesson)
      return activeElement.lesson.id
    if ('module-test' in activeElement && activeElement['module-test'])
      return activeElement['module-test'].id
    if ('course-test' in activeElement && activeElement['course-test'])
      return activeElement['course-test'].id
    return null
  }, [activeElement])

  const currentElementIndex = useMemo(() => {
    if (!activeElementId) return -1
    return flatCourseElements.findIndex(e => e.id === activeElementId)
  }, [activeElementId, flatCourseElements])

  const handleNavigate = (direction: 'next' | 'prev') => {
    const newIndex =
      direction === 'next' ? currentElementIndex + 1 : currentElementIndex - 1

    if (newIndex >= 0 && newIndex < flatCourseElements.length) {
      const target = flatCourseElements[newIndex]
      handleSidebarItemClick(target.id, target.type)
    }
  }

  const handleFinishCourse = async () => {
    if (!id) return

    if (!isCourseCompleted) {
      if (isOwner) {
        navigate('/my-created-courses')
      } else {
        setActiveElement(null)
      }
      return
    }

    try {
      runFireworks()

      await userCourseEnrollmentService.updateProgress({
        courseId: id,
        finishedCourse: true,
        isCompleted: true,
      })

      refreshStatuses()

      if (isOwner) {
        navigate('/my-created-courses')
      } else {
        setMyCerButtInCS(true)
        setCourseCompletedSuccessfully(true)

        setTimeout(() => {
          navigate(`/course-completion/${id}`)
        }, 2000)
      }
    } catch (e) {
      setCourseError(
        e instanceof Error ? e.message : t('Помилка збереження прогресу')
      )
    }
  }

  const handleReviewAdded = (incomingReview: Review) => {
    setReviews(prevReviews => updateReviewsList(prevReviews, incomingReview))
  }

  const handleSidebarItemClick = async (itemId: string, type: string) => {
    if (!itemId || !type) return

    if (type !== 'lesson' && type !== 'module-test' && type !== 'course-test') {
      return
    }

    setIsElementLoading(true)
    window.scrollTo({ top: 0, behavior: 'smooth' })

    try {
      const response = await elementOfCourseService.getElementOfCourse({
        elementId: itemId,
        elementType: type,
      })

      setActiveElement(response)
    } catch (error) {
      setCourseError(
        error instanceof Error
          ? error.message
          : t('Не вдалось завантажити матеріали')
      )
    } finally {
      setIsElementLoading(false)
    }
  }

  const handleStartCourse = async () => {
    if (!id) return

    setIsEnrolling(true)

    try {
      await userCourseEnrollmentService.startCourse(id)

      refreshStatuses()
      if (flatCourseElements.length > 0) {
        const firstElement = flatCourseElements[0]
        handleSidebarItemClick(firstElement.id, firstElement.type)
      }
    } catch (error) {
      console.error(error)
      setCourseError(
        error instanceof Error ? error.message : t('Не вдалось розпочати курс')
      )
    } finally {
      setIsEnrolling(false)
    }
  }

  const handleElementCompleted = async (
    elementId: string,
    elementType: string,
    timeSpentSeconds: number = 0
  ) => {
    if (completedElements.includes(elementId)) return
    if (!id) return

    try {
      const backendType = elementType.includes('test') ? 'test' : 'lesson'

      await userCourseEnrollmentService.updateProgress({
        courseId: id,
        elementId: elementId,
        elementType: backendType as 'lesson' | 'test',
        isCompleted: true,
        timeSpent: timeSpentSeconds,
        finishedCourse: false,
      })
      setCompletedElements(prev => [...prev, elementId])
      refreshStatuses()
    } catch (e) {
      setCourseError(
        e instanceof Error ? e.message : t('Помилка збереження прогресу')
      )
    }
  }

  const handleAddToWishlist = async () => {
    if (!id) return
    try {
      await addCourseToWishlistService.addCourseToWishlist({
        courseId: id,
      })
      refreshStatuses()
    } catch (error) {
      setCourseError(
        'Failed to add to wishlist' +
          (error instanceof Error ? ': ' + error.message : '')
      )
    }
  }

  const handleRemoveFromWishlist = async () => {
    if (!id) return
    try {
      await deleteCourseService.deleteCourseFromWishlist({
        courseId: id,
      })
      refreshStatuses()
    } catch (error) {
      setCourseError(
        t('Не вдалося видалити курс зі списку бажань') +
          (error instanceof Error ? ': ' + error.message : '')
      )
    }
  }

  const handlePublishCourse = async () => {
    if (!id) return
    try {
      const response = await publishCourseService.publishCourse({
        courseId: id,
      })
      navigate(
        `/my-created-courses/?Message=${encodeURIComponent(
          response.message
        )}&Status=${response.status}&Action=publish`
      )
    } catch (error) {
      navigate(
        `/my-created-courses/?Message=${encodeURIComponent(
          error instanceof Error
            ? error.message
            : t('Не вдалось опублікувати курс')
        )}&Status=0&Action=publish`
      )
    } finally {
      setShowPublishModal(false)
    }
  }

  const handleRemoveCourse = async () => {
    if (!id) return
    try {
      const response = await deleteCourseService.deleteCourse({ courseId: id })
      navigate(
        `/my-created-courses/?Message=${encodeURIComponent(
          response.message
        )}&Status=${response.status}&Action=delete`
      )
    } catch (error) {
      navigate(
        `/my-created-courses/?Message=${encodeURIComponent(
          error instanceof Error ? error.message : t('Не вдалось видалити курс')
        )}&Status=0&Action=delete`
      )
    } finally {
      setIsConfirmDelOpen(false)
    }
  }

  const handleShowStatisticsCourseForTeacher = async () => {
    navigate(`/course-statistics/${id}`)
  }

  const handleChangeCourse = async () => {
    navigate(`/create-course/${id}`)
  }

  if (profileLoading || courseLoading) {
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
        data={courseStructureData}
        isEnrolled={isUserEnrolled}
        onItemClick={handleSidebarItemClick}
        activeItemId={activeElementId}
        completedItemIds={completedElements}
        courseCompleted={myCerButtInCS}
        courseCompletedSuccessfully={
          courseCompletedSuccessfully !== null
            ? courseCompletedSuccessfully
            : false
        }
        courseId={id || ''}
      />

      <main
        className={`flex-1 flex flex-col transition-all duration-300 ease-in-out ${isSidebarCollapsed ? 'ml-28' : 'ml-64'} ${isCourseSidebarCollapsed ? 'mr-20' : 'mr-80'}`}
      >
        <CourseHeader
          title={t('Курс') + ' ' + (course?.course.title || t('Назва курсу'))}
          description={t('Розпочніть свій шлях навчання вже сьогодні!')}
        />
        <div className="p-6 max-w-4xl mx-auto w-full">
          {activeElement || isElementLoading ? (
            <ActiveCourseElement
              activeElement={activeElement}
              isLoading={isElementLoading}
              onBack={() => {
                setActiveElement(null)
                window.scrollTo({ top: 0, behavior: 'smooth' })
              }}
              onNext={() => handleNavigate('next')}
              onPrev={() => handleNavigate('prev')}
              isFirst={currentElementIndex === 0}
              isLast={currentElementIndex === flatCourseElements.length - 1}
              completedCourseFailed={courseCompletedSuccessfully}
              isOwner={isOwner}
              onFinish={handleFinishCourse}
              onComplete={(elemId, elemType, timeSpent) => {
                handleElementCompleted(elemId, elemType, timeSpent)
              }}
              isCourseCompleted={isCourseCompleted}
              isCoursePublished={course?.course.is_published || false}
            />
          ) : (
            <>
              <CourseInfoSection
                course={course}
                averageRating={averageRating}
              />

              <AuthorSection ownerData={ownerData} />

              {course?.course.is_published && (
                <StarSection
                  reviews={reviews}
                  averageRating={averageRating}
                  distribution={distribution}
                />
              )}
              {course?.course.is_published && (
                <ReviewsSection
                  reviews={reviews}
                  isReviewsExpanded={isReviewsExpanded}
                  setIsReviewsExpanded={setIsReviewsExpanded}
                  setIsAddReviewModalOpen={setIsAddReviewModalOpen}
                />
              )}

              <CourseFooterSection
                course={course}
                userStatus={userStatus || null}
                inWishlist={inWishlist}
                onStartCourse={handleStartCourse}
                onAddToWishlist={handleAddToWishlist}
                onRemoveFromWishlist={handleRemoveFromWishlist}
                onPublishCourse={handlePublishCourse}
                onRemoveCourse={handleRemoveCourse}
                onChangeCourse={handleChangeCourse}
                onShowStatistics={handleShowStatisticsCourseForTeacher}
                showPublishModal={showPublishModal}
                setShowPublishModal={setShowPublishModal}
                isConfirmDelOpen={isConfirmDelOpen}
                setIsConfirmDelOpen={setIsConfirmDelOpen}
                isEnrolling={isEnrolling}
                isCourseOwner={isOwner}
              />
            </>
          )}
        </div>
      </main>
      {id && (
        <AddCourseReviewModal
          isOpen={isAddReviewModalOpen}
          onClose={() => setIsAddReviewModalOpen(false)}
          courseId={id}
          onReviewAdded={handleReviewAdded}
          isCourseOwner={isOwner}
        />
      )}
    </div>
  )
}

export default CourseReview
