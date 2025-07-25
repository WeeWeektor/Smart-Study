import { Input, Label } from './index'
import React from 'react'

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
}) => (
  <div className="space-y-2">
    <Label htmlFor="email" className="text-slate-700">
      Email адреса
    </Label>
    <Input
      id="email"
      type="email"
      placeholder="your.email@example.com"
      value={value}
      onChange={e => onChange(e.target.value)}
      required={required}
      disabled={disabled}
      className="border-slate-300 focus:border-brand-500 focus:ring-brand-500"
    />
    {error && <div className="text-red-600 text-sm">{error}</div>}
  </div>
)
