import { formatShortDate, parseISODuration, useI18n } from '@/shared/lib'
import { Sidebar } from '@/widgets/layout'
import {
  AddCourseReviewModal,
  Avatar,
  AvatarFallback,
  AvatarImage,
  Button,
  Card,
  CardContent,
  CardHeader,
  ErrorProfile,
  LoadingProfile,
} from '@/shared/ui'
import { useProfileData } from '@/shared/hooks/useProfileData'
import { useEffect, useMemo, useState } from 'react'
import { CourseHeader, CourseSidebar } from '@/widgets/course'
import {
  type CourseOwnerProfileResponse,
  type CourseResponse,
  courseReviewService,
  type CourseStructureResponse,
  getCourseService,
  type Review,
} from '@/features/course'
import { useParams } from 'react-router-dom'
import {
  BarChart,
  BookOpen,
  Briefcase,
  Building2,
  Calendar,
  ChevronDown,
  ChevronUp,
  Clock,
  FileCheck,
  Globe,
  GraduationCap,
  Layers,
  Mail,
  MapPin,
  MessageSquare,
  Phone,
  Plus,
  Star,
  User,
} from 'lucide-react'

const CourseReview = () => {
  const { t } = useI18n()
  const { id } = useParams<{ id: string }>()
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

  const renderAuthorSection = () => {
    if (!ownerData || !ownerData.userData) return null

    const { owner, profile, settings } = ownerData.userData
    const isPublic = settings.show_profile_to_others
    const fullName = `${owner.name} ${owner.surname}`
    const initials =
      `${owner.name?.charAt(0) || ''}${owner.surname?.charAt(0) || ''}`.toUpperCase()

    return (
      <Card className="mb-8 overflow-hidden border-l-4 border-l-brand-600 dark:border-l-brand-500 shadow-sm">
        <CardHeader className="pb-4">
          <div className="flex items-center gap-4">
            <Avatar className="h-16 w-16 border-2 border-white shadow-sm ring-1 ring-slate-100 dark:ring-slate-700">
              <AvatarImage
                src={profile.profile_picture || undefined}
                alt={fullName}
                className="object-cover"
              />
              <AvatarFallback className="bg-brand-100 text-brand-700 font-bold text-xl">
                {initials}
              </AvatarFallback>
            </Avatar>

            <div className="flex flex-col">
              <h3 className="text-xl font-bold text-slate-800 dark:text-slate-100">
                {fullName}
              </h3>
              <span className="text-sm text-slate-500 dark:text-slate-400 font-medium flex items-center gap-1.5">
                <User className="w-3.5 h-3.5" />
                {t('Автор курсу')}
              </span>
            </div>
          </div>
        </CardHeader>

        {isPublic && (
          <CardContent className="space-y-4 pt-0 border-t border-slate-100 dark:border-slate-800 mt-4 pt-4">
            {profile.bio && (
              <div className="text-sm text-slate-600 dark:text-slate-300 bg-slate-50 dark:bg-slate-800/50 p-3 rounded-md italic">
                "{profile.bio}"
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-3 text-sm">
              {profile.specialization && (
                <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300">
                  <Briefcase className="w-4 h-4 text-brand-500 shrink-0" />
                  <span className="font-semibold text-slate-500 dark:text-slate-400">
                    {t('Спеціалізація')}:
                  </span>
                  <span>{profile.specialization}</span>
                </div>
              )}

              {profile.organization && (
                <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300">
                  <Building2 className="w-4 h-4 text-blue-500 shrink-0" />
                  <span className="font-semibold text-slate-500 dark:text-slate-400">
                    {t('Організація')}:
                  </span>
                  <span>{profile.organization}</span>
                </div>
              )}

              {profile.education_level && (
                <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300">
                  <GraduationCap className="w-4 h-4 text-purple-500 shrink-0" />
                  <span className="font-semibold text-slate-500 dark:text-slate-400">
                    {t('Освіта')}:
                  </span>
                  <span className="capitalize">{profile.education_level}</span>
                </div>
              )}

              {profile.location && (
                <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300">
                  <MapPin className="w-4 h-4 text-red-500 shrink-0" />
                  <span className="font-semibold text-slate-500 dark:text-slate-400">
                    {t('Локація')}:
                  </span>
                  <span>{profile.location}</span>
                </div>
              )}
            </div>

            {(owner.email || owner.phone_number) && (
              <div className="border-t border-slate-100 dark:border-slate-800 pt-3 mt-2 flex flex-wrap gap-6">
                {owner.email && (
                  <div className="flex items-center gap-2 text-xs text-slate-500 hover:text-brand-600 transition-colors cursor-pointer">
                    <Mail className="w-3.5 h-3.5" />
                    {owner.email}
                  </div>
                )}
                {owner.phone_number && (
                  <div className="flex items-center gap-2 text-xs text-slate-500 hover:text-brand-600 transition-colors cursor-pointer">
                    <Phone className="w-3.5 h-3.5" />
                    {owner.phone_number}
                  </div>
                )}
              </div>
            )}
          </CardContent>
        )}
      </Card>
    )
  }

  const renderCourseInfoSection = () => {
    if (!course || !course.course) return null

    const { title, description, cover_image, category, details } = course.course

    return (
      <Card className="mb-8 overflow-hidden shadow-sm border border-slate-200 dark:border-slate-800">
        {cover_image && (
          <div className="w-full h-64 md:h-80 relative bg-slate-100 dark:bg-slate-800">
            <img
              src={cover_image}
              alt={title}
              className="w-full h-full object-cover"
            />
            {category && (
              <div className="absolute top-4 left-4">
                <span className="bg-brand-600/90 text-white px-3 py-1 rounded-full text-sm font-medium uppercase tracking-wide shadow-md backdrop-blur-sm">
                  {category}
                </span>
              </div>
            )}
          </div>
        )}

        <CardContent className="p-6">
          <div className="flex flex-col gap-6">
            <div>
              <h3 className="text-lg font-bold mb-2 text-slate-800 dark:text-slate-100 flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-brand-600" />
                {t('Про цей курс')}
              </h3>
              <p className="text-slate-600 dark:text-slate-300 leading-relaxed whitespace-pre-wrap">
                {description || t('Опис відсутній')}
              </p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="flex flex-col gap-1 p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-100 dark:border-slate-800">
                <div className="flex items-center gap-2 text-slate-500 text-xs uppercase font-bold">
                  <BarChart className="w-4 h-4" />
                  {t('Рівень')}
                </div>
                <div className="font-semibold text-slate-700 dark:text-slate-200 capitalize">
                  {details.level || t('Не вказано')}
                </div>
              </div>

              <div className="flex flex-col gap-1 p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-100 dark:border-slate-800">
                <div className="flex items-center gap-2 text-slate-500 text-xs uppercase font-bold">
                  <Globe className="w-4 h-4" />
                  {t('Мова')}
                </div>
                <div className="font-semibold text-slate-700 dark:text-slate-200">
                  {details.course_language || t('Не вказано')}
                </div>
              </div>

              <div className="flex flex-col gap-1 p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-100 dark:border-slate-800">
                <div className="flex items-center gap-2 text-slate-500 text-xs uppercase font-bold">
                  <Clock className="w-4 h-4" />
                  {t('Тривалість')}
                </div>
                <div className="font-semibold text-slate-700 dark:text-slate-200">
                  {parseISODuration(details.time_to_complete, t)}
                </div>
              </div>

              <div className="flex flex-col gap-1 p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-100 dark:border-slate-800">
                <div className="flex items-center gap-2 text-slate-500 text-xs uppercase font-bold">
                  <Star className="w-4 h-4" />
                  {t('Рейтинг')}
                </div>
                <div className="font-semibold text-slate-700 dark:text-slate-200 flex items-center gap-1">
                  <span>{averageRating.toFixed(1)}</span>
                  <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                </div>
              </div>
            </div>

            <div className="flex flex-wrap gap-4 pt-4 border-t border-slate-100 dark:border-slate-800">
              <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
                <Layers className="w-4 h-4 text-brand-500" />
                <span className="font-medium">
                  {details.total_modules} {t('модулів')}
                </span>
              </div>
              <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
                <BookOpen className="w-4 h-4 text-blue-500" />
                <span className="font-medium">
                  {details.total_lessons} {t('уроків')}
                </span>
              </div>
              <div className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
                <FileCheck className="w-4 h-4 text-green-500" />
                <span className="font-medium">
                  {details.total_tests} {t('тестів')}
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  const renderReviewsSection = () => {
    const AddReviewButton = () => (
      <Button
        variant="outline"
        size="sm"
        onClick={() => setIsAddReviewModalOpen(true)}
      >
        <Plus className="w-4 h-4 mr-2" />
        {t('Додати відгук')}
      </Button>
    )

    if (!reviews || reviews.length === 0) {
      return (
        <Card className="mb-8 overflow-hidden shadow-sm border border-slate-200 dark:border-slate-800">
          <CardHeader className="pb-4 border-b border-slate-100 dark:border-slate-800 flex flex-row items-center justify-between">
            <h3 className="text-xl font-bold text-slate-800 dark:text-slate-100 flex items-center gap-2">
              <MessageSquare className="w-5 h-5 text-brand-600" />
              {t('Відгуки студентів')}
              <span className="ml-2 text-sm font-normal text-slate-500 bg-slate-100 dark:bg-slate-800 px-2.5 py-0.5 rounded-full">
                0
              </span>
            </h3>
            <AddReviewButton />
          </CardHeader>
          <CardContent className="p-8 text-center">
            <div className="w-16 h-16 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-4">
              <MessageSquare className="w-8 h-8 text-slate-400 dark:text-slate-500" />
            </div>
            <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100 mb-1">
              {t('Відгуків поки немає')}
            </h3>
            <p className="text-slate-500 dark:text-slate-400">
              {t('Будьте першим, хто поділиться враженнями про цей курс!')}
            </p>
          </CardContent>
        </Card>
      )
    }

    const hasManyReviews = reviews.length > 3
    const displayedReviews = isReviewsExpanded ? reviews : reviews.slice(0, 3)

    return (
      <Card className="mb-8 overflow-hidden shadow-sm border border-slate-200 dark:border-slate-800">
        <CardHeader className="pb-4 border-b border-slate-100 dark:border-slate-800 flex flex-row items-center justify-between">
          <h3 className="text-xl font-bold text-slate-800 dark:text-slate-100 flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-brand-600" />
            {t('Відгуки студентів')}
            <span className="ml-2 text-sm font-normal text-slate-500 bg-slate-100 dark:bg-slate-800 px-2.5 py-0.5 rounded-full">
              {reviews.length}
            </span>
          </h3>

          <AddReviewButton />
        </CardHeader>

        <CardContent className="p-0">
          <div className="divide-y divide-slate-100 dark:divide-slate-800">
            {displayedReviews.map(review => {
              const userInitials =
                `${review.user.name.charAt(0)}${review.user.surname.charAt(0)}`.toUpperCase()
              const fullName = `${review.user.name} ${review.user.surname}`

              return (
                <div
                  key={review.id}
                  className="p-6 hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors"
                >
                  <div className="flex items-start gap-4">
                    <Avatar className="w-10 h-10 border border-slate-200 dark:border-slate-700">
                      <AvatarImage
                        src={review.user.profile_picture || undefined}
                        alt={fullName}
                      />
                      <AvatarFallback className="bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 font-medium">
                        {userInitials}
                      </AvatarFallback>
                    </Avatar>

                    <div className="flex-1 min-w-0">
                      <div className="flex flex-wrap items-center justify-between gap-2 mb-1">
                        <h4 className="text-sm font-semibold text-slate-900 dark:text-slate-100 truncate">
                          {fullName}
                        </h4>
                        <span className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {formatShortDate(review.created_at)}
                        </span>
                      </div>

                      <div className="flex items-center mb-2">
                        {[...Array(5)].map((_, i) => (
                          <Star
                            key={i}
                            className={`w-3.5 h-3.5 ${i < review.rating ? 'fill-yellow-400 text-yellow-400' : 'fill-slate-200 text-slate-200 dark:fill-slate-700 dark:text-slate-700'}`}
                          />
                        ))}
                      </div>

                      <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
                        {review.comment}
                      </p>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>

          {hasManyReviews && (
            <div className="p-4 border-t border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/20 flex justify-center">
              <Button
                variant="ghost"
                onClick={() => setIsReviewsExpanded(prev => !prev)}
                className="text-slate-600 dark:text-slate-400 hover:text-brand-600 dark:hover:text-brand-400"
              >
                {isReviewsExpanded ? (
                  <>
                    <ChevronUp className="w-4 h-4 mr-2" />
                    {t('Згорнути відгуки')}
                  </>
                ) : (
                  <>
                    <ChevronDown className="w-4 h-4 mr-2" />
                    {t('Показати більше відгуків')}
                  </>
                )}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    )
  }

  const renderStarSection = () => {
    const totalCount = reviews.length
    const starLevels = [5, 4, 3, 2, 1]

    return (
      <Card className="mb-8 overflow-hidden shadow-sm border border-slate-200 dark:border-slate-800">
        <CardHeader className="pb-4 border-b border-slate-100 dark:border-slate-800">
          <h3 className="text-xl font-bold text-slate-800 dark:text-slate-100 flex items-center gap-2">
            <Star className="w-5 h-5 text-brand-600" />
            {t('Рейтинг курсу')}
          </h3>
        </CardHeader>

        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row gap-8 items-center">
            <div className="flex flex-col items-center justify-center min-w-[200px] text-center">
              <div className="text-5xl font-extrabold text-slate-900 dark:text-slate-100 mb-2">
                {averageRating.toFixed(1)}
              </div>

              <div className="flex items-center gap-1 mb-2">
                {[1, 2, 3, 4, 5].map(star => (
                  <Star
                    key={star}
                    className={`w-5 h-5 ${
                      star <= Math.round(averageRating)
                        ? 'fill-yellow-400 text-yellow-400'
                        : 'fill-slate-200 text-slate-200 dark:fill-slate-700 dark:text-slate-700'
                    }`}
                  />
                ))}
              </div>

              <p className="text-sm text-slate-500 dark:text-slate-400">
                {t('На основі')}{' '}
                <span className="font-semibold text-slate-700 dark:text-slate-200">
                  {totalCount}
                </span>{' '}
                {t('відгуків')}
              </p>
            </div>

            <div className="flex-1 w-full space-y-3">
              {starLevels.map(level => {
                const count = distribution[level] || 0
                const percentage =
                  totalCount > 0 ? (count / totalCount) * 100 : 0

                return (
                  <div key={level} className="flex items-center gap-3 text-sm">
                    <div className="flex items-center gap-1 w-16 shrink-0 text-slate-600 dark:text-slate-400 font-medium">
                      <span>{level}</span>
                      <Star className="w-3.5 h-3.5 fill-slate-400 text-slate-400" />
                    </div>

                    <div className="flex-1 h-2.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-yellow-400 rounded-full transition-all duration-500 ease-out"
                        style={{ width: `${percentage}%` }}
                      />
                    </div>

                    <div className="w-20 shrink-0 text-right text-slate-500 dark:text-slate-500 text-xs">
                      <span className="font-semibold text-slate-700 dark:text-slate-300 mr-1">
                        {count}
                      </span>
                      ({Math.round(percentage)}%)
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  const renderFooterSection = () => {
    if (!course || !course.course) return null

    // if (!course.course.is_published) {
    // }
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
      />

      <main
        className={`flex-1 flex flex-col transition-all duration-300 ease-in-out ${isSidebarCollapsed ? 'ml-28' : 'ml-64'} ${isCourseSidebarCollapsed ? 'mr-20' : 'mr-80'}`}
      >
        <CourseHeader
          title={t('Курс') + ' ' + (course?.course.title || t('Назва курсу'))}
          description={t('Розпочніть свій шлях навчання вже сьогодні!')}
        />
        <div className="p-6 max-w-4xl mx-auto w-full">
          {renderCourseInfoSection()}
          {renderAuthorSection()}
          {course?.course.is_published && renderReviewsSection()}
          {course?.course.is_published && renderStarSection()}
          {renderFooterSection()}
          <div className="mt-6">
            <h1 className="text-2xl font-bold mb-4">
              Вміст footer з кнопками і перенаправлення на сторінки уроків
              тестів ...
            </h1>
          </div>
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
