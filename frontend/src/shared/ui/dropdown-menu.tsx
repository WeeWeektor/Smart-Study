import React, {
  createContext,
  type ReactNode,
  useContext,
  useEffect,
  useRef,
  useState,
} from 'react'
import { cn } from '../lib/utils'

interface DropdownContextType {
  isOpen: boolean
  setIsOpen: React.Dispatch<React.SetStateAction<boolean>>
}

const DropdownContext = createContext<DropdownContextType | undefined>(
  undefined
)

const useDropdown = () => {
  const context = useContext(DropdownContext)
  if (!context) {
    throw new Error('useDropdown must be used within a DropdownMenu')
  }
  return context
}

export const DropdownMenu = ({
  children,
  className,
}: {
  children: ReactNode
  className?: string
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <DropdownContext.Provider value={{ isOpen, setIsOpen }}>
      <div
        ref={menuRef}
        className={cn('relative inline-block text-left', className)}
      >
        {children}
      </div>
    </DropdownContext.Provider>
  )
}

export const DropdownMenuTrigger = ({
  children,
  asChild = false,
  className,
}: {
  children: ReactNode
  asChild?: boolean
  className?: string
}) => {
  const { isOpen, setIsOpen } = useDropdown()

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    setIsOpen(!isOpen)
  }

  return (
    <div onClick={handleClick} className={cn('cursor-pointer', className)}>
      {children}
    </div>
  )
}

export const DropdownMenuContent = ({
  children,
  className,
  align = 'center',
}: {
  children: ReactNode
  className?: string
  align?: 'left' | 'right' | 'center'
}) => {
  const { isOpen } = useDropdown()

  if (!isOpen) return null

  const alignmentClasses = {
    left: 'left-0',
    right: 'right-0',
    center: 'left-1/2 -translate-x-1/2',
  }

  return (
    <div
      className={cn(
        'absolute top-full mt-2 min-w-[200px] z-50',
        'rounded-md border border-slate-200 bg-white p-1 shadow-lg shadow-slate-200/50',
        'dark:border-slate-800 dark:bg-slate-900 dark:shadow-slate-950/50',
        'animate-in fade-in zoom-in-95 duration-200',
        alignmentClasses[align],
        className
      )}
    >
      {children}
    </div>
  )
}

interface DropdownMenuItemProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode
  className?: string
  inset?: boolean
}

export const DropdownMenuItem = ({
  children,
  className,
  inset,
  onClick,
  ...props
}: DropdownMenuItemProps) => {
  const { setIsOpen } = useDropdown()

  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (onClick) onClick(e)
    setIsOpen(false)
  }

  return (
    <button
      onClick={handleClick}
      className={cn(
        'relative flex w-full cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors',
        'hover:bg-slate-100 hover:text-slate-900 focus:bg-slate-100 focus:text-slate-900',
        'dark:hover:bg-slate-800 dark:hover:text-slate-50 dark:focus:bg-slate-800 dark:focus:text-slate-50',
        inset && 'pl-8',
        className
      )}
      {...props}
    >
      {children}
    </button>
  )
}

export const DropdownMenuSeparator = ({
  className,
}: {
  className?: string
}) => (
  <div
    className={cn('-mx-1 my-1 h-px bg-slate-100 dark:bg-slate-800', className)}
  />
)

export const DropdownMenuLabel = ({
  children,
  className,
}: {
  children: ReactNode
  className?: string
}) => (
  <div
    className={cn(
      'px-2 py-1.5 text-sm font-semibold text-slate-900 dark:text-slate-300',
      className
    )}
  >
    {children}
  </div>
)
