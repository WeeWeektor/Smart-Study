import React, { type ReactNode, useEffect } from 'react'

interface DialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  children: ReactNode
}

// Додаємо інтерфейс з опціональним className
interface BaseProps {
  children: ReactNode
  className?: string
}

export const Dialog: React.FC<DialogProps> = ({
  open,
  onOpenChange,
  children,
}) => {
  useEffect(() => {
    if (open) document.body.style.overflow = 'hidden'
    else document.body.style.overflow = 'unset'
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [open])

  if (!open) return null

  return (
    <div className="fixed inset-0 z-[1100] flex items-center justify-center p-4">
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200"
        onClick={() => onOpenChange(false)}
      />
      {children}
    </div>
  )
}

// Тепер ці компоненти знають про className
export const DialogContent: React.FC<BaseProps> = ({
  children,
  className = '',
}) => (
  <div
    className={`relative w-full bg-white dark:bg-slate-900 rounded-2xl shadow-2xl 
                   border border-border animate-in zoom-in-95 duration-200 overflow-hidden ${className}`}
  >
    {children}
  </div>
)

export const DialogHeader: React.FC<BaseProps> = ({
  children,
  className = '',
}) => (
  <div
    className={`p-6 border-b border-border flex flex-col gap-1.5 ${className}`}
  >
    {children}
  </div>
)

export const DialogTitle: React.FC<BaseProps> = ({
  children,
  className = '',
}) => (
  <h2
    className={`text-xl font-bold text-slate-900 dark:text-slate-100 ${className}`}
  >
    {children}
  </h2>
)

export const DialogFooter: React.FC<BaseProps> = ({
  children,
  className = '',
}) => (
  <div
    className={`p-4 bg-slate-50 dark:bg-slate-800/30 border-t border-border flex justify-end gap-3 ${className}`}
  >
    {children}
  </div>
)
