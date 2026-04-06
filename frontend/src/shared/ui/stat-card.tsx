import * as React from 'react'
import type { LucideIcon } from 'lucide-react'
import { cn } from '../lib/utils'
import { Card, CardContent } from './card'

interface StatCardProps {
  icon: LucideIcon
  value: string | number
  label: string
  iconClassName?: string
  iconBgClassName?: string
  valueClassName?: string
  labelClassName?: string
  className?: string
}

export const StatCard = React.forwardRef<HTMLDivElement, StatCardProps>(
  (
    {
      icon: Icon,
      value,
      label,
      iconClassName,
      iconBgClassName,
      valueClassName,
      labelClassName,
      className,
    },
    ref
  ) => {
    return (
      <Card ref={ref} className={className}>
        <CardContent className="pt-6">
          <div className="flex items-center">
            <div className={cn('p-2 bg-brand-100 rounded-lg', iconBgClassName)}>
              <Icon className={cn('w-6 h-6 text-brand-600', iconClassName)} />
            </div>
            <div className="ml-4">
              <p className={cn('text-2xl font-semibold ', valueClassName)}>
                {value}
              </p>
              <p className={cn('text-sm text-slate-400', labelClassName)}>
                {label}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }
)

StatCard.displayName = 'StatCard'
