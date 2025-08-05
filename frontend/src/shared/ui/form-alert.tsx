import { Alert, AlertDescription } from './index'
import { AlertCircle, CheckCircle } from 'lucide-react'
import React from 'react'

interface FormAlertProps {
  type?: 'error' | 'success' | 'info'
  message: string
}

export const FormAlert: React.FC<FormAlertProps> = ({
  type = 'error',
  message,
}) => {
  let icon = null
  let variant: 'default' | 'destructive' = 'default'
  let descClass = ''

  if (type === 'error') {
    icon = <AlertCircle className="h-4 w-4 text-destructive" />
    variant = 'destructive'
    descClass = 'text-destructive'
  } else if (type === 'success') {
    icon = <CheckCircle className="h-4 w-4 text-success-icon" />
    descClass = 'text-success-text'
  }

  return (
    <Alert variant={variant}>
      {icon}
      <AlertDescription className={descClass}>{message}</AlertDescription>
    </Alert>
  )
}
