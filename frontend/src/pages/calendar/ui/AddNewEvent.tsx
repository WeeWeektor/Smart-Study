import React, { useState } from 'react'
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
}

export const AddNewEvent = ({
  initialDate,
  onSave,
  onCancel,
}: AddNewEventProps) => {
  const { t } = useI18n()
  const [error, setError] = useState<string | null>(null)

  // TODO localize time format based on user locale
  const currentTime = new Date().toLocaleTimeString('uk-UA', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    date: initialDate,
    time: currentTime,
    importance: 'medium',
    link: '',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!formData.title.trim()) return

    const combinedDate = new Date(formData.date)
    const [hours, minutes] = formData.time.split(':')
    combinedDate.setHours(parseInt(hours), parseInt(minutes))

    onSave({
      ...formData,
      date: combinedDate.toISOString(),
    })
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-5 animate-in fade-in zoom-in-95 duration-200 max-h-[80vh] overflow-y-auto"
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
          value={formData.title}
          onChange={e => setFormData({ ...formData, title: e.target.value })}
          placeholder={t('Наприклад: Підготовка до модульного контролю')}
          required
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
            <div className="flex items-end justify-end w-full absolute rigth-6 pr-3 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400 group-focus-within:text-brand-600 transition-colors">
              <Clock className="w-4 h-4" />
            </div>

            <Input
              id="time"
              type="time"
              value={formData.time}
              onChange={e => setFormData({ ...formData, time: e.target.value })}
              className="block w-full pr-3 h-10 cursor-pointer dark:bg-slate-900/50"
              required
            />
          </div>
        </div>
      </div>

      <div className="space-y-2">
        <Label>{t('Дата')}</Label>
        <div className="flex h-10 items-center rounded-md border border-input px-3 py-2 text-sm text-muted-foreground bg-slate-50 dark:bg-slate-900/50">
          <CalendarIcon className="mr-2 h-4 w-4" />
          {new Date(formData.date).toLocaleDateString()}
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
