import React, { useEffect, useRef, useState } from 'react'
import { useI18n } from '@/shared/lib'
import {
  Button,
  Input,
  Label,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Textarea,
} from '@/shared/ui'
import {
  Calendar as CalendarIcon,
  Clock,
  Link as LinkIcon,
  Save,
} from 'lucide-react'

interface AddNewEventProps {
  initialDate: string
  onSave: (data: any) => void
  onCancel: () => void
  defaultValues?: any
}

export const AddNewEvent = ({
  initialDate,
  onSave,
  onCancel,
  defaultValues,
}: AddNewEventProps) => {
  const { t } = useI18n()
  const inputRef = useRef<HTMLInputElement>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const timer = setTimeout(() => {
      inputRef.current?.focus()
    }, 100)
    return () => clearTimeout(timer)
  }, [])

  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(''), 15000)
      return () => clearTimeout(timer)
    }
  }, [error])

  // TODO localize time format based on user locale
  const currentTime = new Date().toLocaleTimeString('uk-UA', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })

  const [formData, setFormData] = useState({
    title: defaultValues?.title || '',
    description: defaultValues?.description || '',
    date: initialDate,
    time: defaultValues?.time || currentTime,
    importance: defaultValues?.importance || 'medium',
    link: defaultValues?.link || '',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!formData.title.trim()) {
      setError(t('Назва обов’язкова'))
      return
    }

    try {
      const finalDate = new Date(formData.date)

      const [hours, minutes] = formData.time.split(':').map(Number)

      finalDate.setHours(hours)
      finalDate.setMinutes(minutes)
      finalDate.setSeconds(0)
      finalDate.setMilliseconds(0)

      if (isNaN(finalDate.getTime())) {
        throw new Error('Invalid date')
      }

      const { time, ...dataToSave } = formData

      onSave({
        ...dataToSave,
        date: finalDate.toISOString(),
      })
    } catch (error) {
      setError(
        t('Помилка формування дати') ||
          (error instanceof Error ? error.message : '')
      )
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-5 p-1 animate-in fade-in zoom-in-95 duration-200 max-h-[80vh] overflow-y-auto backdrop-blur-sm
                 dark:scrollbar-slate-800
                 scrollbar-thin
                 scrollbar-track-transparent
                 scrollbar-thumb-gray-300
                 dark:scrollbar-thumb-slate-700
                 hover:scrollbar-thumb-gray-400
                 dark:hover:scrollbar-thumb-slate-500
                 scrollbar-thumb-rounded-full
                 transition-colors"
    >
      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md text-sm font-medium border border-red-200">
          {error}
        </div>
      )}
      <div className="space-y-2">
        <Label htmlFor="title">{t('Назва події')} *</Label>
        <Input
          id="title"
          ref={inputRef}
          value={formData.title}
          onChange={e => setFormData({ ...formData, title: e.target.value })}
          placeholder={t('Наприклад: Підготовка до модульного контролю')}
          required
          autoFocus
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label>{t('Пріоритет')}</Label>
          <Select
            value={formData.importance}
            onValueChange={val => setFormData({ ...formData, importance: val })}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="low">{t('Низький')}</SelectItem>
              <SelectItem value="medium">{t('Середній')}</SelectItem>
              <SelectItem value="high">{t('Високий')}</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="time">{t('Час події')} *</Label>
          <div className="relative group">
            <Input
              id="time"
              type="time"
              value={formData.time}
              onChange={e => setFormData({ ...formData, time: e.target.value })}
              className="block w-full h-10 dark:bg-slate-900/ pr-10 custom-input-icon cursor-pointer"
              required
            />
            <div className="flex items-end justify-end w-full absolute rigth-6 pr-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400 group-focus-within:text-brand-600 transition-colors">
              <Clock className="w-4 h-4" />
            </div>
          </div>
        </div>
      </div>

      <div className="space-y-2">
        <Label>{t('Дата')}</Label>
        <div className="relative group flex h-10 items-center rounded-md border border-input px-3 py-2 text-sm text-muted-foreground bg-slate-50 dark:bg-slate-900/50">
          {new Date(formData.date).toLocaleDateString()}
          <div className="flex items-end justify-end w-full absolute rigth-6 pr-6 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400 group-focus-within:text-brand-600 transition-colors">
            <CalendarIcon className="h-4 w-4" />
          </div>
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="description">{t('Опис')}</Label>
        <Textarea
          id="description"
          value={formData.description}
          onChange={e =>
            setFormData({ ...formData, description: e.target.value })
          }
          placeholder={t('Додайте деталі події...')}
          rows={3}
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="link" className="flex items-center gap-1">
          <LinkIcon className="w-3 h-3" />
          {t('Посилання (якщо є)')}
        </Label>
        <Input
          id="link"
          type="url"
          value={formData.link}
          onChange={e => setFormData({ ...formData, link: e.target.value })}
          placeholder="https://..."
        />
      </div>

      <div className="flex justify-end gap-3 pt-4 border-t">
        <Button variant="ghost" type="button" onClick={onCancel}>
          {t('Скасувати')}
        </Button>
        <Button
          type="submit"
          className="bg-brand-600 hover:bg-brand-700 text-white gap-2"
        >
          <Save className="w-4 h-4" />
          {t('Зберегти подію')}
        </Button>
      </div>
    </form>
  )
}
