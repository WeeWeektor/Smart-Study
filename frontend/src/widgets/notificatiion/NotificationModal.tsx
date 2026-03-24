import React, { useEffect } from 'react'
import { Bell, Clock, X } from 'lucide-react'
import { useI18n } from '@/shared/lib'
import { Badge, Button } from '@/shared/ui'

interface NotificationModalProps {
  isOpen: boolean
  onClose: () => void
}

export const NotificationModal: React.FC<NotificationModalProps> = ({
  isOpen,
  onClose,
}) => {
  const { t } = useI18n()

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [isOpen])

  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleEsc)
    return () => window.removeEventListener('keydown', handleEsc)
  }, [onClose])

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
            <Clock className="w-6 h-6 text-brand-600" />
            <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
              {t('Сповіщення')}
            </h2>
          </div>
          <div className="flex items-center ring-0 ml-auto gap-1">
            <Button
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full transition-colors text-muted-foreground hover:text-foreground"
              aria-label={t('Закрити')}
            >
              <X className="w-5 h-5" />
            </Button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto pt-6 dark:bg-slate-900/30 bg-slate-50/50 rounded-b-xl space-y-4 px-6">
          <div className="group p-4 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/30 hover:border-brand-200 cursor-pointer relative overflow-hidden text-black dark:text-white hover:scale-[1.01] transition-all">
            <div className="flex justify-between items-start mb-2">
              <div className="flex flex-wrap gap-2">
                <Badge variant="secondary">{t('В процесі')}</Badge>
                <Badge
                  variant="outline"
                  className="flex items-center gap-1 border-slate-300 dark:border-slate-700"
                >
                  <Clock className="w-3 h-3" />
                  14:30
                </Badge>
              </div>
              <span className="text-xs font-bold text-brand-600">
                <Bell className="w-3 h-3" />
              </span>
            </div>

            <h4 className="font-bold text-slate-900 dark:text-slate-100 mb-1 group-hover:text-brand-600 transition-colors">
              {t('Дедлайн курсу "Python для початківців"')}
            </h4>
            <p className="text-xs text-muted-foreground italic line-clamp-1">
              {t('Залишилося 2 дні до завершення модуля.')}
            </p>
          </div>

          <div className="text-center py-12 flex flex-col items-center justify-center">
            <div className="bg-slate-100 dark:bg-slate-800 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4 text-slate-400">
              <Bell className="w-6 h-6" />
            </div>
            <p className="text-sm text-muted-foreground">
              {t('Поки що немає нових сповіщень')}
            </p>
          </div>
        </div>

        <div className="p-4 border-t border-border bg-slate-50 dark:bg-slate-800/30">
          <Button className="w-full text-brand-600 dark:text-brand-400 font-semibold py-3 px-4 rounded-xl hover:bg-brand-50 dark:hover:bg-brand-900/20 transition-colors bg-white dark:bg-slate-900 border">
            {t('Позначити всі як прочитані')}
          </Button>
        </div>
      </aside>
    </div>
  )
}
