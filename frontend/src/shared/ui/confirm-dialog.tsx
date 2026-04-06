import React, { type FC } from 'react'
import { Button } from '@/shared/ui/button.tsx'
import { useI18n } from '@/shared/lib'

interface ConfirmModalProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: () => void
  title?: string
  description?: string
  buttonText?: string
}

export const ConfirmModal: FC<ConfirmModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  description,
  buttonText,
}) => {
  const { t } = useI18n()

  if (!isOpen) return null

  const handleBackgroundClick = () => onClose()
  const handleContentClick = (e: React.MouseEvent) => e.stopPropagation()

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm"
      onClick={handleBackgroundClick}
    >
      <div
        className="bg-white dark:bg-slate-800 rounded-xl w-11/12 max-w-md p-6 shadow-2xl"
        onClick={handleContentClick}
      >
        <h2 className="text-xl font-bold text-center text-slate-900 dark:text-slate-100 mb-4">
          {title}
        </h2>
        <p className="text-center text-slate-700 dark:text-slate-300 mb-6">
          {description}
        </p>

        <div className="flex justify-center gap-4">
          <Button
            className="bg-red-600 dark:bg-red-500 hover:bg-red-700 dark:hover:bg-red-400 text-white"
            onClick={() => {
              onConfirm()
              onClose()
            }}
          >
            {buttonText ? buttonText : t('Видалити')}
          </Button>
          <Button variant="outline" onClick={onClose}>
            {t('Скасувати')}
          </Button>
        </div>
      </div>
    </div>
  )
}
