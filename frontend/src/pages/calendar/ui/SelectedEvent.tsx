import { useMemo, useState } from 'react'
import { useI18n } from '@/shared/lib'
import { Badge, Button, CollapsibleSection, Progress } from '@/shared/ui'
import {
  BookOpen,
  CalendarDays,
  CircleCheckIcon,
  Clock,
  ExternalLink,
  GraduationCap,
  Trash2,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import {
  getImportanceColor,
  getImportanceColorBackground,
  getImportanceColorText,
} from '../lib/utils'

interface SelectedEventProps {
  course: any
  userStatus: any
  isPersonalEvent?: boolean
  onDelete?: (id: string) => void
  onComplete?: (id: string) => void
}

export const SelectedEvent = ({
  course,
  userStatus,
  isPersonalEvent,
  onDelete,
  onComplete,
}: SelectedEventProps) => {
  const { t } = useI18n()
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)

  const isFutureEvent = useMemo(() => {
    const eventDate = new Date(
      isPersonalEvent ? userStatus.date : userStatus.enrolled_at
    )
    return eventDate > new Date()
  }, [isPersonalEvent, userStatus])

  return (
    <div
      className="space-y-6 max-h-[80vh] overflow-y-auto backdrop-blur-sm
                 dark:scrollbar-slate-800
                 scrollbar-thin
                 scrollbar-track-transparent
                 scrollbar-thumb-gray-300
                 dark:scrollbar-thumb-slate-700
                 hover:scrollbar-thumb-gray-400
                 dark:hover:scrollbar-thumb-slate-500
                 scrollbar-thumb-rounded-full
                 transition-colors"
    >
      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md text-sm font-medium border border-red-200">
          {error}
        </div>
      )}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div
            className={`p-2 rounded-lg ${isPersonalEvent ? getImportanceColorBackground(course.importance, 2) : 'bg-brand-100 dark:bg-brand-900/30'}`}
          >
            {isPersonalEvent ? (
              <CalendarDays
                className={`w-6 h-6 ${getImportanceColorText(course.importance)}`}
              />
            ) : (
              <GraduationCap className="w-6 h-6 text-brand-600" />
            )}
          </div>
          <div>
            <p className="text-sm text-muted-foreground">
              {isPersonalEvent ? t('Особиста подія') : t('Поточний прогрес')}
            </p>
            {!isPersonalEvent && (
              <p className="text-lg font-bold">
                {Math.round(userStatus.progress)}%
              </p>
            )}
          </div>
        </div>

        <Badge
          variant={userStatus.is_completed ? 'default' : 'secondary'}
          className={
            userStatus.is_completed
              ? 'bg-green-600'
              : `${getImportanceColor(course.importance)}`
          }
        >
          {isPersonalEvent
            ? t(course.importance || 'medium')
            : userStatus.is_completed
              ? t('Завершено')
              : t('В процесі')}
        </Badge>
      </div>

      {!isPersonalEvent && (
        <Progress value={userStatus.progress} className="h-2" />
      )}

      <div className="grid grid-cols-2 gap-3">
        <div className="p-3 border rounded-lg bg-slate-50 dark:bg-slate-900/50">
          <p className="text-[10px] uppercase font-bold text-slate-400">
            {isPersonalEvent ? t('Дата події') : t('Дата запису')}
          </p>
          <p className="text-sm font-semibold">
            {new Date(
              isPersonalEvent ? userStatus.date : userStatus.enrolled_at
            ).toLocaleDateString()}
          </p>
        </div>

        {isPersonalEvent ? (
          <div
            className={`p-3 border rounded-lg ${getImportanceColorBackground(course.importance)}`}
          >
            <p
              className={`text-[10px] uppercase font-bold ${getImportanceColorText(course.importance)} mb-1`}
            >
              {t('Час')}
            </p>
            <p className="text-sm font-semibold flex items-center gap-2">
              <Clock
                className={`w - 4 h-4 ${getImportanceColorText(course.importance)}`}
              />
              {new Date(userStatus.date).toLocaleTimeString('uk-UA', {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </p>
          </div>
        ) : (
          <div className="p-3 border rounded-lg bg-slate-50 dark:bg-slate-900/50">
            <p className="text-[10px] uppercase font-bold text-slate-400">
              {t('Уроків')}
            </p>
            <p className="text-sm font-semibold">
              {course.details?.total_lessons || '—'}
            </p>
          </div>
        )}
      </div>

      <CollapsibleSection
        title={isPersonalEvent ? t('Деталі замітки') : t('Про курс')}
      >
        <div className="space-y-4">
          <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
            {course.description || t('Опис відсутній')}
          </p>

          {isPersonalEvent && course.link && (
            <Button
              variant="link"
              className="p-0 h-auto text-brand-600 gap-2"
              onClick={() => window.open(course.link, '_blank')}
            >
              <ExternalLink className="w-4 h-4" />
              {t('Перейти за посиланням')}
            </Button>
          )}
        </div>
      </CollapsibleSection>

      <div className="flex flex-col gap-3 pt-2">
        {!isPersonalEvent ? (
          <Button
            className="w-full bg-brand-600 hover:bg-brand-700 text-white gap-2 h-12 text-base shadow-lg shadow-brand-500/20"
            onClick={() => navigate(`/course-review/${course.id}`)}
          >
            <BookOpen className="w-5 h-5" />
            {t('Перейти до навчання')}
          </Button>
        ) : (
          <>
            {isPersonalEvent && isFutureEvent && (
              <>
                <Button
                  className="w-full text-brand-500 hover:bg-brand-50 bg-brand-700/20 dark:hover:bg-brand-800/20 gap-2 h-12"
                  onClick={() => onComplete?.(course.id)}
                >
                  <CircleCheckIcon className="w-5 h-5" />
                  {t('Завершити подію')}
                </Button>

                <Button
                  variant="ghost"
                  className="w-full text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 gap-2 h-12"
                  onClick={() => onDelete?.(course.id)}
                >
                  <Trash2 className="w-5 h-5" />
                  {t('Видалити подію')}
                </Button>
              </>
            )}
          </>
        )}
      </div>
    </div>
  )
}
