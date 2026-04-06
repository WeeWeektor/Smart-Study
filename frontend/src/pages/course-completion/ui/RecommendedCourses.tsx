import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useI18n } from '@/shared/lib'
import { Button, CourseCard, Skeleton } from '@/shared/ui'
import { ArrowRight, ChevronDown, ChevronUp, Sparkles } from 'lucide-react'
import {
  courseRecommendationsService,
  type CourseWrapper,
} from '@/features/course'
import { useUserCoursesStatus } from '@/shared/hooks/useUserCoursesStatus'

interface RecommendedCoursesProps {
  courseId: string
  status: 'passed' | 'failed'
  title?: string
  limit?: number
}

const ITEMS_PER_ROW = 3

export const RecommendedCourses = ({
  courseId,
  status,
  title,
  limit = 12,
}: RecommendedCoursesProps) => {
  const { t } = useI18n()
  const navigate = useNavigate()

  const [recommendations, setRecommendations] = useState<CourseWrapper[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [isExpanded, setIsExpanded] = useState(false)

  const { getItemStatus } = useUserCoursesStatus()

  useEffect(() => {
    const fetchRecommendations = async () => {
      if (!courseId) return

      try {
        setLoading(true)
        setError('')

        const data = await courseRecommendationsService.getRecommendations(
          courseId,
          status,
          limit
        )
        setRecommendations(data)
      } catch (e) {
        setError(
          t('Не вдалося завантажити рекомендації: ') +
            (e instanceof Error ? e.message : String(e))
        )
      } finally {
        setLoading(false)
      }
    }

    fetchRecommendations()
  }, [courseId, limit, status, t])

  const displayedCourses = isExpanded
    ? recommendations
    : recommendations.slice(0, ITEMS_PER_ROW)

  const hasMore = recommendations.length > ITEMS_PER_ROW

  if (loading) {
    return <RecommendationsSkeleton />
  }

  if (recommendations.length === 0 && !error) {
    return null
  }

  return (
    <div className="w-full mt-6 animate-in fade-in duration-700">
      <div className="relative py-4 mb-0">
        <div className="absolute inset-0 flex items-center" aria-hidden="true">
          <div className="w-full h-px bg-gradient-to-r from-transparent via-slate-300 to-transparent dark:via-slate-700 opacity-70"></div>
        </div>
        <div className="relative flex justify-center">
          <span className="bg-background px-3 text-brand-500 shadow-sm rounded-full border border-slate-100 dark:border-slate-800 py-1">
            <Sparkles className="h-5 w-5" />
          </span>
        </div>
      </div>

      <div className="flex items-center justify-between mb-6 px-24 max-w-[1600px] mx-auto">
        <div className="flex items-center gap-2">
          <Sparkles className="w-6 h-6 text-brand-600" />
          <h3 className="text-2xl font-bold text-foreground">
            {title ||
              (status === 'passed'
                ? t('Що вивчати далі')
                : t('Рекомендовані альтернативи'))}
          </h3>
        </div>

        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate('/find-new-courses')}
          className="text-muted-foreground hover:text-brand-600 gap-2 hidden sm:flex w-auto px-4 group"
        >
          {t('До каталогу')}
          <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
        </Button>
      </div>

      {error && (
        <div className="max-w-4xl mx-auto mb-4 p-3 bg-red-100 text-red-700 rounded-md text-sm font-medium border border-red-200">
          {error}
        </div>
      )}

      <div className="flex flex-wrap justify-center gap-6 mx-6">
        {displayedCourses.map(item => {
          const course = item.course
          const {
            status: userStatus,
            progress,
            inWishlist,
          } = getItemStatus(course.id)

          return (
            <div key={course.id} className="w-full sm:w-[48%] xl:w-[32%]">
              <CourseCard
                id={course.id}
                title={course.title}
                description={course.description}
                coverImage={course.cover_image}
                instructor={
                  course.owner
                    ? `${course.owner.name} ${course.owner.surname}`
                    : t('Інструктор')
                }
                instructorId={course.owner?.id}
                category={course.category}
                badgeStatus={course.details?.level}
                badgeType={'level'}
                rating={course.details?.rating || 0}
                students={
                  (course.details?.number_completed || 0) +
                  (course.details?.number_of_active || 0)
                }
                duration={course.details?.time_to_complete}
                status={userStatus}
                progress={progress}
                inWishlist={inWishlist}
                findCourse={true}
              />
            </div>
          )
        })}
      </div>

      {hasMore && (
        <div className="flex justify-center pt-8">
          <Button
            variant="outline"
            onClick={() => setIsExpanded(!isExpanded)}
            className="gap-2 min-w-[200px] shadow-sm mb-6"
          >
            {isExpanded ? (
              <>
                {t('Згорнути')}
                <ChevronUp className="w-4 h-4" />
              </>
            ) : (
              <>
                {t('Показати ще')} ({recommendations.length - ITEMS_PER_ROW})
                <ChevronDown className="w-4 h-4" />
              </>
            )}
          </Button>
        </div>
      )}
    </div>
  )
}

const RecommendationsSkeleton = () => (
  <div className="w-full space-y-6 mt-8 px-4">
    <div className="w-full h-px bg-slate-200 dark:bg-slate-800 mb-10" />

    <div className="flex items-center gap-2 max-w-[1600px] mx-auto">
      <Skeleton className="h-8 w-8 rounded-full" />
      <Skeleton className="h-8 w-64 rounded-md" />
    </div>
    <div className="flex flex-wrap justify-center gap-6 w-full">
      {[1, 2, 3].map(i => (
        <div
          key={i}
          className="w-full sm:max-w-[320px] lg:max-w-[350px] flex flex-col space-y-3"
        >
          <Skeleton className="h-[180px] w-full rounded-xl" />
          <div className="space-y-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-3/4" />
          </div>
          <div className="flex justify-between pt-2">
            <Skeleton className="h-8 w-24" />
            <Skeleton className="h-8 w-8 rounded-full" />
          </div>
        </div>
      ))}
    </div>
  </div>
)
