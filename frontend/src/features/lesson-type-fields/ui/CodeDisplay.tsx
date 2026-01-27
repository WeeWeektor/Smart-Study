import { useState } from 'react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { Check, Code as CodeIcon, Copy, Terminal } from 'lucide-react'
import { useI18n } from '@/shared/lib'

interface CodeDisplayProps {
  code: string
  language?: string
  className?: string
  showLineNumbers?: boolean
}

export const CodeDisplay = ({
  code,
  language = 'text',
  className,
  showLineNumbers = true,
}: CodeDisplayProps) => {
  const { t } = useI18n()
  const [isCopied, setIsCopied] = useState(false)

  const codeString = typeof code === 'string' ? code.trim() : String(code)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(codeString)
      setIsCopied(true)
      setTimeout(() => setIsCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy code', err)
    }
  }

  return (
    <div
      className={`my-6 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-[#09090b] shadow-sm overflow-hidden ${className}`}
    >
      <div className="flex items-center justify-between px-4 py-2 border-b border-slate-200 dark:border-slate-800 bg-slate-100 dark:bg-[#18181b]">
        <div className="flex items-center gap-2">
          {language === 'bash' || language === 'shell' ? (
            <Terminal className="w-4 h-4 text-slate-500" />
          ) : (
            <CodeIcon className="w-4 h-4 text-slate-500" />
          )}
          <span className="text-xs font-mono font-medium text-slate-600 dark:text-slate-400 uppercase">
            {language}
          </span>
        </div>

        <button
          onClick={handleCopy}
          className="group flex items-center gap-1.5 px-2 py-1 rounded-md transition-all 
                     text-xs font-medium text-slate-500 hover:text-slate-900 hover:bg-slate-200 
                     dark:text-slate-400 dark:hover:text-white dark:hover:bg-white/10"
          title={t('Скопіювати код')}
        >
          {isCopied ? (
            <>
              <Check className="w-3.5 h-3.5 text-green-500" />
              <span className="text-green-500">{t('Скопійовано')}</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5 group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors" />
              <span>{t('Копіювати')}</span>
            </>
          )}
        </button>
      </div>

      <div className="relative text-sm">
        <SyntaxHighlighter
          style={vscDarkPlus}
          language={language.toLowerCase()}
          PreTag="div"
          showLineNumbers={showLineNumbers}
          wrapLines={true}
          lineNumberStyle={{
            minWidth: '2.5em',
            paddingRight: '1em',
            color: '#6e7681',
            textAlign: 'right',
            userSelect: 'none',
          }}
          customStyle={{
            margin: 0,
            padding: '1.5rem',
            backgroundColor: '#1e1e1e',
            fontSize: '0.875rem',
            lineHeight: '1.6',
            fontFamily:
              'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace',
          }}
        >
          {codeString}
        </SyntaxHighlighter>
      </div>
    </div>
  )
}
