import React, { useEffect, useState } from 'react'
import { Input, Label } from '@/shared/ui'
import { useI18n } from '@/shared/lib'
import { Download, Presentation, X } from 'lucide-react'
import { validateFile } from '@/features/lesson-type-fields/helper'

type PresentationFieldsProps = {
  onChange: (data: { file?: File; previewUrl: string } | null) => void
  onError?: (hasError: boolean) => void
  initialUrl?: string
  initialFileName?: string
}

const VALIDATION_MIME_TYPES = [
  'application/vnd.ms-powerpoint',
  'application/vnd.openxmlformats-officedocument.presentationml.presentation',
  'application/vnd.oasis.opendocument.presentation',
  'application/x-iwork-keynote-sffkey',
]

const INPUT_ACCEPT_ATTRIBUTE =
  '.ppt, .pptx, .odp, .key, application/vnd.ms-powerpoint, application/vnd.openxmlformats-officedocument.presentationml.presentation, application/vnd.oasis.opendocument.presentation'

export const PresentationFields = ({
  onChange,
  onError,
  initialUrl,
  initialFileName,
}: PresentationFieldsProps) => {
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
    if (initialUrl && !file) {
      setPreviewUrl(initialUrl)
      if (initialFileName) {
        setRemoteFileName(initialFileName)
      }
    } else if (!file) {
      setPreviewUrl(null)
      setRemoteFileName(null)
    }
  }, [initialUrl, initialFileName, file])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (!selectedFile) return

    const validation = validateFile({
      file: selectedFile,
      maxSizeMB: 50,
      acceptedTypes: VALIDATION_MIME_TYPES,
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

    if (previewUrl && previewUrl.startsWith('blob:')) {
      URL.revokeObjectURL(previewUrl)
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

  const formatSize = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
  }

  const displayFileName = file ? file.name : remoteFileName || t('Презентація')
  const displayFileSize = file ? formatSize(file.size) : t('Завантажено')

  return (
    <div className="mt-0 space-y-2">
      <Label className="text-sm font-medium text-slate-700 dark:text-slate-300">
        {t('Презентація *')}
      </Label>

      {!previewUrl ? (
        <Input
          type="file"
          accept={INPUT_ACCEPT_ATTRIBUTE}
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
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-brand-50 dark:bg-brand-900/20 text-orange-500 dark:text-orange-400">
              <Presentation size={20} />
            </div>
            <div className="flex flex-col min-w-0">
              <span className="text-sm font-semibold text-slate-900 dark:text-slate-100 truncate">
                {displayFileName}
              </span>
              <span className="text-sm text-green-600 dark:text-green-500 font-medium leading-tight">
                {displayFileSize}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-1">
            {previewUrl && (
              <a
                href={previewUrl}
                download={displayFileName}
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 text-slate-500 hover:text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors flex items-center justify-center"
                title={t('Завантажити або переглянути')}
              >
                <Download size={18} />
              </a>
            )}

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
        </div>
      )}

      {error && (
        <div className="mb-3 mt-3 p-3 bg-red-100 text-red-700 rounded border border-red-200 text-sm">
          {error}
        </div>
      )}
    </div>
  )
}
