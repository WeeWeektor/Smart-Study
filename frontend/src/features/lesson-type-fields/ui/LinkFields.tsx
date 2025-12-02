import React, { useState } from 'react'
import { Input, Label } from '@/shared/ui'
import { useI18n } from '@/shared/lib'

type LinkFieldsProps = {
  onChange: (value: string) => void
}

export const LinkFields = ({ onChange }: LinkFieldsProps) => {
  const { t } = useI18n()
  const [url, setUrl] = useState<string>('')

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setUrl(value)

    onChange(value)
  }

  const isValidUrl = (value: string) => {
    try {
      new URL(value)
      return true
    } catch {
      return false
    }
  }

  return (
    <div className="mt-0 space-y-1">
      <Label>{t('Посилання *')}</Label>
      <Input
        type="url"
        placeholder={t('Вставте посилання')}
        value={url}
        onChange={handleChange}
        className="mt-1"
      />

      {url && (
        <div className="mt-3">
          {isValidUrl(url) ? (
            <a
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-brand-600 dark:text-brand-400 underline hover:opacity-80"
            >
              {t('Перейти за посиланням')}
            </a>
          ) : (
            <div className="mb-3 mt-3 p-3 bg-red-100 text-red-700 rounded">
              {t('Некоректне посилання')}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
