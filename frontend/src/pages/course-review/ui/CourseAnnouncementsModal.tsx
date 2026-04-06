import React, { useEffect, useState } from 'react'
import {
  Bell,
  Clock,
  ExternalLink,
  MessageSquare,
  Plus,
  Users,
  X,
} from 'lucide-react'
import { useI18n } from '@/shared/lib'
import { Badge, Button } from '@/shared/ui'
import {
  type CourseAnnouncementInterface,
  notificationApiService,
} from '@/entities/notification/api'

interface Props {
  isOpen: boolean
  onClose: () => void
  courseId: string
  onOpenCreate: () => void
}

export const CourseAnnouncementsModal: React.FC<Props> = ({
  isOpen,
  onClose,
  courseId,
  onOpenCreate,
}) => {
  const { t } = useI18n()
  const [announcements, setAnnouncements] = useState<
    CourseAnnouncementInterface[]
  >([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (isOpen && courseId) {
      setLoading(true)
      notificationApiService
        .getCourseAnnouncements(courseId)
        .then(setAnnouncements)
        .catch(err => console.error(err))
        .finally(() => setLoading(false))
    }
  }, [isOpen, courseId])

  useEffect(() => {
    if (isOpen) document.body.style.overflow = 'hidden'
    else document.body.style.overflow = 'unset'
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [isOpen])

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-[999] flex justify-end">
      <div
        className="absolute inset-0 bg-black/40 backdrop-blur-[2px] transition-opacity duration-300"
        onClick={onClose}
      />

      <aside className="relative w-full max-w-md bg-white dark:bg-slate-900 h-screen shadow-2xl flex flex-col animate-in slide-in-from-right duration-300 border-l border-border">
        <div className="flex items-center justify-between p-6 border-b border-border bg-card">
          <div className="flex items-center gap-3">
            <MessageSquare className="w-6 h-6 text-brand-600" />
            <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
              {t('Історія оголошень')}
            </h2>
          </div>
          <div className="flex items-center ring-0 ml-auto gap-1">
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full transition-colors text-muted-foreground hover:text-foreground"
            >
              <X className="w-5 h-5" />
            </Button>
          </div>
        </div>

        <div
          className="flex-1 overflow-y-auto p-6 dark:bg-slate-900/30 bg-slate-50/50 space-y-4
                 dark:scrollbar-slate-800 scrollbar-thin scrollbar-track-transparent
                 scrollbar-thumb-gray-300 dark:scrollbar-thumb-slate-700
                 hover:scrollbar-thumb-gray-400 dark:hover:scrollbar-thumb-slate-500
                 scrollbar-thumb-rounded-full transition-colors"
        >
          {loading ? (
            <div className="flex flex-col items-center justify-center py-20 opacity-50">
              <div className="w-8 h-8 border-4 border-brand-600 border-t-transparent rounded-full animate-spin mb-4" />
              <p>{t('Завантаження...')}</p>
            </div>
          ) : announcements.length > 0 ? (
            announcements.map((ann, idx) => (
              <div
                key={idx}
                className="group p-4 rounded-2xl border transition-all relative overflow-hidden bg-white dark:bg-slate-900 border-slate-100 dark:border-slate-800 shadow-sm hover:border-brand-500/50 hover:shadow-md"
              >
                <div className="flex justify-between items-start mb-2">
                  <div className="flex flex-wrap gap-2 items-center">
                    <Badge
                      variant="secondary"
                      className="bg-brand-600/10 text-brand-600 border-none font-medium"
                    >
                      {t('Оголошення')}
                    </Badge>
                    <span className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground opacity-70">
                      {t('Ви надіслали')}
                    </span>
                  </div>
                  <span className="text-brand-600 opacity-80">
                    <MessageSquare className="w-4 h-4" />
                  </span>
                </div>

                <div className="mb-3">
                  <h4 className="font-bold text-slate-900 dark:text-slate-100 mb-1 group-hover:text-brand-600 transition-colors leading-tight break-words">
                    {ann.title}
                  </h4>

                  <p className="text-sm text-muted-foreground leading-snug whitespace-pre-wrap break-words">
                    {ann.message}
                  </p>
                </div>

                {ann.personal_link && (
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-7 px-2 gap-1.5 text-[10px] font-bold rounded-lg bg-brand-50/50 text-brand-700 hover:bg-brand-100 dark:bg-brand-900/20 dark:text-brand-400 border border-brand-100/50 dark:border-brand-900/30 transition-all"
                    onClick={e => {
                      e.stopPropagation()
                      window.open(ann.personal_link, '_blank')
                    }}
                  >
                    <ExternalLink className="w-3 h-3" />
                    <span className="truncate max-w-[80px]">
                      {ann.link_text || t('Перейти')}
                    </span>
                  </Button>
                )}

                <div className="flex items-center gap-2 mt-4 pt-3 border-t border-slate-50 dark:border-slate-800/50">
                  <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-brand-50 dark:bg-brand-900/20 text-brand-700 dark:text-brand-400 text-xs font-bold">
                    <Users className="w-3.5 h-3.5" />
                    <span>
                      {ann.recipients_count} {t('отримувачів')}
                    </span>
                  </div>

                  <span className="ml-auto text-[10px] text-muted-foreground flex items-center gap-1 opacity-60 font-medium whitespace-nowrap">
                    <Clock className="w-3 h-3" />
                    {new Date(ann.sent_at)
                      .toLocaleString('uk-UA', {
                        day: '2-digit',
                        month: '2-digit',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })
                      .replace(',', ' •')}
                  </span>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-20 flex flex-col items-center justify-center">
              <div className="bg-slate-100 dark:bg-slate-800 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 text-slate-400 opacity-50">
                <Bell className="w-8 h-8" />
              </div>
              <p className="text-sm text-muted-foreground font-medium">
                {t('Ви ще не надсилали оголошень')}
              </p>
            </div>
          )}
        </div>

        <div className="p-4 border-t border-border bg-slate-50 dark:bg-slate-800/30">
          <Button
            className="w-full bg-brand-600 hover:bg-brand-700 text-white font-semibold py-6 rounded-xl shadow-lg shadow-brand-600/20 transition-all flex items-center justify-center gap-2"
            onClick={onOpenCreate}
          >
            <Plus className="w-5 h-5" />
            {t('Надіслати нове повідомлення')}
          </Button>
        </div>
      </aside>
    </div>
  )
}
