import React from 'react'
import { CheckCircle } from 'lucide-react'
import { useI18n } from '@/shared/lib'

interface DeleteAccountSuccessNotificationProps {
  onClose: () => void
}

const DeleteAccountSuccessNotification: React.FC<
  DeleteAccountSuccessNotificationProps
> = ({ onClose }) => {
  const { t } = useI18n()
  return (
    <div className="fixed top-5 right-5 bg-card text-card-foreground rounded-lg shadow-lg z-50 max-w-xs w-full animate-slide-in">
      <div className="p-3">
        <div className="flex justify-between items-center mb-2">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-success-icon" />
            <span className="font-semibold text-success-text">
              {t('common.success')}
            </span>
          </div>
          <button
            className="bg-transparent border-none text-xl cursor-pointer px-1 text-muted-foreground hover:text-foreground"
            onClick={onClose}
          >
            ×
          </button>
        </div>
        <div className="text-sm text-muted-foreground">
          {t('profile.accountDeleted')}
        </div>
      </div>
    </div>
  )
}

export default DeleteAccountSuccessNotification
