import { useI18n } from '@/shared/lib'
import { Button } from '@/shared/ui'
import {
  AlertCircle,
  ArrowRight,
  Award,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Clock,
  HelpCircle,
  Loader2,
  RotateCw,
  Trophy,
  XCircle,
} from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'

export interface TestQuestion {
  id: string | number
  questionText: string
  type?: 'single' | 'multiple'
  choices: string[]
  points: number
  image_url?: string
  explanation?: string | null
  order?: number
}

export interface TestData {
  id: string
  title: string
  description?: string
  time_limit: number
  questions: TestQuestion[]
  pass_score: number
  test_type?: 'course-test' | 'module-test'
  course_id?: string
  can_attempt?: boolean
  max_attempts?: number | string
  randomize_questions?: boolean
}

export interface QuestionResult {
  order: number
  is_correct: boolean
  points_awarded: number
  max_points: number
  selected_choices: string[]
  correct_choices?: string[]
  explanation?: string | null
}

export interface TestResult {
  score: number
  max_score: number
  passed: boolean
  percent: number
  questions_result?: QuestionResult[]
}

interface TestPlayerProps {
  testData: TestData
  onBack: () => void
  onFinishCourse?: (timeSpent: number) => void
  isLast: boolean
  onSubmit: (answers: any[], timeSpent: number) => Promise<TestResult>
  isCourseCompleted: boolean
  onStatsRefresh?: () => void
}

const shuffleArray = <T,>(array: T[]): T[] => {
  const newArray = [...array]
  for (let i = newArray.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[newArray[i], newArray[j]] = [newArray[j], newArray[i]]
  }
  return newArray
}

export const TestPlayer = ({
  testData,
  onBack,
  onFinishCourse,
  onSubmit,
  isLast,
  isCourseCompleted,
}: TestPlayerProps) => {
  const { t } = useI18n()

  const [status, setStatus] = useState<
    'intro' | 'active' | 'submitting' | 'finished'
  >('intro')
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)

  const [answers, setAnswers] = useState<Record<string, string[]>>({})
  const [timeLeft, setTimeLeft] = useState(testData.time_limit * 60)
  const [timeSpentOnAttempt, setTimeSpentOnAttempt] = useState(0)
  const [serverResult, setServerResult] = useState<TestResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const processedQuestions = useMemo(() => {
    let questions = [...testData.questions]

    if (testData.randomize_questions) {
      questions = shuffleArray(questions)

      questions = questions.map(q => ({
        ...q,
        choices: shuffleArray(q.choices),
      }))
    }

    return questions
  }, [testData.questions, testData.randomize_questions])

  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(''), 15000)
      return () => clearTimeout(timer)
    }
  }, [error])

  useEffect(() => {
    let timer: NodeJS.Timeout
    if (status === 'active' && timeLeft > 0) {
      timer = setInterval(() => {
        setTimeLeft(prev => {
          if (prev <= 1) {
            handleFinishTest()
            return 0
          }
          return prev - 1
        })
      }, 1000)
    }
    return () => clearInterval(timer)
  }, [status, timeLeft])

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60)
    const s = seconds % 60
    return `${m}:${s < 10 ? '0' : ''}${s}`
  }

  const handleSelectOption = (
    questionId: string | number,
    choice: string,
    type: 'single' | 'multiple'
  ) => {
    const qId = String(questionId)

    if (error) setError(null)

    setAnswers(prev => {
      const current = prev[qId] || []

      if (type === 'single') {
        return { ...prev, [qId]: [choice] }
      } else {
        if (current.includes(choice)) {
          return { ...prev, [qId]: current.filter(c => c !== choice) }
        } else {
          return { ...prev, [qId]: [...current, choice] }
        }
      }
    })
  }

  const handleNext = () => {
    if (error) setError(null)
    if (currentQuestionIndex < processedQuestions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1)
    } else {
      handleFinishTest()
    }
  }

  const handlePrev = () => {
    if (error) setError(null)
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1)
    }
  }

  const handleFinishTest = async () => {
    setStatus('submitting')
    setError(null)

    const calculatedTimeSpent = testData.time_limit * 60 - timeLeft
    setTimeSpentOnAttempt(calculatedTimeSpent)

    const payload = processedQuestions.map(q => ({
      order: q.order || q.id,
      selected_options: answers[String(q.id)] || [],
    }))

    try {
      const result = await onSubmit(payload, calculatedTimeSpent)
      setServerResult(result)
      setStatus('finished')

      if (onStatsRefresh) {
        onStatsRefresh()
      }

      window.scrollTo({ top: 0, behavior: 'smooth' })
    } catch (err: unknown) {
      setStatus('active')

      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError(t('Виникла невідома помилка при відправці. Спробуйте ще раз.'))
      }
    }
  }

  if (status === 'submitting') {
    return (
      <div className="flex flex-col items-center justify-center py-20 animate-in fade-in">
        <Loader2 className="w-16 h-16 text-brand-600 animate-spin mb-4" />
        <h3 className="text-xl font-medium text-slate-700 dark:text-slate-300">
          {t('Перевіряємо ваші відповіді...')}
        </h3>
      </div>
    )
  }

  if (status === 'finished' && serverResult) {
    const { passed, score, max_score, percent, questions_result } = serverResult

    const canTryAgain = testData.can_attempt !== false

    return (
      <div className="animate-in fade-in duration-500 py-8 text-left">
        <div
          className={`p-8 rounded-xl border-2 ${passed ? 'bg-green-50 border-green-100 dark:bg-green-900/20 dark:border-green-900' : 'bg-red-50 border-red-100 dark:bg-red-900/20 dark:border-red-900'} text-center max-w-2xl mx-auto`}
        >
          <div
            className={`w-24 h-24 mx-auto rounded-full flex items-center justify-center mb-6 shadow-sm ${passed ? 'bg-white text-green-600 dark:bg-green-900 dark:text-green-300' : 'bg-white text-red-600 dark:bg-red-900 dark:text-red-300'}`}
          >
            {passed ? (
              <Trophy className="w-12 h-12" />
            ) : (
              <XCircle className="w-12 h-12" />
            )}
          </div>

          <h2 className="text-3xl font-bold mb-3 text-slate-900 dark:text-slate-100">
            {passed ? t('Тест успішно складено!') : t('Тест не складено')}
          </h2>
          <p className="text-slate-600 dark:text-slate-400 mb-8 max-w-md mx-auto">
            {passed
              ? t('Вітаємо! Ви продемонстрували відмінні знання.')
              : t(
                  'На жаль, набраних балів недостатньо. Спробуйте ще раз, щоб закріпити матеріал.'
                )}
          </p>

          <div className="grid grid-cols-2 gap-4 mb-8">
            <div className="bg-white/80 dark:bg-slate-800/80 p-4 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700">
              <div className="text-xs text-muted-foreground uppercase font-bold tracking-wider mb-1">
                {t('Ваш результат')}
              </div>
              <div className="text-2xl font-bold text-slate-900 dark:text-white">
                {score}{' '}
                <span className="text-sm font-normal text-muted-foreground">
                  / {max_score}
                </span>
              </div>
            </div>
            <div className="bg-white/80 dark:bg-slate-800/80 p-4 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700">
              <div className="text-xs text-muted-foreground uppercase font-bold tracking-wider mb-1">
                {t('Ефективність')}
              </div>
              <div
                className={`text-2xl font-bold ${passed ? 'text-green-600' : 'text-red-600'}`}
              >
                {percent}%
              </div>
            </div>
          </div>

          {questions_result && questions_result.length > 0 && (
            <div className="mt-8 space-y-4 text-left">
              <h3 className="font-bold text-lg mb-4 text-center">
                {t('Детальний розбір')}
              </h3>
              {questions_result.map((qResult, idx) => {
                const questionData = testData.questions.find(
                  q => (q.order || q.id) === qResult.order
                )
                return (
                  <div
                    key={idx}
                    className={`p-4 rounded-lg border ${
                      qResult.is_correct
                        ? 'border-green-200 bg-green-50/50 dark:border-green-900 dark:bg-green-900/10'
                        : 'border-red-200 bg-red-50/50 dark:border-red-900 dark:bg-red-900/10'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      {qResult.is_correct ? (
                        <CheckCircle2 className="w-5 h-5 text-green-600 mt-1 shrink-0" />
                      ) : (
                        <XCircle className="w-5 h-5 text-red-600 mt-1 shrink-0" />
                      )}
                      <div className="w-full">
                        <p className="font-medium text-slate-900 dark:text-slate-100 mb-2">
                          {questionData?.questionText ||
                            `Question ${qResult.order}`}
                        </p>

                        <div className="text-sm text-slate-600 dark:text-slate-400 mb-1">
                          <span className="font-semibold">
                            {t('Ваша відповідь:')}{' '}
                          </span>
                          {qResult.selected_choices.join(', ') || t('Немає')}
                        </div>

                        {qResult.correct_choices && (
                          <div className="text-sm text-green-700 dark:text-green-400 mb-2">
                            <span className="font-semibold">
                              {t('Правильна відповідь:')}{' '}
                            </span>
                            {qResult.correct_choices.join(', ')}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}

          <div className="flex justify-center gap-4 mt-8">
            {!passed && canTryAgain && (
              <Button
                variant="outline"
                onClick={() => {
                  setAnswers({})
                  setServerResult(null)
                  setTimeLeft(testData.time_limit * 60)
                  setCurrentQuestionIndex(0)
                  setStatus('intro')
                }}
              >
                <RotateCw className="w-4 h-4 mr-2" />
                {t('Пройти знову')}
              </Button>
            )}

            {!passed && !canTryAgain && (
              <div className="text-red-500 font-medium py-2 flex items-center gap-2">
                <AlertCircle className="w-5 h-5" />
                {t('Спроби вичерпано. Ви не можете перездати цей тест.')}
              </div>
            )}

            {passed && onFinishCourse && (
              <Button
                onClick={() => onFinishCourse(timeSpentOnAttempt)}
                className="bg-brand-600 hover:bg-brand-700"
              >
                {isLast ? (
                  <>
                    <span>
                      {isCourseCompleted
                        ? t('Отримати сертифікат')
                        : t('Завершіть усі завдання')}
                    </span>
                    <Award className="w-4 h-4 ml-2" />
                  </>
                ) : (
                  <>
                    {t('Продовжити')}
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </>
                )}
              </Button>
            )}
          </div>
        </div>
      </div>
    )
  }

  if (status === 'active') {
    const currentQuestion = processedQuestions[currentQuestionIndex]
    const questionType = currentQuestion.type || 'single'

    const progress =
      ((currentQuestionIndex + 1) / processedQuestions.length) * 100
    const qId = String(currentQuestion.id || currentQuestion.questionText)
    const currentSelected = answers[qId] || []

    let IMAGE_URL = import.meta.env.VITE_COURSE_QUESTION_IMAGE_PATH
    if (
      testData.test_type === 'module-test' ||
      testData.test_type === 'course-test'
    ) {
      IMAGE_URL = `${IMAGE_URL}course-cover-pictures/${testData.course_id}/${testData.test_type}/${currentQuestion.image_url}`
    }

    return (
      <div className="my-6 space-y-6 animate-in slide-in-from-right-8 duration-300 max-w-3xl mx-auto">
        <div className="mt-6 flex items-center justify-between bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-slate-100 dark:border-slate-800">
          <div
            className={`flex items-center gap-2 font-mono font-bold text-lg ${timeLeft < 60 ? 'text-red-500 animate-pulse' : 'text-brand-600 dark:text-brand-400'}`}
          >
            <Clock className="w-5 h-5" />
            <span>{formatTime(timeLeft)}</span>
          </div>
          <div className="text-sm font-medium text-slate-500 dark:text-slate-400">
            {t('Питання')}{' '}
            <span className="text-slate-900 dark:text-slate-200 font-bold">
              {currentQuestionIndex + 1}
            </span>{' '}
            / {processedQuestions.length}
          </div>
        </div>

        <div className="w-full bg-slate-100 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden">
          <div
            className="bg-brand-600 h-full transition-all duration-500 ease-out rounded-full"
            style={{ width: `${progress}%` }}
          />
        </div>

        <div className="py-2">
          {error && (
            <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md text-sm font-medium border border-red-200">
              {error}
            </div>
          )}

          <h3 className="text-xl md:text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 leading-tight">
            {currentQuestion.questionText}
          </h3>

          {currentQuestion.image_url && (
            <div className="mb-6 rounded-xl overflow-hidden border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900">
              <img
                src={`${IMAGE_URL}`}
                alt="Question illustration"
                className="w-full h-auto max-h-[300px] object-contain mx-auto"
                onError={e => {
                  e.currentTarget.style.display = 'none'
                }}
              />
            </div>
          )}

          <div className="flex flex-col gap-3 mb-6 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-slate-200/60 dark:border-slate-700 p-4 w-full md:w-fit md:min-w-[400px]">
            <div className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <HelpCircle className="w-4 h-4 text-slate-400" />
                <span className="font-medium">
                  {questionType === 'single'
                    ? t('Оберіть одну правильну відповідь')
                    : t('Оберіть всі правильні відповіді')}
                </span>
              </div>

              <span className="px-2.5 py-1 bg-white dark:bg-slate-700 rounded-md border border-slate-200 dark:border-slate-600 text-xs font-bold text-slate-700 dark:text-slate-200 shadow-sm whitespace-nowrap">
                {currentQuestion.points} {t('балів')}
              </span>
            </div>

            {currentQuestion.explanation && (
              <div className="flex gap-3 pt-3 mt-1 border-t border-slate-200 dark:border-slate-700">
                <div className="mt-0.5 shrink-0">
                  <div className="w-5 h-5 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                    <span className="text-xs font-bold text-blue-600 dark:text-blue-400">
                      i
                    </span>
                  </div>
                </div>
                <div className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                  {currentQuestion.explanation}
                </div>
              </div>
            )}
          </div>

          <div className="space-y-3">
            {currentQuestion.choices.map((choice, idx) => {
              const isSelected = currentSelected.includes(choice)
              return (
                <div
                  key={idx}
                  onClick={() => handleSelectOption(qId, choice, questionType)}
                  className={`
                    relative p-4 rounded-xl border-2 cursor-pointer transition-all duration-200 flex items-center gap-4 group
                    ${
                      isSelected
                        ? 'border-brand-600 bg-brand-50/50 dark:bg-brand-900/10 shadow-sm'
                        : 'border-slate-200 dark:border-slate-700 hover:border-brand-300 dark:hover:border-slate-600 bg-white dark:bg-slate-900'
                    }
                  `}
                >
                  <div
                    className={`
                    w-6 h-6 rounded-full border-2 flex items-center justify-center shrink-0 transition-colors
                    ${questionType === 'single' ? 'rounded-full' : 'rounded-md'}
                    ${
                      isSelected
                        ? 'bg-brand-600 border-brand-600 text-white'
                        : 'border-slate-300 dark:border-slate-600 group-hover:border-brand-400'
                    }
                  `}
                  >
                    {isSelected && (
                      <div
                        className={`w-2.5 h-2.5 bg-white ${questionType === 'single' ? 'rounded-full' : 'rounded-[2px]'}`}
                      />
                    )}
                  </div>
                  <span
                    className={`font-medium text-base ${isSelected ? 'text-brand-950 dark:text-brand-50' : 'text-slate-700 dark:text-slate-300'}`}
                  >
                    {choice}
                  </span>
                </div>
              )
            })}
          </div>
        </div>

        <div className="mb-6 flex justify-between pt-8 mt-4 border-t border-slate-100 dark:border-slate-800">
          <Button
            variant="ghost"
            onClick={handlePrev}
            disabled={currentQuestionIndex === 0}
            className="text-slate-500 hover:text-slate-900"
          >
            <ChevronLeft className="w-4 h-4 mr-2" /> {t('Назад')}
          </Button>

          <Button
            onClick={handleNext}
            size="lg"
            className="bg-brand-600 hover:bg-brand-700 px-8 shadow-md hover:shadow-lg transition-all"
            disabled={currentSelected.length === 0}
          >
            {currentQuestionIndex === processedQuestions.length - 1 ? (
              <>
                {t('Завершити тест')} <CheckCircle2 className="w-4 h-4 ml-2" />
              </>
            ) : (
              <>
                {t('Наступне питання')}{' '}
                <ChevronRight className="w-4 h-4 ml-2" />
              </>
            )}
          </Button>
        </div>
      </div>
    )
  }

  const canStart = testData.can_attempt !== false

  return (
    <div className="py-12 text-center animate-in zoom-in-95 duration-300">
      <div className="w-24 h-24 bg-brand-50 dark:bg-brand-900/20 text-brand-600 dark:text-brand-400 rounded-full flex items-center justify-center mx-auto mb-8 shadow-sm">
        <AlertCircle className="w-12 h-12" />
      </div>

      <h2 className="text-3xl font-bold text-slate-900 dark:text-slate-100 mb-4">
        {canStart ? t('Ви готові розпочати?') : t('Спроби вичерпано')}
      </h2>

      {canStart ? (
        <p className="text-slate-600 dark:text-slate-400 max-w-md mx-auto mb-10 text-lg leading-relaxed">
          {t('Тест містить')}{' '}
          <span className="font-bold text-slate-900 dark:text-white">
            {testData.questions.length}
          </span>{' '}
          {t('питань')}. {t('У вас буде')}
          <span className="font-bold text-slate-900 dark:text-white">
            {' '}
            {testData.time_limit} {t('хвилин')}
          </span>
          ,{' '}
          {t('щоб відповісти на них. Після початку таймер не можна зупинити.')}
        </p>
      ) : (
        <p className="text-red-500 font-medium mb-10 text-lg">
          {t('На жаль, ви використали всі доступні спроби для цього тесту.')}
        </p>
      )}

      <div className="flex justify-center gap-4">
        <Button
          variant="outline"
          size="lg"
          onClick={onBack}
          className="min-w-[140px]"
        >
          {t('Скасувати')}
        </Button>
        {canStart && (
          <Button
            size="lg"
            onClick={() => setStatus('active')}
            className="bg-brand-600 hover:bg-brand-700 min-w-[200px] shadow-lg hover:shadow-xl transition-all"
          >
            {t('Розпочати тестування')}
          </Button>
        )}
      </div>
    </div>
  )
}
