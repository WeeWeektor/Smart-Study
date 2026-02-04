import { Button, ThemeToggle } from '@/shared/ui'
import type { ReactNode } from 'react'
import { Bell } from 'lucide-react'

interface EditableHeaderProps {
  title: string
  description: string
  icon: ReactNode
  actions?: ReactNode
  actionsBackPage?: ReactNode
}

export const EditableHeader = ({
  title,
  description,
  icon,
  actions,
  actionsBackPage,
}: EditableHeaderProps) => {
  return (
    <header className="bg-card border-b border-border text-card-foreground">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center justify-between space-x-4">
            {actionsBackPage}
            <div>
              <h1 className="text-2xl font-semibold flex items-center text-foreground">
                {icon && <span className="mr-2">{icon}</span>}
                {title.length > 60 ? `${title.slice(0, 60)}...` : title}
              </h1>
              <p className="text-muted-foreground">
                {description.length > 100
                  ? `${description.slice(0, 100)}...`
                  : description}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {actions}
            <ThemeToggle variant="secondary" size="default" />
            <Button variant="ghost" size="sm" className="relative">
              <Bell className="w-5 h-5" />
              <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></span>
            </Button>
          </div>
        </div>
      </div>
    </header>
  )
}
