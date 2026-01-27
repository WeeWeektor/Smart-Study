import { useI18n } from '@/shared/lib'
import { Sidebar } from '@/widgets/layout'
import { AddCourseReviewModal, ErrorProfile, LoadingProfile } from '@/shared/ui'
import { useProfileData } from '@/shared/hooks/useProfileData'
import React, { useEffect, useMemo, useState } from 'react'
import { CourseHeader, CourseSidebar } from '@/widgets/course'
import {
  addCourseToWishlistService,
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

const CourseReview = () => {
  const { t } = useI18n()
  const { id } = useParams<{ id: string }>()

  const { getItemStatus, refresh: refreshStatuses } = useUserCoursesStatus()
  const {
    status: userStatus,
    progress: userProgress,
    inWishlist: inWishlist,
  } = getItemStatus(id || '')

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

  const reviewStats = useMemo(() => {
    const totalReviews = reviews.length

    if (totalReviews === 0) {
      return {
        averageRating: 0,
        distribution: { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 } as Record<
          string,
          number
        >,
      }
    }

    const sum = reviews.reduce((acc, review) => acc + review.rating, 0)
    const averageRating = sum / totalReviews

    const distribution: Record<string, number> = {
      1: 0,
      2: 0,
      3: 0,
      4: 0,
      5: 0,
    }
    reviews.forEach(review => {
      const ratingKey = Math.round(review.rating)
      if (distribution[ratingKey] !== undefined) {
        distribution[ratingKey] += 1
      }
    })

    return { averageRating, distribution }
  }, [reviews])

  const { averageRating, distribution } = reviewStats

  const handleReviewAdded = (incomingReview: Review) => {
    setReviews(prevReviews => {
      const existingIndex = prevReviews.findIndex(
        r => r.id === incomingReview.id
      )

      if (existingIndex !== -1) {
        const updatedList = [...prevReviews]
        updatedList[existingIndex] = incomingReview
        return updatedList
      } else {
        return [incomingReview, ...prevReviews]
      }
    })
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
      console.log('Loaded content:', response)
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

  const handleStartCourse = () => {
    // TODO
    console.log('Start/Continue course', id)
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
        'Failed remove corse from wishlist' +
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

  const handleCheckCourseBeforePublish = async () => {
    // TODO
    console.log('Check data course before publish', id)
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
              onBack={() => setActiveElement(null)}
            />
          ) : (
            <>
              <CourseInfoSection
                course={course}
                averageRating={averageRating}
              />

              <AuthorSection ownerData={ownerData} />

              {course?.course.is_published && (
                <ReviewsSection
                  reviews={reviews}
                  isReviewsExpanded={isReviewsExpanded}
                  setIsReviewsExpanded={setIsReviewsExpanded}
                  setIsAddReviewModalOpen={setIsAddReviewModalOpen}
                />
              )}
              {course?.course.is_published && (
                <StarSection
                  reviews={reviews}
                  averageRating={averageRating}
                  distribution={distribution}
                />
              )}

              <CourseFooterSection
                course={course}
                userStatus={userStatus}
                inWishlist={inWishlist}
                onStartCourse={handleStartCourse}
                onAddToWishlist={handleAddToWishlist}
                onRemoveFromWishlist={handleRemoveFromWishlist}
                onPublishCourse={handlePublishCourse}
                onRemoveCourse={handleRemoveCourse}
                onCheckCourse={handleCheckCourseBeforePublish}
                showPublishModal={showPublishModal}
                setShowPublishModal={setShowPublishModal}
                isConfirmDelOpen={isConfirmDelOpen}
                setIsConfirmDelOpen={setIsConfirmDelOpen}
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
        />
      )}
    </div>
  )
}

export default CourseReview
