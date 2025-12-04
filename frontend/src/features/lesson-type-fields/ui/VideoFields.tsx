import React, { useEffect, useState } from 'react'
import { Input, Label } from '@/shared/ui'
import { useI18n } from '@/shared/lib'
import { validateFile } from '@/features/lesson-type-fields/helper'

type VideoFieldsProps = {
  onChange: (data: { file: File; previewUrl: string } | null) => void
  onError?: (hasError: boolean) => void
}

export const VideoFields = ({ onChange, onError }: VideoFieldsProps) => {
  const { t } = useI18n()
  const [preview, setPreview] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!preview) {
      onError?.(true)
    }
  }, [])

  useEffect(() => {
    return () => {
      if (preview) URL.revokeObjectURL(preview)
    }
  }, [preview])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]

    const validation = validateFile({
      file,
      maxSizeMB: 300,
      acceptedTypes: ['video/*'],
    })

    if (!file) return

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
      <Label>{t('Відеофайл *')}</Label>

      <Input
        type="file"
        accept="video/*"
        className="mt-1"
        onChange={handleFileChange}
      />

      {error && (
        <div className="mb-3 mt-2 p-3 bg-red-100 text-red-700 rounded border border-red-200 text-sm">
          {error}
        </div>
      )}

      {preview && !error && (
        <video
          src={preview}
          controls
          className="w-full rounded-lg mt-3 max-h-[300px] bg-black"
        />
      )}
    </div>
  )
}
