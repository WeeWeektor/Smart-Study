import { useI18n } from '@/shared/lib'
import { Button } from '@/shared/ui'
import {
  AlertCircle,
  ArrowRight,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Clock,
  HelpCircle,
  RotateCw,
  Trophy,
  XCircle,
} from 'lucide-react'
import { useEffect, useState } from 'react'

export interface TestQuestion {
  id: string | number
  questionText: string
  type?: 'single' | 'multiple'
  choices: string[]
  correct_answers: string[]
  points: number
  image_url?: string
  explanation?: string | null
}

export interface TestData {
  id: string
  title: string
  description?: string
  time_limit: number
  questions: TestQuestion[]
  pass_score: number
}

interface TestPlayerProps {
  testData: TestData
  onBack: () => void
  onFinishCourse?: () => void
}

export const TestPlayer = ({
  testData,
  onBack,
  onFinishCourse,
}: TestPlayerProps) => {
  const { t } = useI18n()

  const [status, setStatus] = useState<'intro' | 'active' | 'finished'>('intro')
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)

  const [answers, setAnswers] = useState<Record<string, string[]>>({})
  const [timeLeft, setTimeLeft] = useState(testData.time_limit * 60)
  const [score, setScore] = useState(0)

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
    if (currentQuestionIndex < testData.questions.length - 1) {
      setCurrentQuestionIndex(prev => prev + 1)
    } else {
      handleFinishTest()
    }
  }

  const handlePrev = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1)
    }
  }

  const handleFinishTest = () => {
    let totalScore = 0

    testData.questions.forEach(q => {
      const qId = String(q.id || q.questionText)
      const userAnswers = answers[qId] || []
      const correctAnswers = q.correct_answers || []

      const isCorrect =
        userAnswers.length === correctAnswers.length &&
        userAnswers.every(ans => correctAnswers.includes(ans))

      if (isCorrect) totalScore += q.points
    })

    setScore(totalScore)
    setStatus('finished')
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  if (status === 'finished') {
    const isPassed = score >= testData.pass_score
    const maxScore =
      testData.questions.reduce((acc, q) => acc + q.points, 0) || 1
    const percentage = Math.round((score / maxScore) * 100)

    return (
      <div className="animate-in fade-in duration-500 py-8">
        <div
          className={`p-8 rounded-xl border-2 ${isPassed ? 'bg-green-50 border-green-100 dark:bg-green-900/20 dark:border-green-900' : 'bg-red-50 border-red-100 dark:bg-red-900/20 dark:border-red-900'} text-center max-w-2xl mx-auto`}
        >
          <div
            className={`w-24 h-24 mx-auto rounded-full flex items-center justify-center mb-6 shadow-sm ${isPassed ? 'bg-white text-green-600 dark:bg-green-900 dark:text-green-300' : 'bg-white text-red-600 dark:bg-red-900 dark:text-red-300'}`}
          >
            {isPassed ? (
              <Trophy className="w-12 h-12" />
            ) : (
              <XCircle className="w-12 h-12" />
            )}
          </div>

          <h2 className="text-3xl font-bold mb-3 text-slate-900 dark:text-slate-100">
            {isPassed ? t('Тест успішно складено!') : t('Тест не складено')}
          </h2>
          <p className="text-slate-600 dark:text-slate-400 mb-8 max-w-md mx-auto">
            {isPassed
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
                  / {maxScore}
                </span>
              </div>
            </div>
            <div className="bg-white/80 dark:bg-slate-800/80 p-4 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700">
              <div className="text-xs text-muted-foreground uppercase font-bold tracking-wider mb-1">
                {t('Ефективність')}
              </div>
              <div
                className={`text-2xl font-bold ${isPassed ? 'text-green-600' : 'text-red-600'}`}
              >
                {percentage}%
              </div>
            </div>
          </div>

          <div className="flex justify-center gap-4">
            <Button
              variant="outline"
              onClick={() => {
                setAnswers({})
                setScore(0)
                setTimeLeft(testData.time_limit * 60)
                setCurrentQuestionIndex(0)
                setStatus('intro')
              }}
            >
              <RotateCw className="w-4 h-4 mr-2" />
              {t('Пройти знову')}
            </Button>
            {isPassed && onFinishCourse && (
              <Button
                onClick={onFinishCourse}
                className="bg-brand-600 hover:bg-brand-700"
              >
                {t('Продовжити')} <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            )}
          </div>
        </div>
      </div>
    )
  }

  if (status === 'active') {
    const currentQuestion = testData.questions[currentQuestionIndex]
    const questionType =
      currentQuestion.correct_answers.length > 1 ? 'multiple' : 'single'

    const progress =
      ((currentQuestionIndex + 1) / testData.questions.length) * 100
    const qId = String(currentQuestion.id || currentQuestion.questionText)
    const currentSelected = answers[qId] || []

    return (
      <div className="space-y-6 animate-in slide-in-from-right-8 duration-300 max-w-3xl mx-auto">
        <div className="flex items-center justify-between bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-slate-100 dark:border-slate-800">
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
            / {testData.questions.length}
          </div>
        </div>

        <div className="w-full bg-slate-100 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden">
          <div
            className="bg-brand-600 h-full transition-all duration-500 ease-out rounded-full"
            style={{ width: `${progress}%` }}
          />
        </div>

        <div className="py-2">
          <h3 className="text-xl md:text-2xl font-bold text-slate-900 dark:text-slate-100 mb-4 leading-tight">
            {currentQuestion.questionText}
          </h3>

          {currentQuestion.image_url && (
            <div className="mb-6 rounded-xl overflow-hidden border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900">
              <img
                src={currentQuestion.image_url}
                alt="Question illustration"
                className="w-full h-auto max-h-[300px] object-contain mx-auto"
              />
            </div>
          )}

          <div className="flex items-center gap-2 mb-6 text-sm text-muted-foreground bg-slate-50 dark:bg-slate-800/50 w-fit px-3 py-1.5 rounded-lg">
            <HelpCircle className="w-4 h-4" />
            {questionType === 'single'
              ? t('Оберіть одну правильну відповідь')
              : t('Оберіть всі правильні відповіді')}
            <span className="ml-2 px-1.5 py-0.5 bg-slate-200 dark:bg-slate-700 rounded text-xs font-bold text-slate-700 dark:text-slate-300">
              {currentQuestion.points} {t('балів')}
            </span>
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

        <div className="flex justify-between pt-8 mt-4 border-t border-slate-100 dark:border-slate-800">
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
          >
            {currentQuestionIndex === testData.questions.length - 1 ? (
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

  return (
    <div className="py-12 text-center animate-in zoom-in-95 duration-300">
      <div className="w-24 h-24 bg-brand-50 dark:bg-brand-900/20 text-brand-600 dark:text-brand-400 rounded-full flex items-center justify-center mx-auto mb-8 shadow-sm">
        <AlertCircle className="w-12 h-12" />
      </div>

      <h2 className="text-3xl font-bold text-slate-900 dark:text-slate-100 mb-4">
        {t('Ви готові розпочати?')}
      </h2>
      <p className="text-slate-600 dark:text-slate-400 max-w-md mx-auto mb-10 text-lg leading-relaxed">
        {t('Тест містить')}{' '}
        <span className="font-bold text-slate-900 dark:text-white">
          {testData.questions.length}
        </span>{' '}
        {t('питань')}. {t('У вас буде')}
        <span className="font-bold text-slate-900 dark:text-white">
          {testData.time_limit} {t('хвилин')}
        </span>
        , {t('щоб відповісти на них. Після початку таймер не можна зупинити.')}
      </p>

      <div className="flex justify-center gap-4">
        <Button
          variant="outline"
          size="lg"
          onClick={onBack}
          className="min-w-[140px]"
        >
          {t('Скасувати')}
        </Button>
        <Button
          size="lg"
          onClick={() => setStatus('active')}
          className="bg-brand-600 hover:bg-brand-700 min-w-[200px] shadow-lg hover:shadow-xl transition-all"
        >
          {t('Розпочати тестування')}
        </Button>
      </div>
    </div>
  )
}
