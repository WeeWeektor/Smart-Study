import { useEffect, useMemo, useState } from 'react'
import { useI18n } from '@/shared/lib'
import {
  Button,
  Input,
  Label,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Tabs,
  TabsList,
  TabsTrigger,
} from '@/shared/ui'
import {
  Calendar,
  CalendarIcon,
  ChevronRight,
  Clock,
  Layers,
} from 'lucide-react'
import { normalizeCourseStructure } from '@/shared/lib/course/normalizeStructure.ts'
import { format } from 'date-fns'
import { uk } from 'date-fns/locale'

interface PlaningProps {
  courseId: string
  courseTitle: string
  courseStructure: any | null
  onSave: (events: any[]) => void
  onCancel: () => void
}

export const PlaningCompletionOfTheCourse = ({
  courseId,
  courseTitle,
  courseStructure,
  onSave,
  onCancel,
}: PlaningProps) => {
  const { t } = useI18n()

  const [error, setError] = useState<string | null>(null)
  const [selectedModuleId, setSelectedModuleId] = useState<string>('all')
  const [planMode, setPlanMode] = useState<'once' | 'schedule'>('once')

  const [startDate, setStartDate] = useState(
    new Date().toISOString().split('T')[0]
  )
  const [startTime, setStartTime] = useState('19:00')
  const [selectedDays, setSelectedDays] = useState<number[]>([1, 3, 5])
  const [lessonsPerDay, setLessonsPerDay] = useState(1)

  const [structure, setStructure] = useState<any[]>([])

  const daysOfWeek = [
    { id: 1, label: t('Пн') },
    { id: 2, label: t('Вт') },
    { id: 3, label: t('Ср') },
    { id: 4, label: t('Чт') },
    { id: 5, label: t('Пт') },
    { id: 6, label: t('Сб') },
    { id: 0, label: t('Нд') },
  ]

  useEffect(() => {
    if (courseStructure) {
      const normalized = normalizeCourseStructure(courseStructure)
      setStructure(normalized)
    }
  }, [courseStructure])

  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 15000)
      return () => clearTimeout(timer)
    }
  }, [error])

  const collectItems = (item: any, parentModuleId?: string) => {
    const itemData = {
      id: item.id,
      title: item.title,
      type: item.type,
      moduleId: parentModuleId,
    }

    if (
      item.type === 'lesson' ||
      item.type === 'module-test' ||
      item.type === 'course-test'
    ) {
      return [itemData]
    }

    if (item.children) {
      const currentModuleId = item.type === 'module' ? item.id : parentModuleId
      return item.children.flatMap((child: any) =>
        collectItems(child, currentModuleId)
      )
    }

    return []
  }

  const itemsToSchedule = useMemo(() => {
    if (!structure.length) return []

    if (selectedModuleId === 'all') {
      return structure.flatMap(item => collectItems(item))
    }

    const mod = structure.find(m => m.id === selectedModuleId)
    return mod ? collectItems(mod) : []
  }, [selectedModuleId, structure])

  const totalLessonsCount = itemsToSchedule.length

  const endDatePreview = useMemo(() => {
    if (
      planMode === 'once' ||
      totalLessonsCount === 0 ||
      selectedDays.length === 0
    )
      return null

    let count = 0
    const [year, month, day] = startDate.split('-').map(Number)
    const tempDate = new Date(year, month - 1, day)

    while (count < totalLessonsCount) {
      if (selectedDays.includes(tempDate.getDay())) {
        count += lessonsPerDay
      }
      if (count < totalLessonsCount) {
        tempDate.setDate(tempDate.getDate() + 1)
      }
      if (tempDate.getFullYear() > 2030) break
    }
    return format(tempDate, 'd MMMM yyyy', { locale: uk })
  }, [startDate, selectedDays, lessonsPerDay, totalLessonsCount, planMode])

  const generatePlan = () => {
    const planEvents: any[] = []

    if (itemsToSchedule.length === 0 && planMode === 'schedule') {
      setError(t('Немає елементів для планування'))
      return
    }

    if (planMode === 'once') {
      planEvents.push({
        course: courseId,
        event_date: `${startDate}T${startTime}:00`,
        note: `${t('Дедлайн')}: ${courseTitle}`,
        type: 'course_event',
        link: `${window.location.origin}/course/${courseId}`,
      })
    } else {
      let currentIdx = 0
      const [year, month, day] = startDate.split('-').map(Number)
      const tempDate = new Date(year, month - 1, day)
      const [hours, minutes] = startTime.split(':').map(Number)

      if (selectedDays.length === 0) {
        setError(t('Оберіть хоча б один день тижня'))
        return
      }

      while (currentIdx < itemsToSchedule.length) {
        if (selectedDays.includes(tempDate.getDay())) {
          for (
            let i = 0;
            i < lessonsPerDay && currentIdx < itemsToSchedule.length;
            i++
          ) {
            const item = itemsToSchedule[currentIdx]
            const eventDate = new Date(tempDate)
            eventDate.setHours(hours, minutes, 0, 0)

            const eventBody: any = {
              course: courseId,
              event_date: format(eventDate, "yyyy-MM-dd'T'HH:mm:ss"),
              note: `${item.type === 'lesson' ? t('Урок') : t('Тест')}: ${item.title}`,
              type: 'course_event',
              link: `${window.location.origin}/course/${courseId}`,
            }

            if (item.moduleId) eventBody.module_id = item.moduleId

            if (item.type === 'lesson') {
              eventBody.lesson_id = item.id
            } else if (item.type === 'module-test') {
              eventBody.module_test_id = item.id
            } else if (item.type === 'course-test') {
              eventBody.course_test_id = item.id
            }

            planEvents.push(eventBody)
            currentIdx++
          }
        }
        tempDate.setDate(tempDate.getDate() + 1)
        if (planEvents.length > 500) break
      }
    }

    onSave(planEvents)
  }

  return (
    <div
      className="space-y-6 overflow-y-auto max-h-[80vh] p-2 backdrop-blur-sm overflow-x-hidden
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
      <section className="space-y-3">
        <Label className="text-brand-600 font-bold flex items-center gap-2">
          <Layers className="w-4 h-4" /> {t('Обсяг навчання')}
        </Label>
        <Select value={selectedModuleId} onValueChange={setSelectedModuleId}>
          <SelectTrigger className="h-12">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">{t('Весь курс повністю')}</SelectItem>
            {structure
              .filter(i => i.type === 'module')
              .map(m => (
                <SelectItem key={m.id} value={m.id}>
                  <span className="block truncate max-w-[250px] sm:max-w-[350px]">
                    {t('Модуль')}: {m.title}
                  </span>
                </SelectItem>
              ))}
          </SelectContent>
        </Select>
      </section>

      <section className="space-y-4">
        <Label className="text-brand-600 font-bold flex items-center gap-2">
          <Calendar className="w-4 h-4" /> {t('Режим календаря')}
        </Label>
        <Tabs value={planMode} onValueChange={(v: any) => setPlanMode(v)}>
          <TabsList className="grid grid-cols-2 w-full">
            <TabsTrigger value="once">{t('Один дедлайн')}</TabsTrigger>
            <TabsTrigger value="schedule">{t('Розподілити уроки')}</TabsTrigger>
          </TabsList>
        </Tabs>

        {planMode === 'schedule' ? (
          <div className="p-4 border rounded-xl space-y-5 bg-slate-50 dark:bg-slate-900/50 animate-in fade-in duration-300">
            <div className="space-y-3">
              <Label className="text-xs text-muted-foreground uppercase">
                {t('Дні тижня')}
              </Label>
              <div className="flex justify-between gap-1">
                {daysOfWeek.map(day => (
                  <Button
                    key={day.id}
                    type="button"
                    variant={
                      selectedDays.includes(day.id) ? 'default' : 'outline'
                    }
                    className={`flex-1 h-10 p-0 text-xs ${selectedDays.includes(day.id) ? 'bg-brand-600 text-white' : ''}`}
                    onClick={() =>
                      setSelectedDays(prev =>
                        prev.includes(day.id)
                          ? prev.filter(d => d !== day.id)
                          : [...prev, day.id]
                      )
                    }
                  >
                    {day.label}
                  </Button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="text-xs">{t('Початок (дата)')}</Label>
                <div className="relative group">
                  <Input
                    type="date"
                    value={startDate}
                    onChange={e => setStartDate(e.target.value)}
                    className="pr-10 custom-input-icon cursor-pointer"
                  />
                  <div className="flex items-end justify-end w-full absolute rigth-6 pr-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400 group-focus-within:text-brand-600 transition-colors">
                    <CalendarIcon className="w-4 h-4" />
                  </div>
                </div>
              </div>
              <div className="space-y-2">
                <Label className="text-xs">{t('Час занять')}</Label>
                <div className="relative group">
                  <Input
                    type="time"
                    value={startTime}
                    onChange={e => setStartTime(e.target.value)}
                    className="pr-10 custom-input-icon cursor-pointer"
                  />
                  <div className="flex items-end justify-end w-full absolute rigth-6 pr-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400 group-focus-within:text-brand-600 transition-colors">
                    <Clock className="w-4 h-4" />
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <Label className="text-xs">{t('Уроків за один день')}</Label>
              <div className="flex items-center gap-4">
                <Input
                  type="number"
                  min="1"
                  max={totalLessonsCount > 10 ? 10 : totalLessonsCount}
                  value={lessonsPerDay}
                  onChange={e =>
                    setLessonsPerDay(parseInt(e.target.value) || 1)
                  }
                  className="w-20"
                />
                <div className="flex flex-col">
                  <span className="text-sm font-bold">
                    {t('Всього занять')}: {totalLessonsCount}
                  </span>
                  {endDatePreview && (
                    <span className="text-[11px] text-brand-600 font-medium">
                      🏁 {t('Завершення')}: {endDatePreview}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-4 animate-in slide-in-from-left-2">
            <div className="relative group">
              <Input
                type="date"
                value={startDate}
                onChange={e => setStartDate(e.target.value)}
                className="pr-10 custom-input-icon cursor-pointer"
              />
              <div className="flex items-end justify-end w-full absolute rigth-6 pr-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400 group-focus-within:text-brand-600 transition-colors">
                <CalendarIcon className="w-4 h-4" />
              </div>
            </div>
            <div className="relative group">
              <Input
                type="time"
                value={startTime}
                onChange={e => setStartTime(e.target.value)}
                className="pr-10 custom-input-icon cursor-pointer"
              />
              <div className="flex items-end justify-end w-full absolute rigth-6 pr-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400 group-focus-within:text-brand-600 transition-colors">
                <Clock className="w-4 h-4" />
              </div>
            </div>
          </div>
        )}
      </section>

      <div className="flex gap-3 pt-4 border-t">
        <Button variant="ghost" className="flex-1" onClick={onCancel}>
          {t('Скасувати')}
        </Button>
        <Button
          className="flex-1 bg-brand-600 hover:bg-brand-700 text-white gap-2"
          onClick={generatePlan}
          disabled={totalLessonsCount === 0 && planMode === 'schedule'}
        >
          {t('Сформувати графік')} <ChevronRight className="w-4 h-4" />
        </Button>
      </div>
    </div>
  )
}
