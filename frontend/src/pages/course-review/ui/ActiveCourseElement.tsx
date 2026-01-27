import React, { type ComponentPropsWithoutRef } from 'react'
import ReactMarkdown, { type Components } from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeRaw from 'rehype-raw'
import { ArrowLeft, ClipboardList, Clock, Code, FileCheck } from 'lucide-react'
import {
  Button,
  Card,
  CardContent,
  CardHeader,
  LoadingProfile,
} from '@/shared/ui'
import { CodeDisplay } from '@/features/lesson-type-fields/ui'
import { useI18n } from '@/shared/lib'
import { type ElementOfCourseResponse } from '@/features/course'
import type { Lesson } from '@/features/course/get.element.of.course.service.ts'

interface ActiveCourseElementProps {
  activeElement: ElementOfCourseResponse | null
  isLoading: boolean
  onBack: () => void
}

type MarkdownProps<T extends React.ElementType> =
  ComponentPropsWithoutRef<T> & {
    node?: object
  }

type CodeProps = MarkdownProps<'code'> & {
  inline?: boolean
}

export const ActiveCourseElement: React.FC<ActiveCourseElementProps> = ({
  activeElement,
  isLoading,
  onBack,
}) => {
  const { t } = useI18n()

  const preprocessMarkdownContent = (rawContent: string) => {
    if (!rawContent) return ''

    let processed = rawContent

    const assignmentRegex =
      /(###\s+(?:Завдання|Assignment|Task):)([\s\S]*?)(?=\n#|$)/gi
    processed = processed.replace(assignmentRegex, (_match, header, body) => {
      return `\n<div class="assignment-wrapper">\n\n${header}\n${body}\n\n</div>\n`
    })

    const commentRegex =
      /(\*\*\*(?:Методичний коментар|Methodical comment|Comment):\*\*\s[\s\S]*?\*)/gi
    processed = processed.replace(commentRegex, match => {
      return `\n<div class="methodical-comment">\n\n${match}\n\n</div>\n`
    })

    return processed
  }

  const markdownComponents: Components = {
    h1: ({ node: _node, ...props }: MarkdownProps<'h1'>) => (
      <h1
        className="text-3xl font-bold mt-8 mb-4 border-b pb-2 border-slate-200 dark:border-slate-800"
        {...props}
      />
    ),
    h2: ({ node: _node, ...props }: MarkdownProps<'h2'>) => (
      <h2 className="text-2xl font-bold mt-6 mb-3" {...props} />
    ),
    h3: ({ node: _node, ...props }: MarkdownProps<'h3'>) => {
      const textContent = String(props.children)
      const isAssignmentHeader = /Завдання|Assignment|Task/i.test(textContent)

      if (isAssignmentHeader) {
        return (
          <h3
            className="flex items-center gap-2 text-orange-800 dark:text-orange-300 mb-4 text-sm font-bold uppercase tracking-wider"
            {...props}
          >
            <ClipboardList className="w-4 h-4" />
            {props.children}
          </h3>
        )
      }
      return (
        <h3
          className="text-xl font-bold mt-6 mb-3 text-slate-900 dark:text-white"
          {...props}
        />
      )
    },

    div: ({
      node: _node,
      className,
      children,
      ...props
    }: MarkdownProps<'div'>) => {
      if (className === 'assignment-wrapper') {
        return (
          <div className="w-full my-8">
            <div className="rounded-xl border border-orange-200 dark:border-orange-900/50 bg-orange-50/50 dark:bg-orange-900/10 overflow-hidden shadow-sm">
              <div className="flex flex-row">
                <div className="w-1.5 self-stretch bg-orange-400 dark:bg-orange-600"></div>

                <div className="p-6 md:p-8 w-full">{children}</div>
              </div>
            </div>
          </div>
        )
      }
      if (className === 'methodical-comment') {
        return (
          <div className="mt-8 pt-6 border-t border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300">
            {children}
          </div>
        )
      }
      return (
        <div className={className} {...props}>
          {children}
        </div>
      )
    },

    video: ({ node: _node, ...props }: MarkdownProps<'video'>) => (
      <div className="my-6 rounded-xl overflow-hidden shadow-lg bg-black border border-slate-800 aspect-video">
        <video
          className="w-full h-full object-contain"
          controls
          preload="metadata"
          {...props}
        >
          {props.children}
        </video>
      </div>
    ),

    img: ({ node: _node, ...props }: MarkdownProps<'img'>) => (
      <img
        className="rounded-lg shadow-md max-w-full h-auto my-6 mx-auto"
        loading="lazy"
        {...props}
      />
    ),

    code: ({
      node: _node,
      inline,
      className,
      children,
      ...props
    }: CodeProps) => {
      const match = /language-(\w+)/.exec(className || '')
      const codeString = String(children).replace(/\n$/, '')
      if (inline || !match) {
        return (
          <code
            className="px-1.5 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-brand-600 dark:text-brand-400 font-mono text-sm border border-slate-200 dark:border-slate-700 font-semibold"
            {...props}
          >
            {children}
          </code>
        )
      }
      return (
        <CodeDisplay
          code={codeString}
          language={match[1]}
          showLineNumbers={true}
        />
      )
    },

    pre: ({ children }: MarkdownProps<'pre'>) => (
      <div className="not-prose">{children}</div>
    ),

    p: ({ node: _node, ...props }: MarkdownProps<'p'>) => (
      <p className="mb-4 leading-7" {...props} />
    ),
    ul: ({ node: _node, ...props }: MarkdownProps<'ul'>) => (
      <ul className="mb-4 ml-6 list-disc space-y-1" {...props} />
    ),
    ol: ({ node: _node, ...props }: MarkdownProps<'ol'>) => (
      <ol className="mb-4 ml-6 list-decimal space-y-1" {...props} />
    ),
    a: ({ node: _node, ...props }: MarkdownProps<'a'>) => (
      <a
        className="text-brand-600 hover:underline font-medium"
        target="_blank"
        rel="noopener noreferrer"
        {...props}
      />
    ),
    blockquote: ({ node: _node, ...props }: MarkdownProps<'blockquote'>) => (
      <blockquote
        className="border-l-4 border-brand-500 pl-4 py-2 my-4 italic bg-slate-50 dark:bg-slate-800/50 rounded-r"
        {...props}
      />
    ),
  }

  const renderLessonContent = (lesson: Lesson) => {
    const { content_type, content } = lesson

    const MarkdownBody = ({ textContent }: { textContent: string }) => (
      <div className="prose dark:prose-invert max-w-none">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[rehypeRaw]}
          components={markdownComponents}
        >
          {textContent}
        </ReactMarkdown>
      </div>
    )

    switch (content_type) {
      case 'assignment':
        return <MarkdownBody textContent={preprocessMarkdownContent(content)} />

      case 'code': {
        let codeContent = content
        let language = 'text'
        try {
          const parsed = JSON.parse(content)
          if (parsed && typeof parsed === 'object') {
            codeContent = parsed.code || content
            language = parsed.language || 'text'
          }
        } catch {
          /* empty */
        }

        return (
          <div className="w-full">
            <h3 className="text-lg font-medium mb-2 flex items-center gap-2">
              <Code className="w-5 h-5 text-brand-600" />
              {t('Приклад коду')}
            </h3>
            <CodeDisplay code={codeContent} language={language} />
          </div>
        )
      }

      case 'link':
      case 'custom':
      case 'text':
      default: {
        const processedContent = preprocessMarkdownContent(content)
        return (
          <div className="w-full max-w-none text-slate-800 dark:text-slate-200 leading-relaxed">
            <MarkdownBody textContent={processedContent} />
          </div>
        )
      }
    }
  }

  if (isLoading) {
    return (
      <>
        <Button variant="ghost" onClick={onBack} className="mb-4">
          <ArrowLeft className="w-4 h-4 mr-2" /> {t('Назад до опису курсу')}
        </Button>
        <Card className="min-h-[300px] flex items-center justify-center">
          <LoadingProfile message={t('Завантаження матеріалу...')} />
        </Card>
      </>
    )
  }

  if (!activeElement) return null

  const backButton = (
    <div className="flex justify-center w-full mb-4">
      <Button variant="secondary" onClick={onBack} className="w-60">
        <ArrowLeft className="w-4 h-4 mr-2" /> {t('Назад до опису курсу')}
      </Button>
    </div>
  )

  if ('lesson' in activeElement && activeElement.lesson) {
    const lesson = activeElement.lesson

    return (
      <>
        <Card className="mb-8 overflow-hidden shadow-sm border bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 transition-shadow hover:shadow-md dark:hover:shadow-gray-800/50">
          <CardContent className="text-slate-700 dark:text-slate-200">
            {renderLessonContent(lesson)}
          </CardContent>
        </Card>
        {backButton}
      </>
    )
  }

  if ('module-test' in activeElement && activeElement['module-test']) {
    const test = activeElement['module-test']
    return (
      <>
        <Card className="mb-8 shadow-sm border border-slate-200 dark:border-slate-800">
          <CardHeader>
            <h2 className="text-2xl font-bold">{test.title}</h2>
            <p className="text-muted-foreground">{test.description}</p>
          </CardHeader>
          <CardContent className="p-6 space-y-4">
            <div className="flex gap-4 text-sm text-muted-foreground">
              <div className="flex items-center gap-1">
                <Clock className="w-4 h-4" />
                {t('Ліміт часу:')} {test.time_limit} {t('хв')}
              </div>
              <div className="flex items-center gap-1">
                <FileCheck className="w-4 h-4" />
                {t('Питань:')} {test.questions.length}
              </div>
            </div>
            <Button className="w-full sm:w-auto">{t('Розпочати тест')}</Button>
          </CardContent>
        </Card>
        {backButton}
      </>
    )
  }

  if ('course-test' in activeElement && activeElement['course-test']) {
    const test = activeElement['course-test']
    return (
      <>
        <Card className="mb-8 shadow-sm border border-slate-200 dark:border-slate-800">
          <CardHeader>
            <h2 className="text-2xl font-bold">{test.title}</h2>
            <p className="text-muted-foreground">{test.description}</p>
          </CardHeader>
          <CardContent className="p-6 space-y-4">
            <div className="flex gap-4 text-sm text-muted-foreground">
              <div className="flex items-center gap-1">
                <Clock className="w-4 h-4" />
                {t('Ліміт часу:')} {test.time_limit} {t('хв')}
              </div>
              <div className="flex items-center gap-1">
                <FileCheck className="w-4 h-4" />
                {t('Питань:')} {test.questions.length}
              </div>
            </div>
            <Button className="w-full sm:w-auto">
              {t('Розпочати фінальний тест')}
            </Button>
          </CardContent>
        </Card>
        {backButton}
      </>
    )
  }

  // TODO add button next and previoue element

  return null
}
