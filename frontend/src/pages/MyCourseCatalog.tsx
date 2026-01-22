import { useI18n } from '@/shared/lib'
import { Sidebar } from '@/widgets/layout'
import { CourseHeader } from '@/widgets/course'
import {
  Alert,
  AlertDescription,
  CourseCard,
  EmptyCourses,
  ErrorProfile,
  LoadingProfile,
  StatCard,
} from '@/shared/ui'
import { useProfileData } from '@/shared/hooks/useProfileData'
import { AlertCircle, BookOpen, CheckCircle, Heart, Layers } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { type CourseWrapper, getCourseService } from '@/features/course'

type FilterType = 'all' | 'active' | 'completed' | 'wishlist'

type CourseWithStatus = CourseWrapper & {
  sourceType: 'wishlist' | 'enrolled' | 'completed'
}

const MyCourseCatalog = () => {
  const { t } = useI18n()
  const { profileData, loading, error, refreshProfile } = useProfileData()
  const [courseError, setCourseError] = useState<string>('')
  const [activeFilter, setActiveFilter] = useState<FilterType>('all')
  const [courseLoading, setCourseLoading] = useState(true)
  const [allCourses, setAllCourses] = useState<CourseWithStatus[]>([])

  useEffect(() => {
    if (courseError) {
      const timer = setTimeout(() => setCourseError(''), 15000)
      return () => clearTimeout(timer)
    }
  }, [courseError])

  const fetchCourses = async () => {
    setCourseLoading(true)
    try {
      const response = await getCourseService.getMyCourseCatalog()
      const wishlist = response.in_wishlist.map(cw => ({
        ...cw,
        sourceType: 'wishlist' as const,
      }))
      const enrolled = response.is_enrolled.map(cw => ({
        ...cw,
        sourceType: 'enrolled' as const,
      }))
      const completed = response.is_completed.map(cw => ({
        ...cw,
        sourceType: 'completed' as const,
      }))
      setAllCourses([...wishlist, ...enrolled, ...completed])
      setCourseError('')
    } catch (err: unknown) {
      if (err instanceof Error) {
        setCourseError(err.message)
      } else {
        setCourseError(String(err))
      }
      setAllCourses([])
    } finally {
      setCourseLoading(false)
    }
  }

  useEffect(() => {
    fetchCourses()
  }, [])

  const filteredCourses = useMemo(() => {
    switch (activeFilter) {
      case 'active':
        return allCourses.filter(c => c.sourceType === 'enrolled')
      case 'completed':
        return allCourses.filter(c => c.sourceType === 'completed')
      case 'wishlist':
        return allCourses.filter(c => c.sourceType === 'wishlist')
      case 'all':
      default:
        return allCourses
    }
  }, [allCourses, activeFilter])

  const getCardStatus = (sourceType: CourseWithStatus['sourceType']) => {
    switch (sourceType) {
      case 'completed':
        return 'completed'
      case 'enrolled':
        return 'in_progress'
      case 'wishlist':
      default:
        return 'not_started'
    }
  }

  const FilterButton = ({ type, label, icon: Icon, count }: any) => {
    const isActive = activeFilter === type
    return (
      <button
        onClick={() => setActiveFilter(type)}
        className={`
          flex items-center justify-center px-4 py-2 rounded-full text-sm font-medium transition-all duration-200
          whitespace-nowrap select-none ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2
          ${
            isActive
              ? 'bg-primary text-primary-foreground shadow-sm'
              : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground text-slate-600 dark:text-slate-400 hover:bg-slate-200/50 dark:hover:bg-slate-800'
          }
        `}
      >
        <Icon className={`w-4 h-4 mr-2 ${isActive ? 'text-red' : ''}`} />
        {label}
        {count > 0 && (
          <span
            className={`ml-2 text-[10px] px-2 py-0.5 rounded-full font-bold leading-none ${
              isActive
                ? 'bg-white text-primary'
                : 'bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300'
            }`}
          >
            {count}
          </span>
        )}
      </button>
    )
  }

  const counts = {
    active: allCourses.filter(c => c.sourceType === 'enrolled').length,
    completed: allCourses.filter(c => c.sourceType === 'completed').length,
    wishlist: allCourses.filter(c => c.sourceType === 'wishlist').length,
  }

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

  return (
    <div className="flex h-screen w-full bg-background overflow-hidden">
      <Sidebar userInfo={userInfo} />

      <div
        className="ml-64 flex-1 h-full overflow-y-auto"
        style={{ colorScheme: 'dark' }}
      >
        <CourseHeader
          title={t('Моя бібліотека')}
          description={t('Всі ваші курси та прогрес в одному місці')}
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

          <div className="w-full flex justify-center">
            <div className="inline-flex items-center justify-center p-1 bg-slate-100/80 dark:bg-slate-900/50 backdrop-blur-xl border border-slate-200 dark:border-slate-800 rounded-full shadow-sm">
              <FilterButton
                type="all"
                label={t('Всі курси')}
                icon={Layers}
                count={allCourses.length}
              />
              <FilterButton
                type="active"
                label={t('Активні')}
                icon={BookOpen}
                count={counts.active}
              />
              <FilterButton
                type="wishlist"
                label={t('Вішліст')}
                icon={Heart}
                count={counts.wishlist}
              />
              <FilterButton
                type="completed"
                label={t('Завершені')}
                icon={CheckCircle}
                count={counts.completed}
              />
            </div>
          </div>

          <div className="grid md:grid-cols-4 gap-6 mb-8 mt-6">
            <StatCard
              icon={Layers}
              value={allCourses.length}
              label={t('Всього курсів')}
              iconBgClassName="bg-blue-100"
              iconClassName="text-blue-600"
            />
            <StatCard
              icon={BookOpen}
              value={counts.active}
              label={t('Акивні курси')}
              iconBgClassName="bg-green-100"
              iconClassName="text-green-600"
            />

            <StatCard
              icon={Heart}
              value={counts.wishlist}
              label={t('Курси у вішлісті')}
              iconBgClassName="bg-yellow-100"
              iconClassName="text-yellow-600"
            />

            <StatCard
              icon={CheckCircle}
              value={counts.completed}
              label={t('Завершені курси')}
              iconBgClassName="bg-purple-100"
              iconClassName="text-purple-600"
            />
          </div>

          {/*<div className="flex flex-wrap justify-center gap-6">*/}
          {/*  {allCourses.map(course => (*/}
          {/*    <div*/}
          {/*      key={course.course.id}*/}
          {/*      className="w-full sm:w-[48%] xl:w-[32%]"*/}
          {/*    >*/}
          {/*      <CourseCard*/}
          {/*        id={course.course.id}*/}
          {/*        title={course.course.title}*/}
          {/*        description={course.course.description}*/}
          {/*        coverImage={course.course.cover_image}*/}
          {/*        instructor={*/}
          {/*          course.course.owner.name + ' ' + course.course.owner.surname*/}
          {/*        }*/}
          {/*        instructorId={course.course.owner.id}*/}
          {/*        category={course.course.category}*/}
          {/*        badgeStatus={course.course.details.level}*/}
          {/*        badgeType={'level'}*/}
          {/*        rating={course.course.details.rating}*/}
          {/*        students={*/}
          {/*          course.course.details.number_completed +*/}
          {/*          course.course.details.number_of_active*/}
          {/*        }*/}
          {/*        duration={course.course.details.time_to_complete}*/}
          {/*      />*/}
          {/*    </div>*/}
          {/*  ))}*/}
          {/*</div>*/}

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCourses.length > 0 ? (
              filteredCourses.map(wrapper => (
                <CourseCard
                  key={wrapper.course.id}
                  id={wrapper.course.id}
                  title={wrapper.course.title}
                  description={wrapper.course.description}
                  coverImage={wrapper.course.cover_image}
                  instructor={
                    wrapper.course.owner.name +
                    ' ' +
                    wrapper.course.owner.surname
                  }
                  instructorId={wrapper.course.owner.id}
                  category={wrapper.course.category}
                  badgeStatus={wrapper.course.details.level}
                  badgeType="level"
                  rating={wrapper.course.details.rating}
                  students={
                    wrapper.course.details.number_completed +
                    wrapper.course.details.number_of_active
                  }
                  duration={wrapper.course.details.time_to_complete}
                  // Додаткові пропси для правильного відображення:
                  status={getCardStatus(wrapper.sourceType)}
                  // Якщо у wrapper є поле progress (залежить від API), передаємо його, інакше 0
                  progress={(wrapper as any).progress || 0}
                  countModule={wrapper.course.details.total_modules}
                  countLesson={wrapper.course.details.total_lessons}
                  countTests={wrapper.course.details.total_tests}
                  feedback_count={wrapper.course.details.feedback_count}
                />
              ))
            ) : (
              // Empty State тепер показується коректно на всю ширину
              <div className="col-span-full">
                <EmptyCourses text={t('У цій категорії поки немає курсів.')} />
              </div>
            )}
          </div>

          {/*<div>*/}
          {/*  {allCourses.length === 0 && (*/}
          {/*    <EmptyCourses text="У цій категорії поки немає курсів." />*/}
          {/*  )}*/}
          {/*</div>*/}
          {/*<Pagination*/}
          {/*  page={page}*/}
          {/*  totalPages={totalPages}*/}
          {/*  onPageChange={setPage}*/}
          {/*/>*/}
        </main>
      </div>
    </div>
  )
}

export default MyCourseCatalog
