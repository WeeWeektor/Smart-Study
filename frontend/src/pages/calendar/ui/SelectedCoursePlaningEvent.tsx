import { useI18n } from '@/shared/lib'
import { Badge, Button, CollapsibleSection } from '@/shared/ui'
import {
  BookOpen,
  CalendarDays,
  Clock,
  ExternalLink,
  FileText,
  GraduationCap,
  Layers,
  Trash2,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import {
  getImportanceColor,
  getImportanceColorBackground,
  getImportanceColorText,
} from '../lib/utils'

interface SelectedCoursePlaningEventProps {
  event: any
  onDelete?: (id: string) => void
}

export const SelectedCoursePlaningEvent = ({
  event,
  onDelete,
}: SelectedCoursePlaningEventProps) => {
  const { t } = useI18n()
  const navigate = useNavigate()

  const formatDateSafely = (dateStr: string) => {
    const d = new Date(dateStr)
    if (isNaN(d.getTime())) return t('Дата відсутня')
    return d.toLocaleDateString()
  }

  const formatTimeSafely = (dateStr: string) => {
    const d = new Date(dateStr)
    if (isNaN(d.getTime())) return '--:--'
    return d.toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' })
  }

  const getItemIcon = () => {
    if (event.lesson_id) return <BookOpen className="w-5 h-5 text-brand-600" />
    if (event.module_test_id || event.course_test_id)
      return <FileText className="w-5 h-5 text-amber-600" />
    return <GraduationCap className="w-5 h-5 text-brand-600" />
  }

  return (
    <div
      className="space-y-6 max-h-[80vh] overflow-y-auto backdrop-blur-sm overflow-x-hidden
                 dark:scrollbar-slate-800 scrollbar-thin scrollbar-track-transparent
                 dark:scrollbar-thumb-slate-700 transition-colors p-1"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-brand-100 dark:bg-brand-900/30">
            <CalendarDays className="w-6 h-6 text-brand-600" />
          </div>
          <div>
            <p className="text-sm text-muted-foreground">
              {t('План навчання')}
            </p>
            <p className="text-xs font-medium text-brand-600 flex items-center gap-1">
              {getItemIcon()}
              {event.note?.split(':')[0] || t('Урок')}
            </p>
          </div>
        </div>

        <Badge
          className={`dark:text-white text-black ${getImportanceColor(event.importance)}`}
        >
          {t(event.importance || 'medium')}
        </Badge>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="p-3 border rounded-lg bg-slate-50 dark:bg-slate-900/50">
          <p className="text-[10px] uppercase font-bold text-slate-400">
            {t('Заплановано на')}
          </p>
          <p className="text-sm font-semibold">
            {formatDateSafely(event.event_date)}
          </p>
        </div>

        <div
          className={`p-3 border rounded-lg ${getImportanceColorBackground(event.importance)}`}
        >
          <p
            className={`text-[10px] uppercase font-bold ${getImportanceColorText(event.importance)} mb-1`}
          >
            {t('Час')}
          </p>
          <p className="text-sm font-semibold flex items-center gap-2">
            <Clock
              className={`w-4 h-4 ${getImportanceColorText(event.importance)}`}
            />
            {formatTimeSafely(event.event_date)}
          </p>
        </div>
      </div>

      <CollapsibleSection title={t('Деталі плану')}>
        <div className="space-y-4">
          <div className="flex items-start gap-2">
            <Layers className="w-4 h-4 mt-1 text-slate-400" />
            <div>
              <p className="text-xs text-slate-400 uppercase font-bold">
                {t('Об’єкт планування')}
              </p>
              <p className="text-sm text-slate-600 dark:text-slate-300">
                {event.note || t('Запланована подія')}
              </p>
            </div>
          </div>

          {event.link && (
            <Button
              variant="link"
              className="p-0 h-auto text-brand-600 gap-2"
              onClick={() => window.open(event.link, '_blank')}
            >
              <ExternalLink className="w-4 h-4" />
              {t('Відкрити сторінку курсу')}
            </Button>
          )}
        </div>
      </CollapsibleSection>

      <div className="flex flex-col gap-3 pt-2">
        <Button
          className="w-full bg-brand-600 hover:bg-brand-700 text-white gap-2 h-12 text-base shadow-lg shadow-brand-500/20"
          onClick={() => navigate(`/course-review/${event.course.id}`)}
        >
          <BookOpen className="w-5 h-5" />
          {t('Перейти до виконання')}
        </Button>

        <Button
          variant="ghost"
          className="w-full text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 gap-2 h-12"
          onClick={() => onDelete?.(event.id)}
        >
          <Trash2 className="w-5 h-5" />
          {t('Видалити з графіка')}
        </Button>
      </div>
    </div>
  )
}
