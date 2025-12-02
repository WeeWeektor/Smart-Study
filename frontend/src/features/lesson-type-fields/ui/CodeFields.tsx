import React, { useRef, useState } from 'react'
import { useI18n } from '@/shared/lib'
import { CheckIcon, CopyIcon } from 'lucide-react'

export type CodeData = {
  language: string
  code: string
}

type CodeFieldsProps = {
  onChange: (data: CodeData) => void
  initialLanguage?: string
  initialCode?: string
}

export const CodeFields = ({
  onChange,
  initialLanguage = 'typescript',
  initialCode = '',
}: CodeFieldsProps) => {
  const { t } = useI18n()
  const [error, setError] = useState<string>('')
  const [language, setLanguage] = useState(initialLanguage)
  const [code, setCode] = useState(initialCode)
  const [isCopied, setIsCopied] = useState(false)

  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const updateParent = (newLang: string, newCode: string) => {
    onChange({ language: newLang, code: newCode })
  }

  const handleLanguageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVal = e.target.value
    setLanguage(newVal)
    updateParent(newVal, code)
  }

  const handleCodeChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newVal = e.target.value
    setCode(newVal)
    updateParent(language, newVal)
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Tab') {
      e.preventDefault()

      const textarea = textareaRef.current
      if (!textarea) return

      const { selectionStart, selectionEnd } = textarea
      const spaces = '  '

      const newCode =
        code.substring(0, selectionStart) +
        spaces +
        code.substring(selectionEnd)

      setCode(newCode)
      updateParent(language, newCode)

      setTimeout(() => {
        textarea.selectionStart = selectionStart + spaces.length
        textarea.selectionEnd = selectionStart + spaces.length
      }, 0)
    }
  }

  const handleCopy = async () => {
    if (!code) return
    try {
      await navigator.clipboard.writeText(code)
      setIsCopied(true)
      setTimeout(() => setIsCopied(false), 2000)
    } catch (err) {
      setError(t('Failed to copy: ') + err)
    }
  }

  return (
    <div className="mt-0 space-y-1">
      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">{error}</div>
      )}

      <div className="rounded-lg border border-slate-200 dark:border-slate-800 overflow-hidden bg-slate-50 dark:bg-[#09090b] shadow-sm transition-colors duration-200">
        <div className="flex items-center justify-between px-4 py-2 bg-slate-100 dark:bg-[#18181b] border-b border-slate-200 dark:border-white/10 transition-colors duration-200">
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500 select-none">
              {t('Мова:')}
            </span>
            <input
              type="text"
              value={language}
              onChange={handleLanguageChange}
              className="bg-transparent border-none p-0 text-sm font-medium w-24 focus:ring-0 focus:outline-none 
                         text-slate-700 dark:text-slate-300 
                         placeholder-slate-400 dark:placeholder-slate-600"
              placeholder="bash..."
            />
          </div>

          <button
            onClick={handleCopy}
            type="button"
            className="p-1.5 rounded-md transition-all focus:outline-none
                       text-slate-500 hover:text-slate-900 hover:bg-slate-200
                       dark:text-slate-400 dark:hover:text-white dark:hover:bg-white/10"
            title={t('Скопіювати код')}
          >
            {isCopied ? <CheckIcon /> : <CopyIcon />}
          </button>
        </div>

        <div className="relative group">
          <textarea
            ref={textareaRef}
            value={code}
            onChange={handleCodeChange}
            onKeyDown={handleKeyDown}
            spellCheck={false}
            placeholder={t('Вставте або напишіть код тут...')}
            className="w-full h-[200px] p-4 font-mono text-sm resize-y outline-none border-none focus:ring-0 leading-relaxed scrollbar-thin scrollbar-track-transparent bg-transparent
                       text-slate-800 dark:text-slate-300 
                       placeholder-slate-400 dark:placeholder-slate-700
                       scrollbar-thumb-slate-300 dark:scrollbar-thumb-slate-700"
          />
        </div>
      </div>
    </div>
  )
}
