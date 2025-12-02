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
} from 'lucide-react'

type DocumentFieldsProps = {
  onChange: (file: File | null) => void
}

export const DocumentFields = ({ onChange }: DocumentFieldsProps) => {
  const { t } = useI18n()
  const [file, setFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (!selectedFile) return

    setFile(selectedFile)

    const url = URL.createObjectURL(selectedFile)
    setPreviewUrl(url)

    onChange(selectedFile)
  }

  const handleRemove = () => {
    setFile(null)
    setPreviewUrl(null)
    onChange(null)
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
          accept=".pdf,.doc,.docx,.txt,.xls,.xlsx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
          className="mt-1"
          onChange={handleFileChange}
        />
      )}

      {file && (
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
