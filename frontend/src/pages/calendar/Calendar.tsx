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
import {
  AlertCircle,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  ChevronUp,
  Clock,
} from 'lucide-react'
import {
  Alert,
  AlertDescription,
  Badge,
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  ConfirmModal,
  ErrorProfile,
  LoadingProfile,
  Modal,
} from '@/shared/ui'
import { useUserCoursesStatus } from '@/shared/hooks/useUserCoursesStatus'
import { useI18n } from '@/shared/lib'
import { CourseHeader } from '@/widgets/course'
import { Sidebar } from '@/widgets'
import { useProfileData } from '@/shared/hooks'
import { AddNewEvent, SelectedEvent } from '@/pages/calendar/ui'

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
  const [isModalAddEventOpen, setIsModalAddEventOpen] = useState(false)
  const [newEventData, setNewEventData] = useState({
    title: '',
    description: '',
    date: '',
    importance: '',
    link: '',
  })
  const [personalEvents, setPersonalEvents] = useState<any[]>([])
  const [isConfirmDeleteOpen, setIsConfirmDeleteOpen] = useState(false)
  const [eventIdToDelete, setEventIdToDelete] = useState<string | null>(null)
  const [isEventsExpanded, setIsEventsExpanded] = useState(false)
  const INITIAL_VISIBLE_COUNT = 3

  const getImportanceColor = (importance: string) => {
    switch (importance) {
      case 'high':
        return 'bg-red-500 text-white'
      case 'medium':
        return 'bg-amber-500 text-white'
      case 'low':
        return 'bg-green-500 text-white'
      default:
        return 'bg-brand-500 text-white'
    }
  }

  const getImportanceText = (importance: string) => {
    switch (importance) {
      case 'high':
        return t('Високий')
      case 'medium':
        return t('Середній')
      case 'low':
        return t('Низький')
      default:
        return t('Середній')
    }
  }

  const events = useMemo(() => {
    const courseEvents = rawStats
      ? [
          ...(rawStats.enrolled_list || []),
          ...(rawStats.completed_list || []),
        ].map(item => ({
          id: item.course.id,
          title: item.course.title,
          date: new Date(
            item.course.user_status.is_completed
              ? item.course.user_status.completed_at
              : item.course.user_status.enrolled_at
          ),
          type: item.course.user_status.is_completed ? 'completed' : 'enrolled',
          progress: Math.round(item.course.user_status.progress),
          isPersonal: false,
        }))
      : []

    const personalMapped = personalEvents.map(e => ({
      ...e,
      date: new Date(e.date),
      isPersonal: true,
      type: e.is_completed ? 'completed' : 'enrolled',
      title: e.title,
      description: e.description,
      link: e.link,
      importance: e.importance,
    }))

    return [...courseEvents, ...personalMapped]
  }, [rawStats, personalEvents])

  const days = useMemo(() => {
    const start = startOfWeek(startOfMonth(currentMonth), { weekStartsOn: 1 })
    const end = endOfWeek(endOfMonth(currentMonth), { weekStartsOn: 1 })
    return eachDayOfInterval({ start, end })
  }, [currentMonth])

  const rowsCount = useMemo(() => {
    return days.length / 7
  }, [days])

  const handleEventClick = (eventId: string) => {
    const courseData = [
      ...(rawStats?.enrolled_list || []),
      ...(rawStats?.completed_list || []),
    ].find(item => item.course.id === eventId)

    if (courseData) {
      setActiveEvent(courseData)
      setIsModalOpen(true)
      return
    }

    const personalData = personalEvents.find(e => e.id === eventId)
    if (personalData) {
      setActiveEvent({
        isPersonal: true,
        course: {
          title: personalData.title,
          description: personalData.description,
          id: personalData.id,
          importance: personalData.importance,
          link: personalData.link,
        },
        user_status: {
          progress: 0,
          enrolled_at: personalData.date,
          is_completed: personalData.is_completed,
          date: personalData.date,
        },
      })
      setIsModalOpen(true)
    }
  }

  const handleDateSelect = (day: Date) => {
    setSelectedDate(day)
    setIsEventsExpanded(false)
  }

  const handleSaveNewEvent = (data: any) => {
    // виклик сервісу: await eventService.create(data)
    const newEvent = {
      ...data,
      id: `personal-${Date.now()}`,
      type: 'personal',
      isPersonal: true,
      progress: 0,
    }

    setPersonalEvents(prev => [...prev, newEvent])
    setIsModalAddEventOpen(false)
    // викликати refreshStats або аналогічний метод, якщо дані на бекенді
  }

  const openConfirmDelete = (id: string) => {
    setEventIdToDelete(id)
    setIsModalOpen(false)
    setIsConfirmDeleteOpen(true)
  }

  const handleConfirmDelete = () => {
    if (eventIdToDelete) {
      setPersonalEvents(prev => prev.filter(e => e.id !== eventIdToDelete))
      setIsModalOpen(false)
      setIsConfirmDeleteOpen(false)
      setEventIdToDelete(null)
    }
  }

  const selectedDateEvents = useMemo(() => {
    return events
      .filter(e => isSameDay(e.date, selectedDate))
      .sort((a, b) => a.date.getTime() - b.date.getTime())
  }, [events, selectedDate])

  const handleAddEvent = () => {
    setNewEventData({
      title: newEventData.title,
      description: newEventData.description,
      date: selectedDate.toISOString(),
      importance: newEventData.importance,
      link: newEventData.link,
    })
    setIsModalAddEventOpen(true)
    console.log(newEventData)
  }

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

  const handleToggleCompleteEvent = (eventId: string) => {
    setPersonalEvents(prev =>
      prev.map(event => {
        if (event.id === eventId) {
          const isNowCompleted = !event.is_completed
          return {
            ...event,
            is_completed: isNowCompleted,
            completed_at: isNowCompleted ? new Date().toISOString() : null,
          }
        }
        return event
      })
    )

    setIsModalOpen(false)
    setActiveEvent(null)
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
        {error && (
          <div className="flex flex-col mx-6">
            <Alert className="border-destructive bg-destructive/10 text-destructive mt-6 h-auto">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription className="text-destructive">
                {error}
              </AlertDescription>
            </Alert>
          </div>
        )}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 my-6 px-6">
          <Card className="lg:col-span-8 shadow-md border-border bg-slate-300 dark:bg-slate-700 h-min">
            <CardContent className="p-4 sm:p-6">
              <div className="grid grid-cols-7 gap-px mb-4">
                {['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Нд'].map(d => (
                  <div
                    key={d}
                    className="text-center text-xs font-bold text-muted-foreground py-2 text-black dark:text-white uppercase tracking-widest"
                  >
                    {d}
                  </div>
                ))}
              </div>
              <div
                className="grid grid-cols-7 gap-2 transition-all duration-300 ease-in-out"
                style={{
                  height:
                    rowsCount === 4
                      ? '420px'
                      : rowsCount === 5
                        ? '510px'
                        : '600px',
                }}
              >
                {days.map((day, idx) => {
                  const dayEvents = events.filter(e => isSameDay(e.date, day))
                  const isSelected = isSameDay(day, selectedDate)
                  const isToday = isSameDay(day, new Date())
                  const isCurrentMonth = isSameMonth(day, currentMonth)

                  return (
                    <button
                      key={idx}
                      onClick={() => handleDateSelect(day)}
                      className={`
                      relative w-full min-h-[90px] flex flex-col items-start p-2 rounded-xl border transition-all overflow-hidden dark:hover:border-brand-100
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
                            className={`h-1.5 w-full rounded-full ${
                              e.isPersonal
                                ? getImportanceColor(e.importance)
                                : e.type === 'completed'
                                  ? 'bg-green-500'
                                  : 'bg-brand-500'
                            }`}
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

          <div className="lg:col-span-4 space-y-6 flex flex-col h-full">
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
                  <div className="flex items-end justify-end ring-0 ml-auto">
                    <Button
                      variant="ghost"
                      className="border border-slate-300 dark:border-slate-800 hover:bg-slate-300/50 dark:hover:bg-slate-800/50 gap-1 h-8 bg-slate-100 dark:bg-slate-700"
                      onClick={() => {
                        handleAddEvent()
                      }}
                    >
                      {t('Додати подію')}
                    </Button>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-6 dark:bg-slate-900/30 bg-slate-50/50 rounded-b-xl">
                {selectedDateEvents.length > 0 ? (
                  <div className="space-y-4">
                    {(isEventsExpanded
                      ? selectedDateEvents
                      : selectedDateEvents.slice(0, INITIAL_VISIBLE_COUNT)
                    ).map(event => (
                      <div
                        key={event.id}
                        className={`group p-4 rounded-xl border transition-all cursor-pointer relative overflow-hidden ${
                          event.isPersonal
                            ? 'border-amber-200 bg-amber-50/30 dark:border-amber-900/50 dark:bg-amber-900/10 hover:border-amber-400'
                            : 'border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/30 hover:border-brand-200'
                        } hover:scale-[1.01]`}
                        onClick={() => handleEventClick(event.id)}
                      >
                        {event.isPersonal && (
                          <div
                            className={`absolute left-0 top-0 bottom-0 w-1.5 z-10 ${getImportanceColor(event.importance)}`}
                            title={t(`Приорітет: ${event.importance}`)}
                          />
                        )}
                        <div className="flex justify-between items-start mb-2">
                          <div className="flex flex-wrap gap-2">
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

                            <Badge
                              variant="outline"
                              className="flex items-center gap-1 border-slate-300 dark:border-slate-700"
                            >
                              <Clock className="w-3 h-3" />
                              {format(event.date, 'HH:mm')}
                            </Badge>

                            {event.isPersonal && (
                              <Badge
                                className={`border-none ${getImportanceColor(event.importance)}`}
                              >
                                {t('Приорітет')}:{' '}
                                {getImportanceText(event.importance)}
                              </Badge>
                            )}
                          </div>

                          {!event.isPersonal && (
                            <span className="text-xs font-bold text-brand-600">
                              {event.progress}%
                            </span>
                          )}
                        </div>

                        <h4 className="font-bold text-slate-900 dark:text-slate-100 mb-1 group-hover:text-brand-600 transition-colors">
                          {event.title}
                        </h4>

                        <p className="text-xs text-muted-foreground italic line-clamp-1">
                          {event.isPersonal
                            ? event.description || t('Без опису')
                            : event.type === 'completed'
                              ? t('Курс успішно завершено')
                              : t('Дата початку навчання')}
                        </p>
                      </div>
                    ))}
                    {selectedDateEvents.length > INITIAL_VISIBLE_COUNT && (
                      <Button
                        variant="ghost"
                        className="w-full text-brand-600 hover:text-brand-700 hover:bg-brand-50 dark:hover:bg-brand-900/20 gap-2 text-sm font-semibold transition-colors py-2"
                        onClick={() => setIsEventsExpanded(!isEventsExpanded)}
                      >
                        {isEventsExpanded ? (
                          <>
                            <ChevronUp className="w-4 h-4" />
                            {t('Згорнути')}
                          </>
                        ) : (
                          <>
                            <ChevronDown className="w-4 h-4" />
                            {t('Показати ще')} (
                            {selectedDateEvents.length - INITIAL_VISIBLE_COUNT})
                          </>
                        )}
                      </Button>
                    )}
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
              userStatus={
                activeEvent.course.user_status
                  ? activeEvent.course.user_status
                  : activeEvent.user_status
              }
              isPersonalEvent={activeEvent.isPersonal}
              onDelete={openConfirmDelete}
              onComplete={handleToggleCompleteEvent}
            />
          )}
        </Modal>
        <Modal
          isOpen={isModalAddEventOpen}
          onClose={() => setIsModalAddEventOpen(false)}
          title={t('Створити нову подію')}
        >
          <AddNewEvent
            initialDate={selectedDate.toISOString()}
            onSave={handleSaveNewEvent}
            onCancel={() => setIsModalAddEventOpen(false)}
          />
        </Modal>
        <ConfirmModal
          isOpen={isConfirmDeleteOpen}
          onClose={() => setIsConfirmDeleteOpen(false)}
          onConfirm={handleConfirmDelete}
          title={t('Видалити цю подію?')}
          description={t(
            'Ви впевнені, що хочете видалити цей запис? Цю дію неможливо буде скасувати.'
          )}
          buttonText={t('Видалити')}
        />
      </main>
    </div>
  )
}

export default CalendarPage
