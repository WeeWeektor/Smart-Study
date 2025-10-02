import React from 'react'
import { useI18n } from '@/shared/lib'
import { AlertCircle, CheckCircle } from 'lucide-react'

interface DeleteCourseNotificationProps {
  message: string
  status: number
  onClose: () => void
}

const DeleteCourseNotification: React.FC<DeleteCourseNotificationProps> = ({
  message,
  status,
  onClose,
}) => {
  const { t } = useI18n()
  const isSuccess = status === 200

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
            {isSuccess
              ? t('Курс видалено успішно')
              : t('Помилка видалення курсу')}
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

export default DeleteCourseNotification
