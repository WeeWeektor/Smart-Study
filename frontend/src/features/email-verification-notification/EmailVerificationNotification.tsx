import React from 'react'
import { useI18n } from '@/shared/lib'

interface EmailVerificationNotificationProps {
  onClose: () => void
}

const EmailVerificationNotification: React.FC<
  EmailVerificationNotificationProps
> = ({ onClose }) => {
  const { t } = useI18n()
  return (
    <div className="fixed top-5 right-5 bg-card text-card-foreground rounded-lg shadow-lg z-50 max-w-xs w-full animate-slide-in">
      <div className="p-3">
        <div className="flex justify-between items-center mb-2">
          <span className="font-semibold">{t('Повідомлення')}</span>
          <button
            className="bg-transparent border-none text-xl cursor-pointer px-1 text-muted-foreground hover:text-foreground"
            onClick={onClose}
          >
            ×
          </button>
        </div>
        <div className="text-sm text-muted-foreground">
          {t('Підтвердіть свій email')}
        </div>
      </div>
    </div>
  )
}

export default EmailVerificationNotification
