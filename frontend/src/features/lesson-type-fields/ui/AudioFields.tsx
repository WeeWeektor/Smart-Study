import React, { useState } from 'react'
import { Input, Label } from '@/shared/ui'
import { useI18n } from '@/shared/lib'

type AudioFieldsProps = {
  onChange: (file: File) => void
}

export const AudioFields = ({ onChange }: AudioFieldsProps) => {
  const { t } = useI18n()
  const [preview, setPreview] = useState<string | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    const url = URL.createObjectURL(file)
    setPreview(url)

    onChange(file)
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

      {preview && (
        <audio src={preview} controls className="w-full rounded-lg mt-3" />
      )}
    </div>
  )
}
