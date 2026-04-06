import * as Dialog from '@radix-ui/react-dialog'
import { X } from 'lucide-react'
import type { ReactNode } from 'react'

interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title?: string
  children: ReactNode
}

export const Modal = ({ isOpen, onClose, title, children }: ModalProps) => (
  <Dialog.Root open={isOpen} onOpenChange={onClose}>
    <Dialog.Portal>
      <Dialog.Overlay className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm animate-in fade-in" />
      <Dialog.Content className="fixed left-[50%] top-[50%] z-50 w-full max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 border bg-background p-6 shadow-lg duration-200 animate-in zoom-in-95 sm:rounded-xl">
        <div className="flex items-center justify-between mb-4">
          <Dialog.Title className="text-xl font-bold">{title}</Dialog.Title>
          <Dialog.Close asChild>
            <button className="rounded-full p-1 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
              <X className="h-5 w-5" />
            </button>
          </Dialog.Close>
        </div>
        {children}
      </Dialog.Content>
    </Dialog.Portal>
  </Dialog.Root>
)
