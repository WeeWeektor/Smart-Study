import React from 'react'
import { CheckCircle } from 'lucide-react'

interface DeleteAccountSuccessNotificationProps {
  onClose: () => void
}

const DeleteAccountSuccessNotification: React.FC<
  DeleteAccountSuccessNotificationProps
> = ({ onClose }) => {
  return (
    <div className="fixed top-5 right-5 bg-white rounded-lg shadow-lg z-50 max-w-xs w-full animate-slide-in">
      <div className="p-3">
        <div className="flex justify-between items-center mb-2">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-green-500" />
            <span className="font-semibold text-green-700">Успішно</span>
          </div>
          <button
            className="bg-transparent border-none text-xl cursor-pointer px-1 hover:text-gray-600"
            onClick={onClose}
          >
            ×
          </button>
        </div>
        <div className="text-sm text-gray-700">Ваш акаунт успішно видалено</div>
      </div>
    </div>
  )
}

export default DeleteAccountSuccessNotification
