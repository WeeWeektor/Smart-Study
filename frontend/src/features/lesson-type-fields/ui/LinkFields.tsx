import React, { useEffect, useState } from 'react'
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
    <div className="mt-0 space-y-2">
      <Label className="text-sm font-medium text-slate-700 dark:text-slate-300">
        {t('Посилання *')}
      </Label>

      <div className="relative">
        <Input
          type="url"
          placeholder="https://example.com"
          value={url}
          onChange={handleChange}
          onBlur={() => setIsTouched(true)}
          className={`mt-1 block w-full text-sm transition-all duration-200
            bg-white dark:bg-[#09090b] 
            border-slate-200 dark:border-slate-800 
            rounded-xl shadow-sm focus:ring-brand-500 focus:border-brand-500
            ${errorKey ? 'border-red-500 focus:ring-red-500' : ''}`}
        />
      </div>

      {errorKey && (
        <div className="mb-3 mt-3 p-3 bg-red-100 text-red-700 rounded border border-red-200 text-sm">
          {getErrorMessage(errorKey)}
        </div>
      )}

      {isLinkValidForRender && (
        <div className="mt-3 px-1 animate-in fade-in duration-300">
          <div className="flex items-center gap-2">
            <span className="text-slate-400">🔗</span>
            <a
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-brand-600 dark:text-brand-400 underline hover:text-brand-700 dark:hover:text-brand-300 text-sm font-medium transition-colors"
            >
              {t('Перевірити посилання')}
            </a>
          </div>
        </div>
      )}
    </div>
  )
}
