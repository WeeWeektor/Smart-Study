import React, {
  type ComponentPropsWithoutRef,
  useEffect,
  useMemo,
  useState,
} from 'react'
import ReactMarkdown, { type Components } from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeRaw from 'rehype-raw'
import {
  ArrowLeft,
  Award,
  BookOpen,
  ChevronLeft,
  ChevronRight,
  ClipboardList,
  Code,
  FileCheck,
  LayoutGrid,
  RotateCw,
  Timer,
  Trophy,
} from 'lucide-react'
import { Button, Card, CardContent, LoadingProfile } from '@/shared/ui'
import { CodeDisplay } from '@/features/lesson-type-fields/ui'
import { useI18n } from '@/shared/lib'
import { type ElementOfCourseResponse } from '@/features/course'
import type { Lesson } from '@/features/course/get.element.of.course.service.ts'
import { type TestData, TestPlayer } from '@/pages/course-review'

interface ActiveCourseElementProps {
  activeElement: ElementOfCourseResponse | null
  isLoading: boolean
  onBack: () => void
  onNext: () => void
  onPrev: () => void
  isFirst: boolean
  isLast: boolean
  isOwner: boolean
  onFinish: () => void
  onComplete?: (id: string, type: string) => void
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
  onNext,
  onPrev,
  isFirst,
  isLast,
  isOwner,
  onFinish,
  onComplete,
}) => {
  const { t } = useI18n()

  const [isTestStarted, setIsTestStarted] = useState(false)

  useEffect(() => {
    setIsTestStarted(false)
  }, [activeElement])

  useEffect(() => {
    const lesson =
      activeElement && 'lesson' in activeElement ? activeElement.lesson : null
    if (!lesson || !onComplete) return

    const lessonId = lesson.id
    let timerPassed = false
    let scrollPassed = false

    const timer = setTimeout(() => {
      timerPassed = true
      checkCompletion()
    }, 10000)

    const handleScroll = () => {
      const isBottom =
        window.innerHeight + window.scrollY >= document.body.offsetHeight - 100

      if (isBottom) {
        scrollPassed = true
        checkCompletion()
      }
    }

    const checkCompletion = () => {
      if (timerPassed && scrollPassed) {
        onComplete(lessonId, 'lesson')
      }
    }

    if (document.body.offsetHeight <= window.innerHeight + 50) {
      scrollPassed = true
    }

    window.addEventListener('scroll', handleScroll)

    return () => {
      clearTimeout(timer)
      window.removeEventListener('scroll', handleScroll)
    }
  }, [activeElement, onComplete])

  const currentTestInfo = useMemo(() => {
    if (!activeElement) return null

    if ('module-test' in activeElement && activeElement['module-test']) {
      return {
        test: activeElement['module-test'],
        testType: 'module-test' as const,
        course_id: activeElement['module-test'].module.course,
      }
    }

    if ('course-test' in activeElement && activeElement['course-test']) {
      return {
        test: activeElement['course-test'],
        testType: 'course-test' as const,
        course_id: activeElement['course-test'].course.id,
      }
    }

    return null
  }, [activeElement])

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
        className="border-l-4 border-brand-500 pl-4 pr-4 py-2 my-4 italic bg-slate-50 dark:bg-slate-800/50 rounded-r [&>p]:mb-0"
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

  const NavigationFooter = () => (
    <div className="mt-8 pt-6 border-t border-slate-200 dark:border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
      <Button
        variant="outline"
        onClick={isFirst ? onBack : onPrev}
        className="w-full sm:w-auto min-w-[160px] flex items-center gap-2 group"
      >
        {isFirst ? (
          <>
            <BookOpen className="w-4 h-4 text-slate-500 group-hover:text-slate-900 dark:text-slate-400 dark:group-hover:text-white" />
            <span>{t('До опису курсу')}</span>
          </>
        ) : (
          <>
            <ChevronLeft className="w-4 h-4" />
            <span>{t('Попередній крок')}</span>
          </>
        )}
      </Button>

      <Button
        onClick={isLast ? onFinish : onNext}
        className={`w-full sm:w-auto min-w-[160px] flex items-center gap-2 shadow-sm
          ${isLast ? 'bg-green-600 hover:bg-green-700 text-white' : 'bg-brand-600 hover:bg-brand-700'}`}
      >
        {isLast ? (
          <>
            {isOwner ? (
              <>
                <LayoutGrid className="w-4 h-4" />
                <span>{t('До моїх курсів')}</span>
              </>
            ) : (
              <>
                <Award className="w-4 h-4" />
                <span>{t('Отримати сертифікат')}</span>
              </>
            )}
          </>
        ) : (
          <>
            <span>{t('Наступний крок')}</span>
            <ChevronRight className="w-4 h-4" />
          </>
        )}
      </Button>
    </div>
  )

  if (isLoading) {
    return (
      <Card className="min-h-[300px] flex items-center justify-center">
        <LoadingProfile message={t('Завантаження матеріалу...')} />
      </Card>
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
            <NavigationFooter />
          </CardContent>
        </Card>
        {!isFirst ? backButton : null}
      </>
    )
  }

  if (currentTestInfo) {
    const { test, testType, course_id } = currentTestInfo

    if (isTestStarted) {
      const testDataForPlayer: TestData = {
        id: test.id,
        title: test.title,
        description: test.description,
        time_limit: test.time_limit,
        pass_score: test.pass_score || 0,
        test_type: testType,
        course_id: course_id,
        questions: test.questions.map((q: any) => ({
          id: q.order || q.id || Math.random(),
          questionText: q.questionText,
          choices: q.choices,
          correct_answers: q.correct_answers,
          points: q.points,
          image_url: q.image_url || undefined,
          explanation: q.explanation || null,
        })),
      }

      return (
        <Card className="mb-8 overflow-hidden shadow-sm border bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800">
          <CardContent className="p-0 sm:p-0">
            {' '}
            <TestPlayer
              testData={testDataForPlayer}
              onBack={() => setIsTestStarted(false)}
              onFinishCourse={() => {
                if (test) {
                  onComplete?.(test.id, 'test')
                }

                if (isLast) onFinish()
                else onNext()
              }}
            />
          </CardContent>
        </Card>
      )
    }

    return (
      <>
        <Card className="mb-8 overflow-hidden shadow-sm border bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 transition-shadow hover:shadow-md dark:hover:shadow-gray-800/50">
          <CardContent className="text-slate-700 dark:text-slate-200">
            <h1 className="text-3xl font-bold mt-8 mb-4 pb-2 border-b border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-100">
              {test.title}
            </h1>

            {test.description && (
              <blockquote className="border-l-4 border-brand-500 pl-4 pr-4 py-2 my-4 italic bg-slate-50 dark:bg-slate-800/50 rounded-r [&>p]:mb-0">
                {test.description}
              </blockquote>
            )}

            <div className="grid md:grid-cols-4 gap-6 gap-x-8 gap-y-6 mb-8 p-5 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-100 dark:border-slate-800">
              <div className="flex items-center gap-3">
                <div className="p-2.5 bg-white dark:bg-slate-700 rounded-lg shadow-sm border border-slate-100 dark:border-slate-600">
                  <Timer className="w-5 h-5 text-orange-500" />
                </div>
                <div>
                  <div className="text-[10px] uppercase font-bold text-muted-foreground tracking-wider">
                    {t('Ліміт часу')}
                  </div>
                  <div className="font-semibold text-slate-800 dark:text-slate-200">
                    {test.time_limit === 0
                      ? t('Необмежено')
                      : `${test.time_limit} ${t('хв')}`}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="p-2.5 bg-white dark:bg-slate-700 rounded-lg shadow-sm border border-slate-100 dark:border-slate-600">
                  <RotateCw className="w-5 h-5 text-purple-500" />
                </div>
                <div>
                  <div className="text-[10px] uppercase font-bold text-muted-foreground tracking-wider">
                    {t('Спроби')}
                  </div>
                  <div className="font-semibold text-slate-800 dark:text-slate-200">
                    {test.count_attempts === 0
                      ? t('Необмежено')
                      : `${test.count_attempts} ${t('разів')}`}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="p-2.5 bg-white dark:bg-slate-700 rounded-lg shadow-sm border border-slate-100 dark:border-slate-600">
                  <Trophy className="w-5 h-5 text-yellow-500" />
                </div>
                <div>
                  <div className="text-[10px] uppercase font-bold text-muted-foreground tracking-wider">
                    {t('Прохідний бал')}
                  </div>
                  <div className="font-semibold text-slate-800 dark:text-slate-200">
                    {test.pass_score} {t('балів')}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="p-2.5 bg-white dark:bg-slate-700 rounded-lg shadow-sm border border-slate-100 dark:border-slate-600">
                  <FileCheck className="w-5 h-5 text-blue-500" />
                </div>
                <div>
                  <div className="text-[10px] uppercase font-bold text-muted-foreground tracking-wider">
                    {t('Всього питань')}
                  </div>
                  <div className="font-semibold text-slate-800 dark:text-slate-200">
                    {test.questions.length} {t('завдань')}
                  </div>
                </div>
              </div>
            </div>

            <div className="flex justify-center w-full mb-4">
              <Button
                size="lg"
                className="w-full sm:w-auto text-base px-8 bg-brand-600 hover:bg-brand-700 shadow-md "
                onClick={() => setIsTestStarted(true)}
              >
                {t('Розпочати тест')}
              </Button>
            </div>

            <NavigationFooter />
          </CardContent>
        </Card>
        {!isFirst ? backButton : null}
      </>
    )
  }

  return null
}
