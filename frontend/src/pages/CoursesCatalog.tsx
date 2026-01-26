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
  getCourseService,
  sorting,
} from '@/features/course'
import { useChoicesData } from '@/shared/hooks/useChoiceData'
import { useUserCoursesStatus } from '@/shared/hooks/useUserCoursesStatus'

interface Option {
  value: string
  label: string
}

const CoursesCatalog = () => {
  const { t } = useI18n()
  const { profileData, loading, error, refreshProfile } = useProfileData()
  const {
    choicesData,
    loading: choicesLoading,
    error: choicesError,
    refreshChoices,
  } = useChoicesData()
  const { getItemStatus, loading: statusLoading } = useUserCoursesStatus()
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [categoryFilter, setCategoryFilter] = useState<string[]>([])
  const [sortingFilter, setSortingFilter] = useState<string[]>([])
  const [levelFilter, setLevelFilter] = useState<string>('')
  const [categories, setCategories] = useState<Option[]>([])
  const [levels, setLevels] = useState<Option[]>([])
  const [sort, setSort] = useState<Option[]>([])
  const [page, setPage] = useState<number>(1)
  const [totalPages, setTotalPages] = useState<number>(1)
  const [totalCourses, setTotalCourses] = useState<number>(0)
  const [countAllCourses, setCountAllCourses] = useState<number>(0)
  const [certificatesIssued, setCertificatesIssued] = useState<number>(0)
  const [courses, setCourses] = useState<AllCoursesResponse['courses']>([])
  const [averageRating, setAverageRating] = useState<number>(0)
  const [courseError, setCourseError] = useState<string>('')
  const [courseLoading, setCourseLoading] = useState(false)

  useEffect(() => {
    async function fetchAllCourses() {
      try {
        const response = await getCourseService.getCountAllCourses()
        setCountAllCourses(response.count)
      } catch (err) {
        setCourseError(t('Помилка завантаження кількості курсів: ') + err)
      }
    }

    fetchAllCourses()
  }, [])

  const fetchCourses = async () => {
    setCourseLoading(true)
    try {
      const searchCourse = {
        page: page,
        category: categoryFilter,
        sort_keys: sortingFilter,
        level: levelFilter === t('Всі рівні') ? '' : levelFilter,
        search: searchQuery,
      }
      const response = await getCourseService.getAllCourses(searchCourse)
      setCourses(response.courses)
      setTotalCourses(response.total_courses)
      setTotalPages(response.total_pages)
      setPage(response.page)
      setCertificatesIssued(response.certificates_issued)
      setAverageRating(response.average_rating)
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
    if (choicesData) {
      const categoriesData: Option[] = Object.entries(
        choicesData.category[0]
      ).map(([key, label]) => ({
        value: key,
        label,
      }))
      const levelsData: Option[] = Object.entries(choicesData.levels[0]).map(
        ([key, label]) => ({
          value: key,
          label,
        })
      )

      setCategories(categoriesData)
      setLevels(levelsData)
      setSort(sorting(t))
    }
  }, [choicesData])

  useEffect(() => {
    if (courseError) {
      const timer = setTimeout(() => setCourseError(''), 15000)
      return () => clearTimeout(timer)
    }
  }, [courseError])

  useEffect(() => {
    fetchCourses()
  }, [categoryFilter, levelFilter, sortingFilter, page])

  if (loading && choicesLoading && courseLoading && statusLoading) {
    return <LoadingProfile message={t('Завантаження...')} />
  }

  if (error || choicesError || !profileData) {
    return (
      <ErrorProfile
        error={
          error || choicesError || t('Помилка завантаження даних користувача')
        }
        onRetry={() => {
          refreshProfile()
          refreshChoices()
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
    <div className="flex h-screen w-full bg-background overflow-hidden">
      <Sidebar userInfo={userInfo} />

      <div
        className="ml-64 flex-1 h-full overflow-y-auto"
        style={{ colorScheme: 'dark' }}
      >
        <CourseHeader
          title={t('Підібрати курс')}
          description={t('Підберіть курс за вашими інтересами та цілями')}
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
              options={categories}
              selected={categoryFilter}
              onChange={setCategoryFilter}
              placeholder={t('Категорії')}
              className="w-48"
              countLabel={t('вибраних категорій')}
            />

            <Select value={levelFilter} onValueChange={setLevelFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder={t('Рівень')} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem key={''} value={t('Всі рівні')}>
                  {t('Всі рівні')}
                </SelectItem>
                {levels.map(level => (
                  <SelectItem key={level.value} value={level.value}>
                    {level.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <MultiSelect
              options={sort}
              selected={sortingFilter}
              onChange={setSortingFilter}
              placeholder={t('Сортувати')}
              className="w-48"
              countLabel={t('вибраних сортувань')}
            />
          </div>
          <div className="grid md:grid-cols-4 gap-6 mb-8">
            <StatCard
              icon={BookOpen}
              value={countAllCourses}
              label={t('Всього курсів')}
              iconBgClassName="bg-blue-100"
              iconClassName="text-blue-600"
            />
            <StatCard
              icon={CheckCircle}
              value={totalCourses}
              label={t('Знайдено')}
              iconBgClassName="bg-green-100"
              iconClassName="text-green-600"
            />

            <StatCard
              icon={Star}
              value={averageRating}
              label={t('Середній рейтинг')}
              iconBgClassName="bg-yellow-100"
              iconClassName="text-yellow-600"
            />

            <StatCard
              icon={Users}
              value={certificatesIssued}
              label={t('Видано сертифікатів')}
              iconBgClassName="bg-purple-100"
              iconClassName="text-purple-600"
            />
          </div>
          <div className="flex flex-wrap justify-center gap-6">
            {courses.map(course => {
              const { status, progress, inWishlist } = getItemStatus(
                course.course.id
              )

              return (
                <div
                  key={course.course.id}
                  className="w-full sm:w-[48%] xl:w-[32%]"
                >
                  <CourseCard
                    id={course.course.id}
                    title={course.course.title}
                    description={course.course.description}
                    coverImage={course.course.cover_image}
                    instructor={
                      course.course.owner.name +
                      ' ' +
                      course.course.owner.surname
                    }
                    instructorId={course.course.owner.id}
                    category={course.course.category}
                    badgeStatus={course.course.details.level}
                    badgeType={'level'}
                    rating={course.course.details.rating}
                    students={
                      course.course.details.number_completed +
                      course.course.details.number_of_active
                    }
                    duration={course.course.details.time_to_complete}
                    status={status}
                    progress={progress}
                    inWishlist={inWishlist}
                    findCourse={true}
                  />
                </div>
              )
            })}
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

export default CoursesCatalog
