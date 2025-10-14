import { useI18n } from '@/shared/lib'
import { Loader2, Save, Undo } from 'lucide-react'
import React, { type FC, useState } from 'react'
import {
  Button,
  Input,
  Label,
  type Question,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Textarea,
} from '@/shared/ui'

interface CreateQuestionTestProps {
  order: number
  onClose: () => void
  onAddQuestion: (question: Question) => void
}

export const AddQuestionToTestModal: FC<CreateQuestionTestProps> = ({
  order,
  onClose,
  onAddQuestion,
}) => {
  const { t } = useI18n()
  const [error, setError] = useState<string | null>(null)
  const [isAdding, setIsAdding] = useState(false)
  const [questionText, setQuestionText] = useState<string>('')
  const [points, setPoints] = useState<number>()
  const [explanation, setExplanation] = useState<string | null>(null)
  const [correctAnswers, setCorrectAnswers] = useState<string[]>([])
  const [choices, setChoices] = useState<string[]>([])
  const [image, setImage] = useState<string | null>(null)
  const [imageFile, setImageFile] = useState<File | null>(null)
  const [typeQuestion, setTypeQuestion] = useState<'choice' | 'yes/no'>(
    'choice'
  )
  const [showPreviewQImage, setShowPreviewQImage] = useState<boolean>(false)

  const handleContentClick = (e: React.MouseEvent) => e.stopPropagation()

  const handleNumericInput = (
    raw: string,
    setter: React.Dispatch<React.SetStateAction<number | undefined>>
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

    setter(num)
  }

  const handleAddQuestion = async () => {
    setError(null)

    if (!questionText.trim()) {
      setError(t('Будь ласка, напишіть питання.'))
      return
    }
    if (points === undefined) {
      setError(
        t(
          'Введіть числове значення для параметру "Кількість балів за правильну відповідь".'
        )
      )
      return
    }
    if (choices.length === 0) {
      setError(t('Додайте хоча б один варіант відповіді.'))
      return
    }
    if (correctAnswers.length === 0) {
      setError(t('Вкажіть хоча б одну правильну відповідь.'))
      return
    }

    const newQuestion: Question = {
      questionText,
      choices,
      correctAnswers,
      points,
      order,
      image,
      explanation,
    }

    setIsAdding(true)
    await new Promise(resolve => setTimeout(resolve, 500))
    onAddQuestion(newQuestion)
    setIsAdding(false)
    onClose()
  }

  const handleCancelAddQuestion = () => {
    setQuestionText('')
    setExplanation('')
    setPoints(0)
    setImage('')
    setChoices([])
    setCorrectAnswers([])
    setError(null)
    onClose()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm">
      <div
        className="bg-white dark:bg-slate-800 rounded-xl w-8/12 max-w-6xl max-h-[80vh]
           overflow-y-auto p-6 relative shadow-2xl
           scrollbar-thin
           scrollbar-thumb-transparent
           hover:scrollbar-thumb-gray-400 dark:hover:scrollbar-thumb-gray-600
           transition-colors"
        onClick={handleContentClick}
      >
        <h2 className="flex items-center justify-center text-2xl font-semibold mb-4">
          {t('Питання')} {order}
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
          <div className="mt-6">
            <Label htmlFor="questionText">{t('Текст питання *')}</Label>
            <Textarea
              id="questionText"
              value={questionText}
              onChange={e => setQuestionText(e.target.value)}
              placeholder={t('Введіть текст питання')}
              rows={1}
              className="mt-1"
            />
          </div>

          <div className="mt-6">
            <Label htmlFor="QImage">{t('Зображення до питання')}</Label>
            <div className="flex flex-col gap-2 mt-1">
              <input
                type="file"
                accept="image/*"
                id="question-image-input"
                className="hidden"
                onChange={e => {
                  if (e.target.files && e.target.files[0]) {
                    const file = e.target.files[0]
                    setImage(URL.createObjectURL(file))
                    setImageFile(file)
                    setShowPreviewQImage(true)
                  }
                }}
              />

              <Button
                variant="outline"
                className="hover:bg-gray-100 dark:hover:bg-gray-700"
                onClick={() => {
                  const input = document.getElementById(
                    'question-image-input'
                  ) as HTMLInputElement
                  input?.click()
                }}
              >
                {image ? t('Змінити зображення') : t('Завантажити зображення')}
              </Button>

              {image && (
                <Button
                  variant="outline"
                  size="sm"
                  className="hover:bg-gray-100 dark:hover:bg-gray-700"
                  onClick={() => setShowPreviewQImage(prev => !prev)}
                >
                  {showPreviewQImage
                    ? t('Сховати прев’ю')
                    : t('Переглянути прев’ю')}
                </Button>
              )}

              {image && showPreviewQImage && (
                <img
                  src={image}
                  alt="Preview"
                  className="w-full max-w-xs h-auto rounded-md border border-gray-300 mt-2 mx-auto"
                />
              )}
            </div>
          </div>

          <div className="mt-6">
            <Label htmlFor="explanation">{t('Пояснення для питання')}</Label>
            <Textarea
              id="explanation"
              value={explanation || ''}
              onChange={e => setExplanation(e.target.value)}
              placeholder={t('Введіть текст пояснення питання за необхідності')}
              rows={1}
              className="mt-1"
            />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
            <div>
              <Label htmlFor="points">{t('Кількість балів *')}</Label>
              <Input
                id="points"
                type="text"
                value={points ?? ''}
                onChange={e => handleNumericInput(e.target.value, setPoints)}
                placeholder={t(
                  'Кількість балів за правильну відповідь (мінімум 1)'
                )}
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="typeQuestion">{t('Тип питання')}</Label>
              <Select
                value={typeQuestion}
                onValueChange={value =>
                  setTypeQuestion(value as 'choice' | 'yes/no')
                }
              >
                <SelectTrigger className="mt-1">
                  <SelectValue
                    placeholder={
                      typeQuestion === 'choice'
                        ? t('Вибір відповіді')
                        : t('Так / Ні')
                    }
                  />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="choice">{t('Вибір відповіді')}</SelectItem>
                  <SelectItem value="yes/no">{t('Так / Ні')}</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div>
            {typeQuestion === 'choice' ? (
              <div className="mt-6">
                <Label className="mb-2 block">{t('Варіанти відповіді')}</Label>

                {choices.map((choice, index) => (
                  <div
                    key={index}
                    className="flex items-center mb-3 border border-gray-200 dark:border-gray-700 rounded-lg p-2"
                  >
                    <span className="w-6 font-semibold mr-3">
                      {String.fromCharCode(65 + index)}.
                    </span>

                    <Input
                      type="text"
                      value={choice}
                      onChange={e => {
                        const updated = [...choices]
                        updated[index] = e.target.value
                        setChoices(updated)
                      }}
                      placeholder={t(
                        `Варіант ${String.fromCharCode(65 + index)}`
                      )}
                      className="flex-grow"
                    />

                    <input
                      type="checkbox"
                      checked={correctAnswers.includes(choice)}
                      onChange={e => {
                        if (e.target.checked) {
                          setCorrectAnswers([...correctAnswers, choice])
                        } else {
                          setCorrectAnswers(
                            correctAnswers.filter(a => a !== choice)
                          )
                        }
                      }}
                      className="ml-3 w-5 h-5 accent-brand-600 cursor-pointer"
                    />
                  </div>
                ))}

                <div className="flex gap-4 mt-2">
                  <Button
                    variant="outline"
                    className="text-sm"
                    onClick={() => setChoices([...choices, ''])}
                  >
                    + {t('Додати варіант')}
                  </Button>

                  {choices.length > 0 && (
                    <Button
                      variant="outline"
                      className="text-sm text-red-500 border-red-500 hover:bg-red-50"
                      onClick={() => {
                        setChoices(choices.slice(0, -1))
                        setCorrectAnswers(
                          correctAnswers.filter(
                            a => a !== choices[choices.length - 1]
                          )
                        )
                      }}
                    >
                      − {t('Видалити останній')}
                    </Button>
                  )}
                </div>

                <p className="text-sm text-gray-500 mt-3">
                  {t('Оберіть правильну відповідь, поставивши галочку')}
                </p>
              </div>
            ) : (
              <p> jklsadf</p>
            )}
          </div>
        </div>

        <div className="flex justify-center space-x-6 mt-6">
          <div>
            <Button
              className="w-60 bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 text-white"
              variant="outline"
              onClick={handleCancelAddQuestion}
              disabled={isAdding}
            >
              <Undo className="w-4 h-4 mr-2" />
              {t('Скасувати')}
            </Button>
          </div>

          <div>
            <Button
              className="w-60 bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 text-white"
              onClick={handleAddQuestion}
              disabled={isAdding}
            >
              {isAdding ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  {t('Додавання питання...')}
                </>
              ) : (
                <>
                  <Save className="w-4 h-4 mr-2" />
                  {t('Додати питання')}
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
