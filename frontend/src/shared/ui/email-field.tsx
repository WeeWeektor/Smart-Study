import { Input, Label } from './index'
import React from 'react'
import { useI18n } from '@/shared/lib'

interface EmailFieldProps {
  value: string
  onChange: (value: string) => void
  required?: boolean
  disabled?: boolean
  error?: string
}

export const EmailField: React.FC<EmailFieldProps> = ({
  value,
  onChange,
  required = false,
  disabled = false,
  error,
}) => {
  const { t } = useI18n()
  return (
    <div className="space-y-2">
      <Label htmlFor="email" className="text-foreground">
        {t('auth.email')}
      </Label>
      <Input
        id="email"
        type="email"
        placeholder="your.email@example.com"
        value={value}
        onChange={e => onChange(e.target.value)}
        required={required}
        disabled={disabled}
        className="border-border focus:border-brand-500 focus:ring-brand-500"
      />
      {error && <div className="text-destructive text-sm">{error}</div>}
    </div>
  )
}
