import React from 'react'
import { CheckCircle } from 'lucide-react'

interface LogoutSuccessNotificationProps {
  onClose: () => void
}

const LogoutSuccessNotification: React.FC<LogoutSuccessNotificationProps> = ({
  onClose,
}) => {
  return (
    <div className="fixed top-5 right-5 bg-card text-card-foreground rounded-lg shadow-lg z-50 max-w-xs w-full animate-slide-in">
      <div className="p-3">
        <div className="flex justify-between items-center mb-2">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-success-icon" />
            <span className="font-semibold text-success-text">Успішно</span>
          </div>
          <button
            className="bg-transparent border-none text-xl cursor-pointer px-1 text-muted-foreground hover:text-foreground"
            onClick={onClose}
          >
            ×
          </button>
        </div>
        <div className="text-sm text-muted-foreground">
          Ви успішно вийшли з системи
        </div>
      </div>
    </div>
  )
}

export default LogoutSuccessNotification
