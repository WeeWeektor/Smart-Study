import { Input, Label } from './index'
import React, { useState } from 'react'
import { Eye, EyeOff } from 'lucide-react'
import { useI18n } from '@/shared/lib'

interface PasswordFieldProps {
  value: string
  onChange: (value: string) => void
  required?: boolean
  disabled?: boolean
  error?: string
  label?: string
  placeholder?: string
}

export const PasswordField: React.FC<PasswordFieldProps> = ({
  value,
  onChange,
  required = false,
  disabled = false,
  error,
  label = undefined,
  placeholder = undefined,
}) => {
  const [show, setShow] = useState(false)
  const { t } = useI18n()
  return (
    <div className="space-y-2">
      <Label htmlFor="password" className="text-foreground">
        {label ?? t('Пароль')}
      </Label>
      <div className="relative">
        <Input
          id="password"
          type={show ? 'text' : 'password'}
          value={value}
          onChange={e => onChange(e.target.value)}
          required={required}
          disabled={disabled}
          placeholder={placeholder ?? t('Введіть пароль')}
          className="pr-10 border-border focus:border-brand-500 focus:ring-brand-500"
        />
        <button
          type="button"
          aria-label={show ? t('Сховати пароль') : t('Показати пароль')}
          className="absolute inset-y-0 right-0 flex items-center justify-center w-10 h-full bg-transparent border-none outline-none focus:ring-0 focus:outline-none hover:bg-muted transition rounded"
          onClick={() => setShow(s => !s)}
          tabIndex={-1}
        >
          {show ? (
            <EyeOff className="h-5 w-5 text-muted-foreground mx-auto" />
          ) : (
            <Eye className="h-5 w-5 text-muted-foreground mx-auto" />
          )}
        </button>
      </div>
      {error && <div className="text-destructive text-sm">{error}</div>}
    </div>
  )
}
