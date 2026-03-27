export type NotificationType =
  | 'event_reminder'
  | 'message_from_course_owner'
  | 'achievement_unlocked' // TODO відправка на бек при отриманні досягнення
  | 'default'

export interface NotificationItemInterface {
  id: string
  notification_type: NotificationType
  title: string
  message: string
  sent_at: string
  is_read: boolean
  is_important: boolean

  source_name: string | null
  internal_url: string | null
  external_url: string | null
  action_text: string
}

// TODO валідація по довжені на фронті
