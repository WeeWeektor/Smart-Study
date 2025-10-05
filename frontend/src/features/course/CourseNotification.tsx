import React from 'react'
import { AlertCircle, CheckCircle } from 'lucide-react'

interface CourseNotificationProps {
  message: string
  status: number
  action_type: string
  onClose: () => void
}

const CourseNotification: React.FC<CourseNotificationProps> = ({
  message,
  status,
  action_type,
  onClose,
}) => {
  const isSuccess = status === 200

  const success_message =
    action_type === 'create'
      ? 'Курс успішно створено'
      : action_type === 'update'
        ? 'Курс успішно оновлено'
        : action_type === 'delete'
          ? 'Курс успішно видалено'
          : 'Операція успішна'
  const error_message =
    action_type === 'create'
      ? 'Помилка при створенні курсу'
      : action_type === 'update'
        ? 'Помилка при оновленні курсу'
        : action_type === 'delete'
          ? 'Помилка при видаленні курсу'
          : 'Сталася помилка'

  return (
    <div className="fixed top-5 right-5 bg-card text-card-foreground rounded-lg shadow-lg z-50 max-w-xs w-full animate-slide-in">
      <div className="p-3">
        <div className="flex justify-between items-center mb-2">
          <div className="flex items-center gap-2 font-semibold">
            {isSuccess ? (
              <CheckCircle className="w-5 h-5 text-green-600" />
            ) : (
              <AlertCircle className="w-5 h-5 text-red-600" />
            )}
            {isSuccess ? success_message : error_message}
          </div>
          <button
            className="bg-transparent border-none text-xl cursor-pointer px-1 text-muted-foreground hover:text-foreground"
            onClick={onClose}
          >
            ×
          </button>
        </div>
        <div className="text-sm text-muted-foreground">{message}</div>
      </div>
    </div>
  )
}

export default CourseNotification
