import React, { type FC, useState } from 'react'
import { useI18n } from '@/shared/lib'
import {
  AddQuestionToTestModal,
  type BaseTest,
  Button,
  Card,
  Checkbox,
  type CourseTest,
  Input,
  Label,
  type ModuleTest,
} from '@/shared/ui'
import {
  ChevronDown,
  ChevronUp,
  Loader2,
  PlusCircle,
  Save,
  Trash2,
  Undo,
} from 'lucide-react'
import { disablePageScroll, enablePageScroll } from '@/shared/scroll'

interface CreateTestModalProps {
  order: number
  type: 'module-test' | 'course-test'
  onClose: () => void
  onAddTest: (test: BaseTest & { type: 'module-test' | 'course-test' }) => void
}

export interface Question {
  questionText: string
  choices: string[]
  correctAnswers: string[]
  points: number
  order: number
  image: string | null
  explanation: string | null
  imageFile: File | null
}

export const CreateTestModal: FC<CreateTestModalProps> = ({
  order,
  type,
  onClose,
  onAddTest,
}) => {
  const { t } = useI18n()
  const [error, setError] = useState<string | null>(null)
  const [title, setTitle] = useState<string>('')
  const [description, setDescription] = useState<string>('')
  const [timeLimit, setTimeLimit] = useState<number>()
  const [countAttempts, setCountAttempts] = useState<number>()
  const [passScore, setPassScore] = useState<number>()
  const [randomQuestions, setRandomQuestions] = useState<boolean>(false)
  const [showAnswers, setShowAnswers] = useState<boolean>(false)
  const [questions, setQuestions] = useState<Question[]>([])
  const [isAdding, setIsAdding] = useState(false)
  const [isCreateQuestionOpen, setIsCreateQuestionOpen] = useState(false)
  const [questionModalData, setQuestionModalData] = useState<{
    order: number
  } | null>(null)
  const [collapsedQuestions, setCollapsedQuestions] = useState<
    Record<number, boolean>
  >({})

  React.useEffect(() => {
    disablePageScroll()
    return () => enablePageScroll()
  }, [])

  const handleContentClick = (e: React.MouseEvent) => e.stopPropagation()

  const handleNumericInput = (
    raw: string,
    setter: React.Dispatch<React.SetStateAction<number | undefined>>,
    options?: { min?: number; max?: number; allowEmpty?: boolean }
  ) => {
    const digitsOnly = raw.replace(/\D+/g, '')

    if (digitsOnly === '') {
      setter(undefined)
      return
    }

    const num = Number(digitsOnly)
    if (Number.isNaN(num)) {
      setter(undefined)
      return
    }

    let clamped = num
    if (options?.min !== undefined && clamped < options.min)
      clamped = options.min
    if (options?.max !== undefined && clamped > options.max)
      clamped = options.max

    setter(clamped)
  }

  const handleAddTest = async () => {
    setError(null)

    if (!title.trim() || !description.trim()) {
      setError(t('Будь ласка, заповніть усі обов’язкові поля.'))
      return
    }
    if (
      timeLimit === undefined ||
      countAttempts === undefined ||
      passScore === undefined
    ) {
      setError(t('Введіть числові значення для параметрів тесту.'))
      return
    }

    const newTest: CourseTest | ModuleTest = {
      ...{
        type,
        title,
        description,
        time_limit: timeLimit,
        count_attempts: countAttempts,
        pass_score: passScore,
        random_questions: randomQuestions,
        show_correct_answers: showAnswers,
        questions,
      },
      order,
    }

    setIsAdding(true)
    await new Promise(resolve => setTimeout(resolve, 500))
    onAddTest(newTest)
    setIsAdding(false)
    onClose()
  }

  const handleCancelAddTest = () => {
    setTitle('')
    setDescription('')
    setTimeLimit(undefined)
    setCountAttempts(undefined)
    setPassScore(undefined)
    setRandomQuestions(false)
    setShowAnswers(false)
    setQuestions([])
    setError(null)
    onClose()
  }

  const toggleQuestionCollapse = (order: number) => {
    setCollapsedQuestions(prev => ({
      ...prev,
      [order]: !prev[order],
    }))
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm">
      <div
        className="bg-white dark:bg-slate-800 rounded-xl w-9/12 max-w-6xl max-h-[80vh]
           overflow-y-auto p-6 relative shadow-2xl
           scrollbar-thin
           scrollbar-thumb-transparent
           hover:scrollbar-thumb-gray-400 dark:hover:scrollbar-thumb-gray-600
           transition-colors"
        onClick={handleContentClick}
      >
        <h2 className="flex items-center justify-center text-2xl font-semibold mb-4">
          {`${t('Тест')} ${order}${title ? ` - ${title.length > 30 ? title.slice(0, 30) + '...' : title}` : ''}`}
        </h2>

        <button
          onClick={onClose}
          className="absolute top-3 right-3 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
        >
          ✕
        </button>

        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">
            {error}
          </div>
        )}

        <div className="gap-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
            <div>
              <Label htmlFor="title">{t('Назва тесту *')}</Label>
              <Input
                id="title"
                value={title}
                onChange={e => setTitle(e.target.value)}
                placeholder={t('Введіть назву тесту')}
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="description">{t('Опис тесту *')}</Label>
              <Input
                id="description"
                value={description}
                onChange={e => setDescription(e.target.value)}
                placeholder={t('Введіть опис тесту')}
                className="mt-1"
              />
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
            <div>
              <Label htmlFor="timeLimit">{t('Обмеження в часі *')}</Label>
              <Input
                id="timeLimit"
                type="text"
                value={timeLimit ?? ''}
                onChange={e => handleNumericInput(e.target.value, setTimeLimit)}
                placeholder={t(
                  'Часове обмеження в хвилинах (0 - без обмежень)'
                )}
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="сountAttempts">{t('Кількість спроб *')}</Label>
              <Input
                id="countAttempts"
                type="text"
                value={countAttempts ?? ''}
                onChange={e =>
                  handleNumericInput(e.target.value, setCountAttempts)
                }
                placeholder={t('Кількість дозволених спроб (0 - без обмежень)')}
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="passScore">{t('Прохідний бал за тест *')}</Label>
              <Input
                id="passScore"
                type="text"
                value={passScore ?? ''}
                onChange={e =>
                  handleNumericInput(e.target.value, setPassScore, {
                    min: 0,
                    max: 100,
                  })
                }
                placeholder={t('Мінімальний прохідний бал (0-100)')}
                className="mt-1"
              />
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
            <div className="flex items-center justify-center space-x-6 border border-gray-300 dark:border-gray-700 rounded-xl p-4 shadow-sm">
              <Label htmlFor="randomQuestions">
                {t('Перемішувати питання')}
              </Label>
              <Checkbox
                checked={randomQuestions}
                onCheckedChange={() => setRandomQuestions(!randomQuestions)}
              />
            </div>
            <div className="flex items-center justify-center space-x-6 border border-gray-300 dark:border-gray-700 rounded-xl p-4 shadow-sm">
              <Label htmlFor="showAnswers">
                {t('Показувати відповіді після завершення тесту')}
              </Label>
              <Checkbox
                checked={showAnswers}
                onCheckedChange={() => setShowAnswers(!showAnswers)}
              />
            </div>
          </div>
        </div>

        <div>
          <div className="my-4 flex-grow h-0.5 bg-gray-400 dark:bg-gray-600" />
          <div className="flex items-center justify-between mx-3">
            <p className="text-lg">{t('Питання тесту')}</p>
            <Button
              className="bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 text-white"
              size="sm"
              onClick={() => {
                const nextOrder = questions.length + 1
                setQuestionModalData({ order: nextOrder })
                setIsCreateQuestionOpen(true)
              }}
            >
              <PlusCircle className="w-4 h-4 mr-2" />
              {t('Додати питання')}
            </Button>
          </div>

          <div className="mt-6">
            {questions.length === 0 ? (
              <p className="text-center text-gray-600 dark:text-gray-400">
                {t(
                  'Питання ще не додані. Натисніть "Додати питання" вище, щоб почати.'
                )}
              </p>
            ) : (
              questions.map((q, index) => {
                const isCollapsed = collapsedQuestions[q.order] ?? false
                return (
                  <Card
                    key={q.order}
                    className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer bg-white dark:bg-slate-600 dark:hover:shadow-gray-700 mt-4"
                  >
                    <div
                      className="flex justify-between items-center p-3 cursor-pointer"
                      onClick={() => toggleQuestionCollapse(q.order)}
                    >
                      <div className="flex items-center space-x-3">
                        {isCollapsed ? (
                          <ChevronDown className="w-5 h-5" />
                        ) : (
                          <ChevronUp className="w-5 h-5" />
                        )}
                        <span className="font-semibold">
                          {t('Питання')} {index + 1}
                        </span>
                        <span className="px-2 py-1 text-xs bg-brand-600 text-white rounded-md">
                          {t('Вибір відповіді')}
                        </span>
                        <span className="text-sm text-gray-400 ml-2">
                          {q.points} {t('балів')}
                        </span>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200"
                        onClick={e => {
                          e.stopPropagation()
                          setQuestions(prev =>
                            prev.filter(ques => ques.order !== q.order)
                          )
                        }}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>

                    {!isCollapsed && (
                      <div className="p-4">
                        <p className="mb-3">{q.questionText}</p>
                        <div className="grid grid-cols-2 gap-2">
                          {q.choices.map((choice, i) => {
                            const isCorrect = q.correctAnswers.includes(choice)
                            return (
                              <div
                                key={i}
                                className={`p-2 rounded border ${
                                  isCorrect
                                    ? 'bg-green-100 dark:bg-green-800 border-green-300'
                                    : 'bg-gray-100 dark:bg-gray-700 border-gray-300'
                                }`}
                              >
                                {String.fromCharCode(65 + i)}. {choice}
                              </div>
                            )
                          })}
                        </div>
                      </div>
                    )}
                  </Card>
                )
              })
            )}
          </div>

          <div className="my-4 flex-grow h-0.5 bg-gray-400 dark:bg-gray-600" />
        </div>

        <div className="flex justify-center space-x-6 mt-6">
          <div>
            <Button
              className="w-60 hover:bg-gray-100 dark:hover:bg-gray-700"
              variant="outline"
              onClick={handleCancelAddTest}
              disabled={isAdding}
            >
              <Undo className="w-4 h-4 mr-2" />
              {t('Скасувати')}
            </Button>
          </div>

          <div>
            <Button
              className="w-60 bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 text-white"
              onClick={handleAddTest}
              disabled={isAdding}
            >
              {isAdding ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  {t('Додавання тесту...')}
                </>
              ) : (
                <>
                  <Save className="w-4 h-4 mr-2" />
                  {t('Додати тест')}
                </>
              )}
            </Button>
          </div>
        </div>
        {isCreateQuestionOpen && questionModalData && (
          <AddQuestionToTestModal
            order={questionModalData.order}
            onClose={() => setIsCreateQuestionOpen(false)}
            onAddQuestion={newQuestion => {
              setQuestions(prev => [...prev, newQuestion as Question])
            }}
          />
        )}
      </div>
    </div>
  )
}
