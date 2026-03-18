import { useI18n } from '@/shared/lib'
import { Badge, Button, CollapsibleSection, Progress } from '@/shared/ui'
import { BookOpen, GraduationCap } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

interface SelectedEventProps {
  course: any
  userStatus: any
}

export const SelectedEvent = ({ course, userStatus }: SelectedEventProps) => {
  const { t } = useI18n()
  const navigate = useNavigate()

  return (
    <div className="space-y-6">
      {/* Шапка з прогресом */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-brand-100 dark:bg-brand-900/30 rounded-lg">
            <GraduationCap className="w-6 h-6 text-brand-600" />
          </div>
          <div>
            <p className="text-sm text-muted-foreground">
              {t('Поточний прогрес')}
            </p>
            <p className="text-lg font-bold">
              {Math.round(userStatus.progress)}%
            </p>
          </div>
        </div>
        <Badge
          variant={userStatus.is_completed ? 'default' : 'secondary'}
          className={userStatus.is_completed ? 'bg-green-600' : ''}
        >
          {userStatus.is_completed ? t('Завершено') : t('В процесі')}
        </Badge>
      </div>

      <Progress value={userStatus.progress} className="h-2" />

      {/* Короткі деталі */}
      <div className="grid grid-cols-2 gap-3">
        <div className="p-3 border rounded-lg bg-slate-50 dark:bg-slate-900/50">
          <p className="text-[10px] uppercase font-bold text-slate-400">
            {t('Дата запису')}
          </p>
          <p className="text-sm font-semibold">
            {new Date(userStatus.enrolled_at).toLocaleDateString()}
          </p>
        </div>
        <div className="p-3 border rounded-lg bg-slate-50 dark:bg-slate-900/50">
          <p className="text-[10px] uppercase font-bold text-slate-400">
            {t('Уроків')}
          </p>
          <p className="text-sm font-semibold">
            {course.details?.total_lessons || '—'}
          </p>
        </div>
      </div>

      {/* Опис */}
      <CollapsibleSection title={t('Про курс')}>
        <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
          {course.description || t('Опис відсутній')}
        </p>
      </CollapsibleSection>

      {/* Кнопка переходу */}
      <Button
        className="w-full bg-brand-600 hover:bg-brand-700 text-white gap-2 h-12 text-base shadow-lg shadow-brand-500/20"
        onClick={() => navigate(`/course-review/${course.id}`)}
      >
        <BookOpen className="w-5 h-5" />
        {t('Перейти до навчання')}
      </Button>
    </div>
  )
}
