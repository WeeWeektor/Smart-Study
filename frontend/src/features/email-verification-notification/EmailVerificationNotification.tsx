import React from 'react'

interface EmailVerificationNotificationProps {
  onClose: () => void
}

const EmailVerificationNotification: React.FC<
  EmailVerificationNotificationProps
> = ({ onClose }) => {
  return (
    <div className="fixed top-5 right-5 bg-white rounded-lg shadow-lg z-50 max-w-xs w-full animate-slide-in">
      <div className="p-3">
        <div className="flex justify-between items-center mb-2">
          <span className="font-semibold">Повідомлення</span>
          <button
            className="bg-transparent border-none text-xl cursor-pointer px-1"
            onClick={onClose}
          >
            ×
          </button>
        </div>
        <div className="text-sm">Підтвердіть свій email</div>
      </div>
    </div>
  )
}

export default EmailVerificationNotification
