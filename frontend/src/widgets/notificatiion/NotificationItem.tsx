import {
  ArrowRight,
  Clock,
  ExternalLink,
  Info,
  MessageSquare,
  Trophy,
} from 'lucide-react'
import { Badge, Button } from '@/shared/ui'
import { useI18n } from '@/shared/lib'
import type { NotificationItemInterface } from '@/widgets/notificatiion/model.ts'

interface NotificationItemProps {
  notification: NotificationItemInterface
  onMarkRead: (id: string) => void
}

export const NotificationItem = ({
  notification,
  onMarkRead,
}: NotificationItemProps) => {
  const { t } = useI18n()

  const config = {
    event_reminder: {
      icon: <Clock className="w-4 h-4" />,
      badge: t('Нагадування'),
      color: 'text-amber-500',
      bgColor: 'bg-amber-500/10',
    },
    message_from_course_owner: {
      icon: <MessageSquare className="w-4 h-4" />,
      badge: t('Викладач'),
      color: 'text-brand-600',
      bgColor: 'bg-brand-600/10',
    },
    achievement_unlocked: {
      icon: <Trophy className="w-4 h-4" />,
      badge: t('Досягнення'),
      color: 'text-emerald-500',
      bgColor: 'bg-emerald-500/10',
    },
    default: {
      icon: <Info className="w-4 h-4" />,
      badge: t('Системне'),
      color: 'text-slate-500',
      bgColor: 'bg-slate-500/10',
    },
  }

  const currentConfig = config[notification.notification_type] || config.default

  const handleItemClick = () => {
    if (!notification.is_read) {
      onMarkRead(notification.id)
    }
  }

  return (
    <div
      onClick={handleItemClick}
      className={`group p-4 rounded-2xl border transition-all relative overflow-hidden cursor-pointer
        ${
          notification.is_read
            ? 'bg-white dark:bg-slate-900/50 border-slate-100 dark:border-slate-800 opacity-80'
            : 'bg-white dark:bg-slate-900 border-brand-100 dark:border-brand-900/30 shadow-sm border-l-4 border-l-brand-600'
        } 
        hover:border-brand-500/50 hover:shadow-md`}
    >
      <div className="flex justify-between items-start mb-2">
        <div className="flex flex-wrap gap-2 items-center">
          <Badge
            variant="secondary"
            className={`${currentConfig.bgColor} ${currentConfig.color} border-none font-medium`}
          >
            {currentConfig.badge}
          </Badge>

          {!notification.is_read && (
            <div className="relative flex h-4 w-4 ml-1">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-4 w-4 bg-brand-600"></span>
            </div>
          )}

          {notification.source_name && (
            <span className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground opacity-70">
              {notification.source_name}
            </span>
          )}
        </div>
        <span className={`${currentConfig.color} opacity-80`}>
          {currentConfig.icon}
        </span>
      </div>

      <div className="mb-3">
        <h4 className="font-bold text-slate-900 dark:text-slate-100 mb-1 group-hover:text-brand-600 transition-colors leading-tight break-words">
          {notification.title}
        </h4>
        <p className="text-sm text-muted-foreground leading-snug whitespace-pre-wrap break-words">
          {notification.message}
        </p>
      </div>

      <div className="flex items-center gap-2 mt-4 pt-3 border-t border-slate-50 dark:border-slate-800/50">
        {notification.internal_url && (
          <Button
            variant="outline"
            size="sm"
            className="h-8 gap-1.5 text-xs font-semibold rounded-lg"
            onClick={e => {
              e.stopPropagation()
              window.location.href = notification.internal_url!
            }}
          >
            {t('Перейти')}
            <ArrowRight className="w-3 h-3" />
          </Button>
        )}

        {notification.external_url && (
          <Button
            variant="secondary"
            size="sm"
            className="h-8 gap-1.5 text-xs font-semibold rounded-lg bg-brand-50 text-brand-700 hover:bg-brand-100 dark:bg-brand-900/20 dark:text-brand-400"
            onClick={e => {
              e.stopPropagation()
              window.open(notification.external_url!, '_blank')
            }}
          >
            <ExternalLink className="w-3 h-3" />
            {notification.action_text || t('Приєднатися')}
          </Button>
        )}

        <span className="ml-auto text-[10px] text-muted-foreground flex items-center gap-1 opacity-60 font-medium">
          <Clock className="w-3 h-3" />
          {new Date(notification.sent_at).toLocaleString('uk-UA', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
          })}
        </span>
      </div>
    </div>
  )
}
