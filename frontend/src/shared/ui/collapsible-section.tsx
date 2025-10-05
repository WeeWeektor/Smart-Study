import { type ReactNode, useState } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'
import { Button } from '@/shared/ui/button.tsx'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card.tsx'

interface CollapsibleSectionProps {
  title: string
  children: ReactNode
  defaultCollapsed?: boolean
}

export function CollapsibleSection({
  title,
  children,
  defaultCollapsed = false,
}: CollapsibleSectionProps) {
  const [isCollapsed, setIsCollapsed] = useState(defaultCollapsed)

  return (
    <Card className="w-full max-w-6xl relative">
      <Button
        variant="ghost"
        size="icon"
        className="absolute top-3 left-3"
        onClick={() => setIsCollapsed(prev => !prev)}
      >
        {isCollapsed ? <ChevronDown /> : <ChevronUp />}
      </Button>

      <CardHeader>
        <CardTitle className="pl-10">{title}</CardTitle>
      </CardHeader>

      {!isCollapsed && (
        <CardContent className="transition-all duration-300 ease-in-out">
          {children}
        </CardContent>
      )}
    </Card>
  )
}
