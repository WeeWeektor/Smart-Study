import React, { useEffect, useState } from 'react'
import { Input, Label } from '@/shared/ui'
import { useI18n } from '@/shared/lib'
import { validateFile } from '@/features/lesson-type-fields/helper'
import { FileVideo, X } from 'lucide-react'

type VideoFieldsProps = {
  onChange: (data: { file: File; previewUrl: string } | null) => void
  onError?: (hasError: boolean) => void
}

export const VideoFields = ({ onChange, onError }: VideoFieldsProps) => {
  const { t } = useI18n()
  const [preview, setPreview] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [fileName, setFileName] = useState<string | null>(null)

  useEffect(() => {
    if (!preview) {
      onError?.(true)
    }
  }, [preview, onError])

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
      setFileName(null)
      onChange(null)
      e.target.value = ''
      return
    }

    setError(null)
    onError?.(false)

    const url = URL.createObjectURL(file)
    setPreview(url)
    setFileName(file.name)
    onChange({ file: file, previewUrl: url })
  }

  const handleRemove = () => {
    setPreview(null)
    setFileName(null)
    onChange(null)
    onError?.(true)
  }

  return (
    <div className="mt-0 space-y-2">
      <Label className="text-sm font-medium text-slate-700 dark:text-slate-300">
        {t('Відеофайл *')}
      </Label>

      {!preview ? (
        <Input
          type="file"
          accept="video/*"
          className="mt-1 block w-full text-sm text-slate-500 cursor-pointer
            file:mr-4 file:py-2 file:px-4 h-auto
            file:rounded-md file:border-0
            file:text-sm file:font-semibold
            file:bg-brand-50 file:text-brand-700
            hover:file:bg-brand-100
            dark:file:bg-brand-900/20 dark:file:text-brand-400"
          onChange={handleFileChange}
        />
      ) : (
        <div className="flex items-center justify-between p-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-[#09090b] shadow-sm transition-all animate-in fade-in duration-200">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-brand-50 dark:bg-brand-900/20 text-brand-600 dark:text-brand-400">
              <FileVideo size={20} />
            </div>
            <div className="flex flex-col min-w-0">
              <span className="text-sm font-semibold text-slate-900 dark:text-slate-100 truncate">
                {fileName || t('Відеофайл')}
              </span>
              <span className="text-sm text-green-600 dark:text-green-500 font-medium">
                {t('Файл готовий')}
              </span>
            </div>
          </div>

          <button
            type="button"
            onClick={handleRemove}
            className="p-2 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors group"
          >
            <X
              size={18}
              className="text-slate-400 group-hover:text-red-500 transition-colors"
            />
          </button>
        </div>
      )}

      {error && (
        <div className="mb-3 mt-3 p-3 bg-red-100 text-red-700 rounded border border-red-200 text-sm">
          {error}
        </div>
      )}

      {preview && !error && (
        <div className="mt-4 rounded-xl overflow-hidden border border-slate-200 dark:border-slate-800 bg-black shadow-lg">
          <video
            src={preview}
            controls
            className="w-full max-h-[350px] object-contain"
          />
        </div>
      )}
    </div>
  )
}
