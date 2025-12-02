import React, { useState } from 'react'
import { Input, Label } from '@/shared/ui'
import { useI18n } from '@/shared/lib'
import { Presentation, X } from 'lucide-react'

type PresentationFieldsProps = {
  onChange: (file: File | null) => void
}

export const PresentationFields = ({ onChange }: PresentationFieldsProps) => {
  const { t } = useI18n()
  const [file, setFile] = useState<File | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (!selectedFile) return

    setFile(selectedFile)
    onChange(selectedFile)
  }

  const handleRemove = () => {
    setFile(null)
    onChange(null)
  }

  const formatSize = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
  }

  return (
    <div className="mt-0 space-y-1">
      <Label>{t('Презентація *')}</Label>

      {!file && (
        <Input
          type="file"
          accept="
            .ppt, .pptx, .odp, .key,
            application/vnd.ms-powerpoint,
            application/vnd.openxmlformats-officedocument.presentationml.presentation,
            application/vnd.oasis.opendocument.presentation
          "
          className="mt-1"
          onChange={handleFileChange}
        />
      )}

      {file && (
        <div className="mt-2 flex items-center justify-between p-3 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-[#09090b] shadow-sm transition-colors">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="p-2 bg-white dark:bg-[#18181b] rounded-md border border-slate-100 dark:border-slate-800 shrink-0 text-orange-500 dark:text-orange-400">
              <Presentation size={20} />
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

          <button
            type="button"
            onClick={handleRemove}
            className="p-2 text-slate-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 dark:hover:text-red-400 rounded-md transition-colors shrink-0"
            title={t('Видалити файл')}
          >
            <X size={18} />
          </button>
        </div>
      )}
    </div>
  )
}
