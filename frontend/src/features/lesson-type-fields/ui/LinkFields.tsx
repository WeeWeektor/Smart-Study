import React, { useState, useEffect } from 'react'
import { Input, Label } from '@/shared/ui'
import { useI18n } from '@/shared/lib'
import { validateUrl } from '@/features/lesson-type-fields/helper'

type LinkFieldsProps = {
  onChange: (value: string) => void
  onError?: (hasError: boolean) => void
  initialValue?: string
}

export const LinkFields = ({
  onChange,
  onError,
  initialValue = '',
}: LinkFieldsProps) => {
  const { t } = useI18n()
  const [url, setUrl] = useState<string>(initialValue)
  const [errorKey, setErrorKey] = useState<string | null>(null)

  const [isTouched, setIsTouched] = useState(false)

  useEffect(() => {
    const validation = validateUrl(url)

    onError?.(!validation.isValid)

    if (isTouched) {
      setErrorKey(validation.errorKey)
    }
  }, [url, onError, isTouched])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setIsTouched(true)
    const value = e.target.value
    setUrl(value)
    onChange(value)
  }

  const getErrorMessage = (key: string | null) => {
    if (!key) return null
    switch (key) {
      case 'empty':
        return t("Посилання обов'язкове")
      case 'invalid_format':
        return t(
          'Некоректний формат посилання (має починатися з http:// або https://)'
        )
      default:
        return t('Невірне посилання')
    }
  }

  const isLinkValidForRender =
    !errorKey && url.length > 0 && validateUrl(url).isValid

  return (
    <div className="mt-0 space-y-1">
      <Label>{t('Посилання *')}</Label>

      <Input
        type="url"
        placeholder="https://example.com"
        value={url}
        onChange={handleChange}
        onBlur={() => setIsTouched(true)}
        className={`mt-1 ${errorKey ? 'border-red-500 focus:ring-red-500' : ''}`}
      />

      {errorKey && (
        <div className="mt-2 p-2 bg-red-50 text-red-600 text-sm rounded border border-red-100">
          {getErrorMessage(errorKey)}
        </div>
      )}

      {isLinkValidForRender && (
        <div className="mt-3">
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-brand-600 dark:text-brand-400 underline hover:opacity-80 text-sm flex items-center gap-1"
          >
            🔗 {t('Перевірити посилання')}
          </a>
        </div>
      )}
    </div>
  )
}
