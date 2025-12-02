import React, { useEffect, useRef, useState } from 'react'
import { Input, Label } from '@/shared/ui'
import { useI18n } from '@/shared/lib'
import { EyeOff, ZoomInIcon, ZoomOutIcon } from 'lucide-react'

type ImageFieldsProps = {
  onChange: (file: File) => void
}

export const ImageFields = ({ onChange }: ImageFieldsProps) => {
  const { t } = useI18n()
  const [preview, setPreview] = useState<string | null>(null)
  const [isOpen, setIsOpen] = useState(false)

  const [scale, setScale] = useState(1)
  const [position, setPosition] = useState({ x: 0, y: 0 })
  const [isDragging, setIsDragging] = useState(false)
  const dragStartRef = useRef({ x: 0, y: 0 })
  const imageRef = useRef<HTMLImageElement>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const url = URL.createObjectURL(file)
    setPreview(url)
    onChange(file)
  }

  useEffect(() => {
    return () => {
      if (preview) URL.revokeObjectURL(preview)
    }
  }, [preview])

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

  return (
    <div className="mt-0 space-y-1">
      <Label>{t('Зображення *')}</Label>
      <Input
        type="file"
        accept="image/*"
        className="mt-1"
        onChange={handleFileChange}
      />

      {preview && (
        <>
          <div
            className="mt-3 relative border border-gray-200 rounded-lg overflow-hidden h-[200px] w-full bg-gray-50 flex items-center justify-center cursor-pointer hover:bg-gray-100 transition-colors"
            onClick={() => setIsOpen(true)}
          >
            <img
              src={preview}
              alt="Preview"
              className="max-w-full max-h-full object-contain"
            />
            <div className="absolute inset-0 flex items-center justify-center bg-black/0 hover:bg-black/10 transition-colors">
              <span className="bg-black/60 text-white text-xs px-2 py-1 rounded opacity-0 hover:opacity-100 transition-opacity">
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
