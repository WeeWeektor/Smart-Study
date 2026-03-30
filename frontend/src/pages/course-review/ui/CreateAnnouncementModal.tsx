import React, { useState } from 'react'
import { useI18n } from '@/shared/lib'
import {
  Button,
  Checkbox,
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  Input,
  Textarea,
} from '@/shared/ui'
import { AlertCircle, AlertTriangle, Send } from 'lucide-react'

interface Props {
  isOpen: boolean
  onClose: () => void
  onSend: (data: any) => Promise<void>
}

export const CreateAnnouncementModal: React.FC<Props> = ({
  isOpen,
  onClose,
  onSend,
}) => {
  const { t } = useI18n()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    message: '',
    personal_link: '',
    link_text: '',
  })
  const [confirmed, setConfirmed] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Константи лімітів з твоїх моделей Django
  const LIMITS = {
    TITLE: 255,
    MESSAGE: 1000,
  }

  // Перевірка валідності перед відправкою
  const isInvalid =
    formData.title.length === 0 ||
    formData.title.length > LIMITS.TITLE ||
    formData.message.length === 0 ||
    formData.message.length > LIMITS.MESSAGE ||
    !confirmed ||
    loading

  const handleSubmit = async () => {
    if (isInvalid) return
    setLoading(true)
    setError(null)

    try {
      const payload = {
        ...formData,
        personal_link: formData.personal_link || '',
        link_text: formData.link_text || '',
      }

      await onSend(payload)

      setFormData({ title: '', message: '', personal_link: '', link_text: '' })
      setConfirmed(false)
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[550px] dark:bg-slate-900 flex flex-col max-h-[90vh]">
        <DialogHeader className="px-6 pt-6">
          <DialogTitle className="flex items-center gap-2">
            <Send className="w-5 h-5 text-brand-600" />
            {t('Надіслати оголошення')}
          </DialogTitle>
        </DialogHeader>

        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-5 dark:scrollbar-slate-800 scrollbar-thin scrollbar-track-transparent scrollbar-thumb-gray-300 dark:scrollbar-thumb-slate-700">
          {error && (
            <div className="p-3 bg-red-100 border border-red-200 text-red-700 rounded-xl text-sm flex items-center gap-2 animate-in fade-in zoom-in-95">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              {error}
            </div>
          )}

          {/* Title Input */}
          <div className="space-y-2">
            <div className="flex justify-between items-center ml-1">
              <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                {t('Заголовок')}
              </label>
              <span
                className={`text-[10px] font-bold ${formData.title.length > LIMITS.TITLE ? 'text-red-500' : 'text-slate-400'}`}
              >
                {formData.title.length} / {LIMITS.TITLE}
              </span>
            </div>
            <Input
              placeholder={t('Наприклад: Важливе оновлення курсу')}
              value={formData.title}
              onChange={e =>
                setFormData(p => ({ ...p, title: e.target.value }))
              }
              className={`rounded-xl transition-colors ${formData.title.length > LIMITS.TITLE ? 'border-red-500 focus:ring-red-500' : ''}`}
            />
          </div>

          {/* Message Textarea */}
          <div className="space-y-2">
            <div className="flex justify-between items-center ml-1">
              <label className="text-sm font-semibold text-slate-700 dark:text-slate-300">
                {t('Повідомлення')}
              </label>
              <span
                className={`text-[10px] font-bold ${formData.message.length > LIMITS.MESSAGE ? 'text-red-500' : 'text-slate-400'}`}
              >
                {formData.message.length} / {LIMITS.MESSAGE}
              </span>
            </div>
            <Textarea
              placeholder={t('Текст оголошення для всіх студентів курсу...')}
              className={`min-h-[140px] rounded-xl resize-none transition-colors ${formData.message.length > LIMITS.MESSAGE ? 'border-red-500 focus:ring-red-500' : ''}`}
              value={formData.message}
              onChange={e =>
                setFormData(p => ({ ...p, message: e.target.value }))
              }
            />
          </div>

          {/* Links Section */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-semibold text-slate-700 dark:text-slate-300 ml-1">
                {t('Посилання')}
              </label>
              <Input
                placeholder="https://..."
                value={formData.personal_link}
                onChange={e =>
                  setFormData(p => ({ ...p, personal_link: e.target.value }))
                }
                className="rounded-xl"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-semibold text-slate-700 dark:text-slate-300 ml-1">
                {t('Текст кнопки')}
              </label>
              <Input
                placeholder={t('Перейти')}
                value={formData.link_text}
                onChange={e =>
                  setFormData(p => ({ ...p, link_text: e.target.value }))
                }
                className="rounded-xl"
              />
            </div>
          </div>

          {/* Confirmation Box */}
          <div
            onClick={() => setConfirmed(!confirmed)}
            className={`p-4 rounded-2xl border transition-all cursor-pointer flex gap-3 mt-2
              ${
                confirmed
                  ? 'bg-brand-50/50 border-brand-200 dark:bg-brand-900/10 dark:border-brand-800'
                  : 'bg-amber-50 dark:bg-amber-900/10 border-amber-200 dark:border-amber-800'
              }`}
          >
            <Checkbox
              id="check"
              checked={confirmed}
              onCheckedChange={v => setConfirmed(!!v)}
              className="mt-0.5"
            />
            <label className="text-[13px] leading-snug cursor-pointer select-none">
              <AlertCircle
                className={`w-3.5 h-3.5 inline mr-1 mb-0.5 ${confirmed ? 'text-brand-600' : 'text-amber-600'}`}
              />
              <span
                className={`font-bold ${confirmed ? 'text-brand-900 dark:text-brand-200' : 'text-amber-900 dark:text-amber-200'}`}
              >
                {t('Підтвердження')}:
              </span>{' '}
              <span
                className={
                  confirmed
                    ? 'text-brand-800 dark:text-brand-300'
                    : 'text-amber-800 dark:text-amber-300'
                }
              >
                {t(
                  'Я перевірив текст. Повідомлення миттєво отримають усі студенти. Редагування неможливе.'
                )}
              </span>
            </label>
          </div>
        </div>

        <DialogFooter className="px-6 pb-6 pt-2">
          <Button variant="ghost" onClick={onClose} className="rounded-xl">
            {t('Скасувати')}
          </Button>
          <Button
            className="bg-brand-600 hover:bg-brand-700 text-white font-bold px-8 rounded-xl shadow-lg shadow-brand-600/20 disabled:opacity-50 disabled:shadow-none transition-all"
            disabled={isInvalid}
            onClick={handleSubmit}
          >
            {loading ? (
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                {t('Надсилання...')}
              </div>
            ) : (
              t('Надіслати зараз')
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
