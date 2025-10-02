import { useI18n } from '@/shared/lib'
import { Sidebar } from '@/widgets/layout'
import { CourseHeader } from '@/widgets/course'
import {
  Alert,
  AlertDescription,
  Button,
  CourseCard,
  EmptyCourses,
  ErrorProfile,
  Input,
  LoadingProfile,
  MultiSelect,
  Pagination,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  StatCard,
} from '@/shared/ui'
import { useProfileData } from '@/shared/hooks/useProfileData'
import { useNavigate, useParams } from 'react-router-dom'
import {
  AlertCircle,
  BookOpen,
  CheckCircle,
  Search,
  Star,
  Users,
} from 'lucide-react'
import { useEffect, useState } from 'react'
import {
  type AllCoursesResponse,
  type CountTeacherCourseRequest,
  getCourseService,
  sorting,
  statues,
} from '@/features/course'

interface Option {
  value: string
  label: string
}

const TeacherCourses = () => {
  const { t } = useI18n()
  const navigate = useNavigate()
  const { profileData, loading, error, refreshProfile } = useProfileData()
  const { name: teacherName, id: teacherId } = useParams<{
    name: string
    id: string
  }>()
  const currentUserId = profileData?.user.id
  const isOwner = teacherId ? currentUserId === teacherId : true
  const resCourTeachId = isOwner ? currentUserId : teacherId

  const [searchQuery, setSearchQuery] = useState<string>('')
  const [sortingFilter, setSortingFilter] = useState<string[]>([])
  const [statusesFilter, setStatusesFilter] = useState<string>('')
  const [sort, setSort] = useState<Option[]>([])
  const [statuses, setStatuses] = useState<Option[]>([])
  const [courseError, setCourseError] = useState<string>('')
  const [courseLoading, setCourseLoading] = useState(false)
  const [courses, setCourses] = useState<AllCoursesResponse['courses']>([])
  const [page, setPage] = useState<number>(1)
  const [totalPages, setTotalPages] = useState<number>(1)
  const [countAllTeacherCourses, setCountAllTeacherCourses] =
    useState<number>(0)
  const [countPublishedTeacherCourses, setCountPublishedTeacherCourses] =
    useState<number>(0)
  const [countAnnouncements, setCountAnnouncements] = useState<number>(0)
  const [totalCourses, setTotalCourses] = useState<number>(0)
  const [averageRating, setAverageRating] = useState<number>(0)
  const [CountAllCourseInDBs, setCountAllCourseInDBs] = useState<number>(0)

  useEffect(() => {
    if (!resCourTeachId) return

    const request: CountTeacherCourseRequest = {
      author_id: resCourTeachId,
      owner: isOwner,
    }

    async function fetchCountTeacherCourses() {
      try {
        const response1 = await getCourseService.getCountTeacherCourses(request)
        setCountAllTeacherCourses(response1.allCourses)
        setCountPublishedTeacherCourses(response1.publishedCourses)
        const response2 = await getCourseService.getCountAllCourses()
        setCountAllCourseInDBs(response2.count)
        console.log(response1)
        console.log(response2)
      } catch (err) {
        setCourseError(t('Помилка завантаження кількості курсів: ') + err)
      }
    }

    fetchCountTeacherCourses()
  }, [currentUserId, isOwner])

  const fetchCourses = async () => {
    setCourseLoading(true)
    try {
      const searchCourse = {
        page: page,
        sort_keys: sortingFilter,
        status:
          statusesFilter === t('Всі рівні')
            ? isOwner
              ? 'all'
              : ''
            : statusesFilter,
        author_id: resCourTeachId,
        search: searchQuery,
        is_owner: isOwner,
      }
      const response = await getCourseService.getAllCourses(searchCourse)
      setCourses(response.courses)
      setTotalCourses(response.total_courses)
      setTotalPages(response.total_pages)
      setPage(response.page)
      setAverageRating(response.average_rating)
      setCountAnnouncements(response.count_announcements)
      setCourseError('')
    } catch (err: unknown) {
      if (err instanceof Error) {
        setCourseError(err.message)
      } else {
        setCourseError(String(err))
      }
      setCourses([])
    } finally {
      setCourseLoading(false)
    }
  }

  useEffect(() => {
    setSort(sorting(t))
    setStatuses(statues(t))
  }, [sortingFilter, statusesFilter])

  useEffect(() => {
    if (courseError) {
      const timer = setTimeout(() => setCourseError(''), 15000)
      return () => clearTimeout(timer)
    }
  }, [courseError])

  useEffect(() => {
    if (!resCourTeachId) return
    fetchCourses()
  }, [sortingFilter, statusesFilter, page, resCourTeachId])

  if (loading && courseLoading) {
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

  const handleCreateCourse = () => {
    navigate('/create-course')
  }

  return (
    <div className="min-h-screen bg-background">
      <Sidebar userInfo={userInfo} />

      <div className="ml-64">
        <CourseHeader
          title={
            isOwner
              ? t('Створені вами курси')
              : t('Курси викладача') + ' ' + teacherName
          }
          description={
            isOwner
              ? t('Додавайте й редагуйте ваші курси')
              : t('Переглядайте доступні курси цього викладача')
          }
          action={isOwner}
          onActionClick={isOwner ? handleCreateCourse : undefined}
          actionText={isOwner ? t('Створити') : undefined}
        />

        <main className="p-6">
          {courseError && (
            <Alert className="mb-6 border-destructive bg-destructive/10">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription className="text-destructive">
                {courseError}
              </AlertDescription>
            </Alert>
          )}
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
              <Input
                placeholder={t('Шукати курси...')}
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                className="pl-10"
              />
              <Button
                variant="secondary"
                size="round_md"
                className="text-muted-foreground hover:text-brand-600 dark:hover:text-brand-400"
                style={{ position: 'absolute', right: 0, top: 0 }}
                onClick={fetchCourses}
              >
                <Search className="absolute top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
              </Button>
            </div>

            <MultiSelect
              options={sort}
              selected={sortingFilter}
              onChange={setSortingFilter}
              placeholder={t('Сортувати')}
              className="w-48"
              countLabel={t('вибраних сортувань')}
            />

            {isOwner && (
              <Select value={statusesFilter} onValueChange={setStatusesFilter}>
                <SelectTrigger className="w-48">
                  <SelectValue placeholder={t('Рівень')} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem key={''} value={t('Всі рівні')}>
                    {t('Всі рівні')}
                  </SelectItem>
                  {statuses.map(status => (
                    <SelectItem key={status.value} value={status.value}>
                      {status.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          </div>
          <div className="grid md:grid-cols-4 gap-6 mb-8">
            {(isOwner && (
              <StatCard
                icon={BookOpen}
                value={countAllTeacherCourses}
                label={t('Всього курсів')}
                iconBgClassName="bg-blue-100"
                iconClassName="text-blue-600"
              />
            )) || (
              <StatCard
                icon={BookOpen}
                value={CountAllCourseInDBs}
                label={t('Всього курсів')}
                iconBgClassName="bg-blue-100"
                iconClassName="text-blue-600"
              />
            )}
            {(isOwner && (
              <StatCard
                icon={CheckCircle}
                value={countPublishedTeacherCourses}
                label={t('Опубліковані курсів')}
                iconBgClassName="bg-green-100"
                iconClassName="text-green-600"
              />
            )) || (
              <StatCard
                icon={CheckCircle}
                value={totalCourses}
                label={t('Знайдено')}
                iconBgClassName="bg-green-100"
                iconClassName="text-green-600"
              />
            )}

            <StatCard
              icon={Star}
              value={averageRating}
              label={t('Середній рейтинг')}
              iconBgClassName="bg-yellow-100"
              iconClassName="text-yellow-600"
            />

            <StatCard
              icon={Users}
              value={countAnnouncements}
              label={t('Загальна кількість студентів')}
              iconBgClassName="bg-purple-100"
              iconClassName="text-purple-600"
            />
          </div>
          <div className="flex flex-wrap justify-center gap-6">
            {(isOwner &&
              courses.map(course => (
                <div
                  key={course.course.id}
                  className="w-full sm:w-[48%] xl:w-[32%]"
                >
                  <CourseCard
                    id={course.course.id}
                    title={course.course.title}
                    description={course.course.description}
                    coverImage={course.course.cover_image}
                    instructorId={course.course.owner.id}
                    category={course.course.category}
                    badgeLabel={
                      course.course.is_published
                        ? t('Опублікований')
                        : t('Неопублікований')
                    }
                    badgeType={'published'}
                    rating={course.course.details.rating}
                    students={
                      course.course.details.number_completed +
                      course.course.details.number_of_active
                    }
                    duration={course.course.details.time_to_complete}
                    countModule={course.course.details.total_modules}
                    countLesson={course.course.details.total_lessons}
                    countTests={course.course.details.total_tests}
                    feedback_count={course.course.details.feedback_count}
                  />
                </div>
              ))) ||
              courses.map(course => (
                <div
                  key={course.course.id}
                  className="w-full sm:w-[48%] xl:w-[32%]"
                >
                  <CourseCard
                    id={course.course.id}
                    title={course.course.title}
                    description={course.course.description}
                    coverImage={course.course.cover_image}
                    instructorId={course.course.owner.id}
                    category={course.course.category}
                    badgeLabel={course.course.details.level}
                    badgeType={'level'}
                    rating={course.course.details.rating}
                    students={
                      course.course.details.number_completed +
                      course.course.details.number_of_active
                    }
                    duration={course.course.details.time_to_complete}
                    countModule={course.course.details.total_modules}
                    countLesson={course.course.details.total_lessons}
                    countTests={course.course.details.total_tests}
                    feedback_count={course.course.details.feedback_count}
                  />
                </div>
              ))}
          </div>
          <div>{courses.length === 0 && <EmptyCourses />}</div>
          <Pagination
            page={page}
            totalPages={totalPages}
            onPageChange={setPage}
          />
        </main>
      </div>
    </div>
  )
}

export default TeacherCourses
