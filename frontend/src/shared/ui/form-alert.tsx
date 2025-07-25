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
  return (
    <Alert
      className={
        type === 'error'
          ? 'border-red-200 bg-red-50'
          : type === 'success'
            ? 'border-green-200 bg-green-50'
            : ''
      }
    >
      {type === 'error' && <AlertCircle className="h-4 w-4 text-red-600" />}
      {type === 'success' && <CheckCircle className="h-4 w-4 text-green-600" />}
      <AlertDescription
        className={
          type === 'error'
            ? 'text-red-700'
            : type === 'success'
              ? 'text-green-700'
              : ''
        }
      >
        {message}
      </AlertDescription>
    </Alert>
  )
}
