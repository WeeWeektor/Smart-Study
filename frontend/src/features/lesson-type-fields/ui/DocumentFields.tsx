import React, { useEffect, useState } from 'react'
import { Input, Label } from '@/shared/ui'
import { useI18n } from '@/shared/lib'
import {
  Eye,
  File as FileIcon,
  FileSpreadsheet,
  FileText,
  FileType,
  X,
  Download,
} from 'lucide-react'
import { validateFile } from '@/features/lesson-type-fields/helper'

type DocumentFieldsProps = {
  onChange: (data: { file: File; previewUrl: string } | null) => void
  onError?: (hasError: boolean) => void
}

const ACCEPTED_DOC_TYPES = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'text/plain',
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
]

const INPUT_ACCEPT_ATTRIBUTE =
  '.pdf,.doc,.docx,.txt,.xls,.xlsx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

export const DocumentFields = ({ onChange, onError }: DocumentFieldsProps) => {
  const { t } = useI18n()
  const [file, setFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!file) {
      onError?.(true)
    }
  }, [])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]

    const validation = validateFile({
      file: selectedFile,
      maxSizeMB: 20,
      acceptedTypes: ACCEPTED_DOC_TYPES,
    })

    if (!selectedFile) {
      return
    }

    if (!validation.isValid) {
      setError(t(validation.errorMessage || 'Помилка файлу'))
      onError?.(true)

      setFile(null)
      setPreviewUrl(null)
      onChange(null)

      e.target.value = ''
      return
    }

    setError(null)
    onError?.(false)

    setFile(selectedFile)
    const url = URL.createObjectURL(selectedFile)
    setPreviewUrl(url)

    onChange({ file: selectedFile, previewUrl: url })
  }

  const handleRemove = () => {
    setFile(null)
    setPreviewUrl(null)
    onChange(null)
    setError(null)

    onError?.(true)
  }

  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl)
    }
  }, [previewUrl])

  const handlePreview = () => {
    if (previewUrl) {
      window.open(previewUrl, '_blank')
    }
  }

  const formatSize = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
  }

  const getFileIcon = (type: string) => {
    if (type.includes('pdf')) {
      return <FileType className="text-red-500" />
    }
    if (type.includes('word') || type.includes('document')) {
      return <FileText className="text-blue-500" />
    }
    if (type.includes('sheet') || type.includes('excel')) {
      return <FileSpreadsheet className="text-green-500" />
    }
    return <FileIcon className="text-slate-500" />
  }

  const isViewable =
    file && (file.type === 'application/pdf' || file.type === 'text/plain')

  return (
    <div className="mt-0 space-y-1">
      <Label>{t('Документ *')}</Label>

      {!file && (
        <Input
          type="file"
          accept={INPUT_ACCEPT_ATTRIBUTE}
          className="mt-1"
          onChange={handleFileChange}
        />
      )}

      {error && (
        <div className="mb-3 mt-2 p-3 bg-red-100 text-red-700 rounded border border-red-200 text-sm">
          {error}
        </div>
      )}

      {file && !error && (
        <div className="mt-2 flex items-center justify-between p-3 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-[#09090b] shadow-sm transition-colors">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="p-2 bg-white dark:bg-[#18181b] rounded-md border border-slate-100 dark:border-slate-800 shrink-0">
              {getFileIcon(file.type)}
            </div>

            <div className="min-w-0">
              <p className="text-sm font-medium text-slate-800 dark:text-slate-200 truncate pr-2">
                {file.name}
              </p>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                {formatSize(file.size)} •{' '}
                {file.name.split('.').pop()?.toUpperCase()}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1 shrink-0">
            {isViewable && (
              <button
                type="button"
                onClick={handlePreview}
                className="p-2 text-slate-500 hover:text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 dark:hover:text-blue-400 rounded-md transition-colors"
                title={t('Переглянути файл')}
              >
                <Eye size={18} />
              </button>
            )}

            {previewUrl && (
              <a
                href={previewUrl}
                download={file.name}
                className="p-2 text-slate-500 hover:text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20 dark:hover:text-blue-400 rounded-md transition-colors flex items-center justify-center"
                title={t('Завантажити файл')}
              >
                <Download size={18} />
              </a>
            )}

            <button
              type="button"
              onClick={handleRemove}
              className="p-2 text-slate-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 dark:hover:text-red-400 rounded-md transition-colors"
              title={t('Видалити файл')}
            >
              <X size={18} />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
