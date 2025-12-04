import React, { useEffect, useState } from 'react'
import { Input, Label } from '@/shared/ui'
import { useI18n } from '@/shared/lib'
import { validateFile } from '@/features/lesson-type-fields/helper'

type AudioFieldsProps = {
  onChange: (data: { file: File; previewUrl: string } | null) => void
  onError?: (hasError: boolean) => void
}

export const AudioFields = ({ onChange, onError }: AudioFieldsProps) => {
  const { t } = useI18n()
  const [preview, setPreview] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    return () => {
      if (preview) URL.revokeObjectURL(preview)
    }
  }, [preview])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]

    const validation = validateFile({
      file,
      maxSizeMB: 10,
      acceptedTypes: ['audio/*'],
    })

    if (!file) {
      return
    }

    if (!validation.isValid) {
      setError(t(validation.errorMessage || 'Помилка файлу'))
      onError?.(true)

      setPreview(null)
      onChange(null)
      e.target.value = ''
      return
    }

    setError(null)
    onError?.(false)

    const url = URL.createObjectURL(file)
    setPreview(url)

    onChange({ file: file, previewUrl: url })
  }

  return (
    <div className="mt-0 space-y-1">
      <Label>{t('Аудіофайл *')}</Label>

      <Input
        type="file"
        accept="audio/*"
        className="mt-1"
        onChange={handleFileChange}
      />

      {preview && !error && (
        <audio src={preview} controls className="w-full rounded-lg mt-3" />
      )}

      {error && (
        <div className="mb-3 mt-3 p-3 bg-red-100 text-red-700 rounded border border-red-200 text-sm">
          {error}
        </div>
      )}
    </div>
  )
}
