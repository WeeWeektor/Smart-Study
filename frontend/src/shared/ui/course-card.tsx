import {
  Badge,
  Button,
  Card,
  CardContent,
  ConfirmModal,
  Progress,
  UserModal,
} from '@/shared/ui'
import {
  BookOpen,
  Clock,
  Eye,
  FileCheck,
  Layers,
  MessageSquare,
  RefreshCw,
  Rocket,
  Star,
  Trash2,
  UploadCloud,
  Users,
} from 'lucide-react'
import { formatLabel, parseISODuration, useI18n } from '@/shared/lib'
import { Link, useNavigate } from 'react-router-dom'
import React from 'react'
import { deleteCourseService } from '@/features/course'

interface CourseCardProps {
  id: string
  title: string
  description: string
  coverImage: string
  instructor?: string
  instructorId: string
  category: string
  badgeStatus: string | boolean
  badgeType: 'level' | 'status' | 'published'
  rating: number
  students: number
  duration: string
  progress?: number
  nextLesson?: string
  status?: 'completed' | 'not_started' | 'in_progress'
  countModule?: number
  countLesson?: number
  countTests?: number
  feedback_count?: number
  inWishlist?: boolean
}

export const CourseCard = ({
  id,
  title,
  description,
  coverImage,
  instructor,
  instructorId,
  category,
  badgeStatus,
  badgeType,
  rating,
  students,
  duration,
  progress,
  nextLesson,
  status,
  countModule,
  countLesson,
  countTests,
  feedback_count,
  inWishlist,
}: CourseCardProps) => {
  const { t } = useI18n()
  const navigate = useNavigate()
  const [isModalOpen, setIsModalOpen] = React.useState(false)
  const [isConfirmDelOpen, setIsConfirmDelOpen] = React.useState(false)

  const getBadgeLabel = () => {
    if (badgeType === 'published') {
      return badgeStatus ? t('Опублікований') : t('Чорновик')
    }
    return formatLabel(String(badgeStatus), t)
  }

  const handleDelete = async () => {
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

  const handleDeleteFromWishlist = async () => {
    try {
      const response = await deleteCourseService.deleteCourseFromWishlist({
        courseId: id,
      })
      navigate(
        `/my-courses-subscriptions/?Message=${encodeURIComponent(
          response.message
        )}&Status=${response.status}&Action=delete`
      )
    } catch (error) {
      navigate(
        `/my-courses-subscriptions/?Message=${encodeURIComponent(
          error instanceof Error
            ? error.message
            : t('Не вдалось видалити курс з вішліста')
        )}&Status=0&Action=delete`
      )
    } finally {
      setIsConfirmDelOpen(false)
    }
  }

  return (
    <Card
      key={id}
      className="h-full flex flex-col overflow-hidden hover:shadow-lg transition-shadow cursor-pointer bg-white dark:bg-slate-800 dark:hover:shadow-gray-700"
    >
      <div className="relative w-full overflow-hidden bg-slate-200 dark:bg-slate-700 rounded-lg">
        {coverImage ? (
          <div className="w-full" style={{ paddingTop: '56.25%' }}>
            <img
              src={coverImage}
              alt={title}
              className="absolute top-0 left-0 w-full h-full object-contain object-center"
            />
          </div>
        ) : (
          <div className="w-full" style={{ paddingTop: '56.25%' }}>
            <div className="absolute inset-0 flex items-center justify-center text-slate-400 dark:text-slate-300">
              <BookOpen className="w-12 h-12" />
            </div>
          </div>
        )}
        <div className="absolute top-4 right-4">
          <Badge
            className={`font-medium ${getBadgeColor(badgeStatus, badgeType)}`}
          >
            {getBadgeLabel()}
          </Badge>
        </div>
      </div>

      <CardContent className="flex-1 flex flex-col p-6 text-slate-900 dark:text-slate-100">
        <h3 className="font-semibold text-slate-900 dark:text-slate-200 line-clamp-2 mb-2 h-8 leading-6">
          {title}
        </h3>
        <p className="text-sm text-slate-600 dark:text-slate-400 mb-4 line-clamp-2 h-10 leading-5">
          {' '}
          {description}
        </p>

        <div className="flex items-center justify-between text-sm text-slate-700 dark:text-slate-400 mb-4">
          {instructor ? (
            <>
              <span
                onClick={() => {
                  setIsModalOpen(true)
                }}
                className="cursor-pointer text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200 transition-colors hover:underline"
              >
                {instructor}
              </span>

              <UserModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                userName={instructor}
                userId={instructorId}
                role={t('Викладач')}
              />
            </>
          ) : (
            <span className="flex items-center gap-1">
              <MessageSquare className="w-4 h-4 text-orange-600" />
              {feedback_count} {t('відгуків')}
            </span>
          )}

          <span className={`font-medium text-purple-600`}>
            {formatLabel(category, t)}
          </span>
        </div>

        {!instructor && (
          <>
            <div className="flex items-center justify-between gap-4 text-sm text-slate-600 dark:text-slate-300 mb-4">
              <span className="flex items-center gap-1">
                <BookOpen className="w-4 h-4 text-blue-600" />
                {countLesson} {t('уроків')}
              </span>

              <span className="text-slate-400">•</span>

              <span className="flex items-center gap-1">
                <FileCheck className="w-4 h-4 text-green-600" />
                {countTests} {t('тестів')}
              </span>

              <span className="text-slate-400">•</span>

              <span className="flex items-center gap-1">
                <Layers className="w-4 h-4 text-purple-600" />
                {countModule} {t('модулів')}
              </span>
            </div>
          </>
        )}

        <div className="flex items-center justify-between text-sm text-slate-800 dark:text-slate-400 mb-4">
          <div className="flex items-center">
            <Star className="w-4 h-4 text-yellow-400 mr-1" />
            {rating}
          </div>
          <div className="flex items-center">
            <Users className="w-4 h-4 mr-1 dark:text-slate-300" />
            {students}
          </div>
          <div className="flex items-center">
            <Clock className="w-4 h-4 mr-1 dark:text-slate-300" />
            {parseISODuration(duration, t)}
          </div>
        </div>

        {progress !== undefined && progress > 0 && (
          <div className="mb-4">
            <div className="flex justify-between text-sm mb-2">
              <span className="text-slate-600">{t('Прогрес')}</span>
              <span className="font-medium">{progress}%</span>
            </div>
            <Progress
              value={progress}
              className="h-2 bg-slate-200 dark:bg-slate-700"
            />
            {nextLesson && (
              <p className="text-xs text-slate-500 mt-2">
                {t('Наступний:')} {nextLesson}
              </p>
            )}
          </div>
        )}

        <div className="mt-auto pt-2">
          {status && (
            <div className="flex gap-2">
              {status === 'completed' ? (
                <Link to={`/course-review/${id}`} className="flex-1">
                  <Button variant="outline" className="w-full">
                    <Eye className="w-4 h-4 mr-2" />
                    {t('Переглянути')}
                  </Button>
                </Link>
              ) : (
                <>
                  <Link to={`/course-review/${id}`} className="flex-1">
                    <Button className="w-full bg-brand-600 hover:bg-brand-700">
                      {status === 'not_started' ? (
                        <Rocket className="w-4 h-4 mr-2" />
                      ) : (
                        <RefreshCw className="w-4 h-4 mr-2" />
                      )}
                      {status === 'not_started'
                        ? t('Розпочати')
                        : t('Продовжити')}
                    </Button>
                  </Link>
                  {status === 'not_started' && inWishlist && (
                    <>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200"
                        onClick={() => setIsConfirmDelOpen(true)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                      <ConfirmModal
                        isOpen={isConfirmDelOpen}
                        onClose={() => setIsConfirmDelOpen(false)}
                        onConfirm={handleDeleteFromWishlist}
                        title={t('Видалення курсу')}
                        description={t(
                          'Ви впевнені, що хочете видалити цей курс з вішліста?'
                        )}
                      />
                    </>
                  )}
                </>
              )}
            </div>
          )}

          {badgeType && badgeType === 'published' && (
            <div className="flex gap-2">
              {badgeStatus ? (
                <Link to={`/course-review/${id}`} className="flex-1">
                  <Button variant="outline" className="w-full">
                    <Eye className="w-4 h-4 mr-2" />
                    {t('Переглянути')}
                  </Button>
                </Link>
              ) : (
                <>
                  <Link to={`/course-review/${id}`} className="flex-1">
                    <Button className="w-full bg-brand-600 hover:bg-brand-700">
                      <UploadCloud className="w-4 h-4 mr-2" />
                      {t('Переглянути та опублікувати')}
                    </Button>
                  </Link>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200"
                    onClick={() => setIsConfirmDelOpen(true)}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                  <ConfirmModal
                    isOpen={isConfirmDelOpen}
                    onClose={() => setIsConfirmDelOpen(false)}
                    onConfirm={handleDelete}
                    title={t('Видалення курсу')}
                    description={t(
                      'Ви впевнені, що хочете видалити цей курс? Цю дію неможливо скасувати.'
                    )}
                  />
                </>
              )}
            </div>
          )}

          {badgeType && badgeType === 'level' && (
            <div className="flex gap-2">
              <Link to={`/course-review/${id}`} className="flex-1">
                <Button className="w-full bg-brand-600 hover:bg-brand-700">
                  <Eye className="w-4 h-4 mr-2" />
                  {t('Переглянути')}
                </Button>
              </Link>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

const getBadgeColor = (
  status: string | boolean,
  type: 'level' | 'status' | 'published'
) => {
  switch (type) {
    case 'level':
      switch (String(status).toLowerCase()) {
        case 'beginner':
          return 'bg-green-100 text-green-600 dark:bg-green-800 dark:text-green-300 hover:bg-green-200 hover:text-green-700 dark:hover:bg-green-700 dark:hover:text-green-200'
        case 'intermediate':
          return 'bg-yellow-100 text-yellow-600 dark:bg-yellow-800 dark:text-yellow-300 hover:bg-yellow-200 hover:text-yellow-700 dark:hover:bg-yellow-700 dark:hover:text-yellow-200'
        case 'advanced':
          return 'bg-red-100 text-red-600 dark:bg-red-800 dark:text-red-300 hover:bg-red-200 hover:text-red-700 dark:hover:bg-red-700 dark:hover:text-red-200'
        default:
          return 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300 hover:bg-slate-200 hover:text-slate-700 dark:hover:bg-slate-700 dark:hover:text-slate-200'
      }
    case 'status':
      switch (String(status).toLowerCase()) {
        case 'completed':
          return 'bg-green-100 text-green-600 dark:bg-green-800 dark:text-green-300 hover:bg-green-200 hover:text-green-700 dark:hover:bg-green-700 dark:hover:text-green-200'
        case 'in_progress':
          return 'bg-yellow-100 text-yellow-600 dark:bg-yellow-800 dark:text-yellow-300 hover:bg-yellow-200 hover:text-yellow-700 dark:hover:bg-yellow-700 dark:hover:text-yellow-200'
        case 'not_started':
          return 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300 hover:bg-slate-200 hover:text-slate-700 dark:hover:bg-slate-700 dark:hover:text-slate-200'
        default:
          return 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300 hover:bg-slate-200 hover:text-slate-700 dark:hover:bg-slate-700 dark:hover:text-slate-200'
      }
    case 'published':
      return status
        ? 'bg-green-100 text-green-600 dark:bg-green-800 dark:text-green-300 hover:bg-green-200 hover:text-green-700 dark:hover:bg-green-700 dark:hover:text-green-200'
        : 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300 hover:bg-slate-200 hover:text-slate-700 dark:hover:bg-slate-700 dark:hover:text-slate-200'
  }
}
