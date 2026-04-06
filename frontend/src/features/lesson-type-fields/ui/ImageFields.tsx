import React, { useEffect, useRef, useState } from 'react'
import { Input, Label } from '@/shared/ui'
import { useI18n } from '@/shared/lib'
import { EyeOff, ImageIcon, X, ZoomInIcon, ZoomOutIcon } from 'lucide-react'
import { validateFile } from '@/features/lesson-type-fields/helper'

type ImageFieldsProps = {
  onChange: (data: { file?: File; previewUrl: string } | null) => void
  onError?: (hasError: boolean) => void
  initialUrl?: string
  initialFileName?: string
}

export const ImageFields = ({
  onChange,
  onError,
  initialUrl,
  initialFileName,
}: ImageFieldsProps) => {
  const { t } = useI18n()
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(initialUrl || null)
  const [error, setError] = useState<string | null>(null)
  const [isOpen, setIsOpen] = useState(false)
  const [fileName, setFileName] = useState<string | null>(
    initialFileName || null
  )

  const [scale, setScale] = useState(1)
  const [position, setPosition] = useState({ x: 0, y: 0 })
  const [isDragging, setIsDragging] = useState(false)
  const dragStartRef = useRef({ x: 0, y: 0 })
  const imageRef = useRef<HTMLImageElement>(null)

  useEffect(() => {
    const hasContent = !!file || !!initialUrl
    onError?.(!hasContent)
  }, [file, initialUrl, onError])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (!selectedFile) return

    const validation = validateFile({
      file: selectedFile,
      maxSizeMB: 10,
      acceptedTypes: ['image/*'],
    })

    if (!validation.isValid) {
      setError(t(validation.errorMessage || 'Помилка файлу'))
      setFile(null)
      setPreview(null)
      setFileName(null)
      onChange(null)
      e.target.value = ''
      return
    }

    if (preview && preview.startsWith('blob:')) {
      URL.revokeObjectURL(preview)
    }

    setError(null)
    setFile(selectedFile)

    const url = URL.createObjectURL(selectedFile)
    setPreview(url)
    setFileName(selectedFile.name)
    onChange({ file: selectedFile, previewUrl: url })
  }

  useEffect(() => {
    if (initialUrl && !file) {
      setPreview(initialUrl)
      if (initialFileName) {
        setFileName(initialFileName)
      }
    } else if (!file) {
      setPreview(null)
      setFileName(null)
    }
  }, [initialUrl, initialFileName, file])

  useEffect(() => {
    if (isOpen) {
      setScale(1)
      setPosition({ x: 0, y: 0 })
    }
  }, [isOpen])

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (isOpen && e.key === 'Escape') setIsOpen(false)
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen])

  const handleWheel = (e: React.WheelEvent) => {
    e.stopPropagation()
    const delta = e.deltaY > 0 ? -0.1 : 0.1
    const newScale = Math.max(0.1, Math.min(scale + delta, 5))
    setScale(newScale)
  }

  const zoomIn = () => setScale(s => Math.min(s + 0.2, 5))
  const zoomOut = () => setScale(s => Math.max(s - 0.2, 0.1))

  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault()
    setIsDragging(true)
    dragStartRef.current = {
      x: e.clientX - position.x,
      y: e.clientY - position.y,
    }
  }

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return
    e.preventDefault()
    const newX = e.clientX - dragStartRef.current.x
    const newY = e.clientY - dragStartRef.current.y
    setPosition({ x: newX, y: newY })
  }

  const handleMouseUp = () => setIsDragging(false)
  const handleMouseLeave = () => setIsDragging(false)

  const handleRemove = () => {
    setFile(null)
    setPreview(null)
    setFileName(null)
    onChange(null)
    setError(null)
    onError?.(true)
  }

  return (
    <div className="mt-0 space-y-2">
      <Label className="text-sm font-medium text-slate-700 dark:text-slate-300">
        {t('Зображення *')}
      </Label>

      {!preview ? (
        <Input
          type="file"
          accept="image/*"
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
              <ImageIcon size={20} />
            </div>
            <div className="flex flex-col min-w-0">
              <span className="text-sm font-semibold text-slate-900 dark:text-slate-100 truncate">
                {fileName || t('Зображення')}
              </span>
              <span className="text-sm text-green-600 dark:text-green-500 font-medium leading-tight">
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
        <>
          <div
            className="mt-4 relative border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden h-[250px] w-full bg-slate-50 dark:bg-[#09090b] flex items-center justify-center cursor-pointer hover:bg-slate-100 dark:hover:bg-white/5 transition-all shadow-md group"
            onClick={() => setIsOpen(true)}
          >
            <img
              src={preview}
              alt="Preview"
              className="max-w-full max-h-full object-contain"
            />
            <div className="absolute inset-0 flex items-center justify-center bg-black/0 group-hover:bg-black/20 transition-colors">
              <span className="bg-black/60 text-white text-xs px-3 py-1.5 rounded-full opacity-0 group-hover:opacity-100 transition-opacity backdrop-blur-sm">
                {t('Натисніть для перегляду')}
              </span>
            </div>
          </div>

          {isOpen && (
            <div
              className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/95 backdrop-blur-sm overflow-hidden"
              onWheel={handleWheel}
            >
              <div className="absolute top-0 left-0 right-0 p-4 flex justify-end items-center gap-4 z-50 pointer-events-none">
                <div className="flex gap-2 bg-black/50 p-1 rounded-lg pointer-events-auto backdrop-blur-md">
                  <button
                    onClick={zoomOut}
                    className="p-2 text-white/80 hover:text-white hover:bg-white/20 rounded transition-all"
                  >
                    <ZoomOutIcon />
                  </button>
                  <span className="text-white/80 text-sm flex items-center w-12 justify-center select-none">
                    {Math.round(scale * 100)}%
                  </span>
                  <button
                    onClick={zoomIn}
                    className="p-2 text-white/80 hover:text-white hover:bg-white/20 rounded transition-all"
                  >
                    <ZoomInIcon />
                  </button>
                </div>

                <button
                  className="pointer-events-auto p-2 rounded-full transition-all duration-200
                             text-white/70 hover:text-white bg-white/10 hover:bg-white/20"
                  onClick={() => setIsOpen(false)}
                >
                  <EyeOff />
                </button>
              </div>

              <div
                className="w-full h-full flex items-center justify-center cursor-grab active:cursor-grabbing"
                onMouseDown={handleMouseDown}
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
                onMouseLeave={handleMouseLeave}
              >
                <img
                  ref={imageRef}
                  src={preview}
                  alt="Full Screen"
                  draggable={false}
                  style={{
                    transform: `translate(${position.x}px, ${position.y}px) scale(${scale})`,
                    transition: isDragging ? 'none' : 'transform 0.1s ease-out',
                  }}
                  className="max-w-none select-none"
                />
              </div>

              <div className="absolute bottom-5 text-white/40 text-sm pointer-events-none select-none">
                {t('Scroll для зуму • Drag для переміщення')}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
