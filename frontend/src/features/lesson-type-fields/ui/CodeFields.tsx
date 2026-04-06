import React, { useEffect, useRef, useState } from 'react'
import { useI18n } from '@/shared/lib'
import { AlertCircle, CheckIcon, CopyIcon } from 'lucide-react'
import { validateCodeBlock } from '@/features/lesson-type-fields/helper'

export type CodeData = {
  language: string
  code: string
}

type CodeFieldsProps = {
  onChange: (data: CodeData) => void
  onError?: (hasError: boolean) => void
  initialLanguage?: string
  initialCode?: string
}

export const CodeFields = ({
  onChange,
  onError,
  initialLanguage = 'typescript',
  initialCode = '',
}: CodeFieldsProps) => {
  const { t } = useI18n()

  const [language, setLanguage] = useState(initialLanguage)
  const [code, setCode] = useState(initialCode)

  const [isCopied, setIsCopied] = useState(false)
  const [copyError, setCopyError] = useState<string>('')

  const [validationErrorKey, setValidationErrorKey] = useState<string | null>(
    null
  )
  const [isTouched, setIsTouched] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    const result = validateCodeBlock(language, code)

    onError?.(!result.isValid)

    if (isTouched) {
      setValidationErrorKey(result.errorKey)
    } else {
      setValidationErrorKey(null)
    }
  }, [code, language, onError, isTouched])

  const getErrorMessage = (key: string | null) => {
    if (!key) return null
    switch (key) {
      case 'empty_lang':
        return t('Вкажіть мову програмування')
      case 'empty_code':
        return t('Поле коду не може бути порожнім')
      default:
        return t('Помилка валідації')
    }
  }

  const updateParent = (newLang: string, newCode: string) => {
    onChange({ language: newLang, code: newCode })
  }

  const handleLanguageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setIsTouched(true)
    const newVal = e.target.value
    setLanguage(newVal)
    updateParent(newVal, code)
  }

  const handleCodeChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setIsTouched(true)
    const newVal = e.target.value
    setCode(newVal)
    updateParent(language, newVal)
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Tab') {
      e.preventDefault()
      setIsTouched(true)

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
      setCopyError(t('Помилка копіювання: ') + err)
    }
  }

  return (
    <div className="mt-0 space-y-1">
      {copyError && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">
          {copyError}
        </div>
      )}

      <div
        className={`rounded-lg border overflow-hidden bg-slate-50 dark:bg-[#09090b] shadow-sm transition-colors duration-200 
          ${
            validationErrorKey
              ? 'border-red-500 dark:border-red-500'
              : 'border-slate-200 dark:border-slate-800'
          }`}
      >
        <div
          className={`flex items-center justify-between px-4 py-2 border-b transition-colors duration-200
            ${
              validationErrorKey
                ? 'bg-red-50 dark:bg-red-900/10 border-red-200 dark:border-red-800'
                : 'bg-slate-100 dark:bg-[#18181b] border-slate-200 dark:border-white/10'
            }`}
        >
          <div className="flex items-center gap-2">
            <span
              className={`text-xs select-none ${validationErrorKey === 'empty_lang' ? 'text-red-600 font-bold' : 'text-slate-500'}`}
            >
              {t('Мова:')}
            </span>
            <input
              type="text"
              value={language}
              onChange={handleLanguageChange}
              onBlur={() => setIsTouched(true)}
              className={`bg-transparent border-none p-0 text-sm font-medium w-24 focus:ring-0 focus:outline-none 
                         placeholder-slate-400 dark:placeholder-slate-600
                         ${validationErrorKey === 'empty_lang' ? 'text-red-700 dark:text-red-400' : 'text-slate-700 dark:text-slate-300'}`}
              placeholder="bash..."
            />
          </div>

          <div className="flex items-center gap-2">
            {validationErrorKey && (
              <div
                className="text-red-500 flex items-center gap-1"
                title={getErrorMessage(validationErrorKey) || ''}
              >
                <span className="text-xs font-medium hidden sm:inline">
                  {getErrorMessage(validationErrorKey)}
                </span>
                <AlertCircle size={16} />
              </div>
            )}

            <button
              onClick={handleCopy}
              type="button"
              className="p-1.5 rounded-md transition-all focus:outline-none
                         text-slate-500 hover:text-slate-900 hover:bg-slate-200
                         dark:text-slate-400 dark:hover:text-white dark:hover:bg-white/10"
              title={t('Скопіювати код')}
            >
              {isCopied ? <CheckIcon size={16} /> : <CopyIcon size={16} />}
            </button>
          </div>
        </div>

        <div className="relative group">
          <textarea
            ref={textareaRef}
            value={code}
            onChange={handleCodeChange}
            onBlur={() => setIsTouched(true)}
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
