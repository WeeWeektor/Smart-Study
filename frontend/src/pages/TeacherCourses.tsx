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
import { useState } from 'react'
import type { AllCoursesResponse } from '@/features/courses'

const TeacherCourses = () => {
  const { t } = useI18n()
  const navigate = useNavigate()
  const { name: teacherName, id: teacherId } = useParams<{
    name: string
    id: string
  }>()
  const { profileData, loading, error, refreshProfile } = useProfileData()
  const [searchQuery, setSearchQuery] = useState<string>('')
  const [categoryFilter, setCategoryFilter] = useState<string[]>([])
  const [sortingFilter, setSortingFilter] = useState<string[]>([])
  const [levelFilter, setLevelFilter] = useState<string>('')
  const [categories, setCategories] = useState<Option[]>([])
  const [levels, setLevels] = useState<Option[]>([])
  const [sort, setSort] = useState<Option[]>([])
  const [courseError, setCourseError] = useState<string>('')
  const [courseLoading, setCourseLoading] = useState(false)
  const [courses, setCourses] = useState<AllCoursesResponse['courses']>([])
  const [page, setPage] = useState<number>(1)
  const [totalPages, setTotalPages] = useState<number>(1)

  if (loading) {
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

  const currentUserId = profileData.user.id
  const isOwner = currentUserId === teacherId

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
              : t('Курси викладача') +
                ' ' +
                userInfo.name +
                ' ' +
                userInfo.surname
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

        <main>
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
            {isOwner && (
              <MultiSelect
                options={statuses}
                selected={statusesFilter}
                onChange={setStatusesFilter}
                placeholder={t('Всі статуси')}
                className="w-48"
                countLabel={t('вибраних статусів')}
              />
            )}
          </div>
          <div className="grid md:grid-cols-4 gap-6 mb-8">
            <StatCard
              icon={BookOpen}
              value={countAllCourses}
              label={t('Всього курсів')}
              iconBgClassName="bg-blue-100"
              iconClassName="text-blue-600"
            />
            {(isOwner && (
              <StatCard
                icon={CheckCircle}
                value={totalPublishedCourses}
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
              value={certificatesIssued}
              label={t('Загальна кількість студентів')}
              iconBgClassName="bg-purple-100"
              iconClassName="text-purple-600"
            />
          </div>
          <div className="flex flex-wrap justify-center gap-6">
            {courses.map(course => (
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
                    course.course.owner.name + ' ' + course.course.owner.surname
                  }
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
