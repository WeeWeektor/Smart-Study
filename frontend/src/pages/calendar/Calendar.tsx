import { useMemo, useState } from 'react'
import {
  addMonths,
  eachDayOfInterval,
  endOfMonth,
  endOfWeek,
  format,
  isSameDay,
  isSameMonth,
  startOfMonth,
  startOfWeek,
  subMonths,
} from 'date-fns'
import { uk } from 'date-fns/locale'
import { AlertCircle, ChevronLeft, ChevronRight, Clock } from 'lucide-react'
import {
  Badge,
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  ErrorProfile,
  LoadingProfile,
  Modal,
} from '@/shared/ui'
import { useUserCoursesStatus } from '@/shared/hooks/useUserCoursesStatus'
import { useI18n } from '@/shared/lib'
import { CourseHeader } from '@/widgets/course'
import { Sidebar } from '@/widgets'
import { useProfileData } from '@/shared/hooks'
import { SelectedEvent } from '@/pages/calendar/ui'

const CalendarPage = () => {
  const { t } = useI18n()
  const { rawStats, loading } = useUserCoursesStatus()
  const [currentMonth, setCurrentMonth] = useState(new Date())
  const [selectedDate, setSelectedDate] = useState(new Date())
  const {
    profileData,
    loading: loadingProfile,
    error,
    refreshProfile,
  } = useProfileData()
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [activeEvent, setActiveEvent] = useState<any>(null)

  const events = useMemo(() => {
    if (!rawStats) return []
    const all = [
      ...(rawStats.enrolled_list || []),
      ...(rawStats.completed_list || []),
    ]

    return all.map(item => ({
      id: item.course.id,
      title: item.course.title,
      date: new Date(
        item.course.user_status.is_completed
          ? item.course.user_status.completed_at
          : item.course.user_status.enrolled_at
      ),
      type: item.course.user_status.is_completed ? 'completed' : 'enrolled',
      progress: Math.round(item.course.user_status.progress),
    }))
  }, [rawStats])

  const days = useMemo(() => {
    const start = startOfWeek(startOfMonth(currentMonth), { weekStartsOn: 1 })
    const end = endOfWeek(endOfMonth(currentMonth), { weekStartsOn: 1 })
    return eachDayOfInterval({ start, end })
  }, [currentMonth])

  const handleEventClick = (courseId: string) => {
    const fullData = [
      ...(rawStats?.enrolled_list || []),
      ...(rawStats?.completed_list || []),
    ].find(item => item.course.id === courseId)

    if (fullData) {
      setActiveEvent(fullData)
      setIsModalOpen(true)
    }
  }

  const selectedDateEvents = events.filter(e => isSameDay(e.date, selectedDate))

  if (loadingProfile && loading) {
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
    <div className="p-0 space-b-6 min-h-full bg-background transition-colors duration-300">
      <Sidebar
        userInfo={userInfo}
        isCollapsible={true}
        onCollapseChange={setIsSidebarCollapsed}
      />

      <main
        className={`flex-1 flex flex-col transition-all duration-300 ease-in-out ${isSidebarCollapsed ? 'ml-28' : 'ml-64'}`}
      >
        <CourseHeader
          title={t('Навчальний календар')}
          description={t('Відстежуйте свій прогрес та важливі дати курсу')}
        />

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 my-6 px-6">
          <Card className="lg:col-span-8 shadow-md border-border bg-slate-300 dark:bg-slate-700">
            <CardContent className="p-4 sm:p-6">
              <div className="grid grid-cols-7 gap-px mb-4">
                {['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Нд'].map(d => (
                  <div
                    key={d}
                    className="text-center text-xs font-bold text-muted-foreground py-2 uppercase tracking-widest"
                  >
                    {d}
                  </div>
                ))}
              </div>
              <div className="grid grid-cols-7 gap-2">
                {days.map((day, idx) => {
                  const dayEvents = events.filter(e => isSameDay(e.date, day))
                  const isSelected = isSameDay(day, selectedDate)
                  const isToday = isSameDay(day, new Date())
                  const isCurrentMonth = isSameMonth(day, currentMonth)

                  return (
                    <button
                      key={idx}
                      onClick={() => setSelectedDate(day)}
                      className={`
                      relative min-h-[90px] flex flex-col items-start p-2 rounded-xl border transition-all dark:hover:border-brand-100
                      ${!isCurrentMonth ? 'opacity-30 bg-slate-50/50 dark:bg-slate-900/10' : 'bg-card hover:border-brand-400'}
                      ${isSelected ? 'border-brand-600 ring-2 ring-brand-500/20 z-10' : 'border-slate-100 dark:border-slate-800'}
                      ${isToday ? 'bg-brand-500/10 dark:bg-brand-200/10' : ''}
                    `}
                    >
                      <span
                        className={`text-sm font-bold ${isToday ? 'text-brand-600' : 'text-foreground'}`}
                      >
                        {format(day, 'd')}
                      </span>

                      <div className="mt-auto w-full space-y-1">
                        {dayEvents.slice(0, 2).map((e, i) => (
                          <div
                            key={i}
                            className={`h-1.5 w-full rounded-full ${e.type === 'completed' ? 'bg-green-500' : 'bg-brand-500'}`}
                          />
                        ))}
                        {dayEvents.length > 2 && (
                          <span className="text-[10px] text-muted-foreground font-medium">
                            +{dayEvents.length - 2} {t('події')}
                          </span>
                        )}
                      </div>
                    </button>
                  )
                })}
              </div>
            </CardContent>
          </Card>

          <div className="lg:col-span-4 space-y-6">
            <div className="flex items-center justify-center bg-card border rounded-xl p-1 shadow-sm w-auto">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setCurrentMonth(subMonths(currentMonth, 1))}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <div className="px-4 font-bold min-w-[140px] text-center capitalize">
                {format(currentMonth, 'LLLL yyyy', { locale: uk })}
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setCurrentMonth(addMonths(currentMonth, 1))}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
            <Card className="shadow-md">
              <CardHeader className="border-b pb-4">
                <CardTitle className="text-lg flex items-center gap-2">
                  <Clock className="w-5 h-5 text-brand-600" />
                  {format(selectedDate, 'd MMMM', { locale: uk })}
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-6 dark:bg-slate-900/30 bg-slate-50/50 rounded-b-xl">
                {selectedDateEvents.length > 0 ? (
                  <div className="space-y-4">
                    {selectedDateEvents.map(event => (
                      <div
                        key={event.id}
                        className="group p-4 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/30 hover:border-brand-200 transition-all"
                        onClick={() => handleEventClick(event.id)}
                      >
                        <div className="flex justify-between items-start mb-2">
                          <Badge
                            variant={
                              event.type === 'completed'
                                ? 'default'
                                : 'secondary'
                            }
                            className={
                              event.type === 'completed' ? 'bg-green-600' : ''
                            }
                          >
                            {event.type === 'completed'
                              ? t('Завершено')
                              : t('В процесі')}
                          </Badge>
                          <span className="text-xs font-bold text-brand-600">
                            {event.progress}%
                          </span>
                        </div>
                        <h4 className="font-bold text-slate-900 dark:text-slate-100 mb-1 group-hover:text-brand-600 transition-colors">
                          {event.title}
                        </h4>
                        <p className="text-xs text-muted-foreground italic">
                          {event.type === 'completed'
                            ? t('Курс успішно завершено')
                            : t('Дата початку навчання')}
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <div className="bg-slate-100 dark:bg-slate-800 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 text-slate-400">
                      <AlertCircle className="w-6 h-6" />
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {t('На цей день подій не заплановано')}
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card className="bg-brand-600 text-white shadow-lg overflow-hidden relative">
              <div className="absolute top-[-10%] right-[-10%] w-24 h-24 bg-white/10 rounded-full blur-2xl" />
              <CardContent className="p-6">
                <h4 className="text-sm font-bold uppercase tracking-wider mb-4 opacity-80">
                  {t('Статистика за місяць')}
                </h4>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-white/10 p-3 rounded-lg backdrop-blur-sm">
                    <div className="text-2xl font-bold">
                      {
                        events.filter(e => isSameMonth(e.date, currentMonth))
                          .length
                      }
                    </div>
                    <div className="text-[10px] uppercase font-bold opacity-70">
                      {t('Всього подій')}
                    </div>
                  </div>
                  <div className="bg-white/10 p-3 rounded-lg backdrop-blur-sm">
                    <div className="text-2xl font-bold text-green-300">
                      {
                        events.filter(
                          e =>
                            isSameMonth(e.date, currentMonth) &&
                            e.type === 'completed'
                        ).length
                      }
                    </div>
                    <div className="text-[10px] uppercase font-bold opacity-70">
                      {t('Завершено')}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title={activeEvent?.course.title}
        >
          {activeEvent && (
            <SelectedEvent
              course={activeEvent.course}
              userStatus={activeEvent.course.user_status}
            />
          )}
        </Modal>
      </main>
    </div>
  )
}

export default CalendarPage
