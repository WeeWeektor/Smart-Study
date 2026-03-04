import React, { useEffect, useState } from 'react'
import { Input, Label } from '@/shared/ui'
import { useI18n } from '@/shared/lib'
import { validateFile } from '@/features/lesson-type-fields/helper'
import { Music, X } from 'lucide-react'

type AudioFieldsProps = {
  onChange: (data: { file?: File; previewUrl: string } | null) => void
  onError?: (hasError: boolean) => void
  initialUrl?: string
  initialFileName?: string
}

export const AudioFields = ({
  onChange,
  onError,
  initialUrl,
  initialFileName,
}: AudioFieldsProps) => {
  const { t } = useI18n()
  const [file, setFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(
    initialUrl || null
  )
  const [remoteFileName, setRemoteFileName] = useState<string | null>(
    initialFileName || null
  )
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const hasContent = !!file || !!initialUrl
    onError?.(!hasContent)
  }, [file, initialUrl, onError])

  useEffect(() => {
    return () => {
      if (previewUrl && previewUrl.startsWith('blob:')) {
        URL.revokeObjectURL(previewUrl)
      }
    }
  }, [previewUrl])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (!selectedFile) return

    const validation = validateFile({
      file: selectedFile,
      maxSizeMB: 10,
      acceptedTypes: ['audio/*'],
    })

    if (!validation.isValid) {
      setError(t(validation.errorMessage || 'Помилка файлу'))
      setFile(null)
      setPreviewUrl(null)
      setRemoteFileName(null)
      onChange(null)
      e.target.value = ''
      return
    }

    setError(null)
    setFile(selectedFile)
    setRemoteFileName(null)

    const url = URL.createObjectURL(selectedFile)
    setPreviewUrl(url)
    onChange({ file: selectedFile, previewUrl: url })
  }

  const handleRemove = () => {
    setFile(null)
    setPreviewUrl(null)
    setRemoteFileName(null)
    onChange(null)
    setError(null)
    onError?.(true)
  }

  const displayFileName = file ? file.name : remoteFileName || t('Аудіозапис')

  return (
    <div className="mt-0 space-y-2">
      <Label className="text-sm font-medium text-slate-700 dark:text-slate-300">
        {t('Аудіофайл *')}
      </Label>

      {!previewUrl ? (
        <Input
          type="file"
          accept="audio/*"
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
              <Music size={20} />
            </div>
            <div className="flex flex-col min-w-0">
              <span className="text-sm font-semibold text-slate-900 dark:text-slate-100 truncate">
                {displayFileName}
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

      {previewUrl && !error && (
        <div className="mt-4 p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-[#09090b]">
          <audio src={previewUrl} controls className="w-full" />
        </div>
      )}
    </div>
  )
}
