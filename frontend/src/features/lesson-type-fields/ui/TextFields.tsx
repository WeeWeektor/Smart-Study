import React, { useRef, useState } from 'react'
import { Label } from '@/shared/ui'
import { useI18n } from '@/shared/lib'
import {
  Bold,
  Heading1,
  Heading2,
  Italic,
  List,
  ListOrdered,
  Underline,
} from 'lucide-react'

type TextFieldsProps = {
  onChange: (value: string) => void
  initialValue?: string
  label?: string
}

export const TextFields = ({
  onChange,
  initialValue = '',
  label,
}: TextFieldsProps) => {
  const { t } = useI18n()
  const [value, setValue] = useState(initialValue)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newVal = e.target.value
    setValue(newVal)
    onChange(newVal)
  }

  const insertFormat = (prefix: string, suffix: string = '') => {
    const textarea = textareaRef.current
    if (!textarea) return

    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const selectedText = value.substring(start, end)

    const newText =
      value.substring(0, start) +
      prefix +
      selectedText +
      suffix +
      value.substring(end)

    setValue(newText)
    onChange(newText)

    textarea.focus()
    setTimeout(() => {
      textarea.selectionStart = start + prefix.length
      textarea.selectionEnd = start + prefix.length + selectedText.length
    }, 0)
  }

  const insertList = (type: 'ul' | 'ol') => {
    const textarea = textareaRef.current
    if (!textarea) return

    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const selectedText = value.substring(start, end)

    let newTextSnippet = ''

    if (selectedText.length === 0) {
      newTextSnippet = type === 'ul' ? '- ' : '1. '
    } else {
      const lines = selectedText.split('\n')

      newTextSnippet = lines
        .map((line, index) => {
          if (type === 'ul') {
            return line.startsWith('- ') ? line : `- ${line}`
          }
          return `${index + 1}. ${line}`
        })
        .join('\n')
    }

    const newText =
      value.substring(0, start) + newTextSnippet + value.substring(end)

    setValue(newText)
    onChange(newText)

    textarea.focus()
    setTimeout(() => {
      textarea.selectionStart = start
      textarea.selectionEnd = start + newTextSnippet.length
    }, 0)
  }

  return (
    <div className="mt-0 space-y-1">
      <Label>{label || t('Текстовий опис')}</Label>
      <div className="rounded-lg border border-slate-200 dark:border-slate-800 overflow-hidden bg-slate-50 dark:bg-[#09090b] shadow-sm transition-colors duration-200">
        <div className="flex flex-wrap items-center gap-1 px-2 py-2 bg-slate-100 dark:bg-[#18181b] border-b border-slate-200 dark:border-white/10 transition-colors duration-200">
          <div className="flex items-center gap-1 pr-2 border-r border-slate-300 dark:border-white/10 mr-1">
            <ToolbarButton
              onClick={() => insertFormat('**', '**')}
              icon={<Bold />}
              tooltip={t('Жирний (Ctrl+B)')}
            />
            <ToolbarButton
              onClick={() => insertFormat('*', '*')}
              icon={<Italic />}
              tooltip={t('Курсив (Ctrl+I)')}
            />
            <ToolbarButton
              onClick={() => insertFormat('<u>', '</u>')}
              icon={<Underline />}
              tooltip={t('Підкреслений')}
            />
          </div>

          <div className="flex items-center gap-1 pr-2 border-r border-slate-300 dark:border-white/10 mr-1">
            <ToolbarButton
              onClick={() => insertFormat('# ')}
              icon={<Heading1 />}
              tooltip={t('Заголовок H1')}
            />
            <ToolbarButton
              onClick={() => insertFormat('## ')}
              icon={<Heading2 />}
              tooltip={t('Заголовок H2')}
            />
          </div>

          <div className="flex items-center gap-1">
            <ToolbarButton
              onClick={() => insertList('ul')}
              icon={<List />}
              tooltip={t('Маркований список')}
            />
            <ToolbarButton
              onClick={() => insertList('ol')}
              icon={<ListOrdered />}
              tooltip={t('Нумерований список')}
            />
          </div>
        </div>

        <textarea
          ref={textareaRef}
          value={value}
          onChange={handleChange}
          placeholder={t('Введіть текст опису...')}
          className="w-full h-[150px] p-4 text-sm bg-transparent resize-y outline-none border-none focus:ring-0 leading-relaxed
                     text-slate-800 dark:text-slate-200 
                     placeholder-slate-400 dark:placeholder-slate-600
                     scrollbar-thin scrollbar-thumb-slate-300 dark:scrollbar-thumb-slate-700 scrollbar-track-transparent"
        />
      </div>

      <p className="text-xs text-slate-500 mt-1 pl-1">
        {t('* Підтримується Markdown розмітка')}
      </p>
    </div>
  )
}

const ToolbarButton = ({
  onClick,
  icon,
  tooltip,
}: {
  onClick: () => void
  icon: React.ReactNode
  tooltip: string
}) => (
  <button
    type="button"
    onClick={onClick}
    title={tooltip}
    className="p-1.5 rounded-md transition-all
               text-slate-600 hover:text-slate-900 hover:bg-slate-200
               dark:text-slate-400 dark:hover:text-white dark:hover:bg-white/10"
  >
    {icon}
  </button>
)
