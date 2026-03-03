import { useI18n } from '@/shared/lib'
import { Loader2, Minus, Plus, Save, Undo } from 'lucide-react'
import React, { type FC, useEffect, useState } from 'react'
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
import { disablePageScroll, enablePageScroll } from '@/shared/scroll'

interface CreateQuestionTestProps {
  order: number
  initialData?: Question
  onClose: () => void
  onAddQuestion: (question: Question) => void
}

export const AddQuestionToTestModal: FC<CreateQuestionTestProps> = ({
  order,
  initialData,
  onClose,
  onAddQuestion,
}) => {
  const { t } = useI18n()
  const [error, setError] = useState<string | null>(null)
  const [isAdding, setIsAdding] = useState(false)

  const [questionText, setQuestionText] = useState<string>(
    initialData?.questionText || ''
  )
  const [points, setPoints] = useState<number | undefined>(initialData?.points)
  const [explanation, setExplanation] = useState<string | null>(
    initialData?.explanation || null
  )
  const [correctAnswers, setCorrectAnswers] = useState<string[]>(
    initialData?.correctAnswers || []
  )
  const [choices, setChoices] = useState<string[]>(initialData?.choices || [])
  const [image, setImage] = useState<string | null>(initialData?.image || null)
  const [imageFile, setImageFile] = useState<File | null>(
    initialData?.imageFile || null
  )

  const initialType =
    initialData?.choices.includes('yes') &&
    initialData?.choices.includes('no') &&
    initialData.choices.length === 2
      ? 'yes/no'
      : 'choice'
  const [typeQuestion, setTypeQuestion] = useState<'choice' | 'yes/no'>(
    initialType
  )

  const [showPreviewQImage, setShowPreviewQImage] = useState<boolean>(
    !!initialData?.image
  )

  useEffect(() => {
    disablePageScroll()
    return () => enablePageScroll()
  }, [])

  useEffect(() => {
    if (typeQuestion === 'yes/no') {
      setChoices(['yes', 'no'])
    }
    if (typeQuestion === 'choice' && !initialData) {
      setChoices([])
      setCorrectAnswers([])
    }
  }, [typeQuestion, initialData])

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
      imageFile,
    }

    setIsAdding(true)
    await new Promise(resolve => setTimeout(resolve, 500))
    onAddQuestion(newQuestion)
    setIsAdding(false)
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
          {initialData ? t('Редагування питання') : t('Питання')} {order}
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
                placeholder={t('Кількість балів за правильну відповідь')}
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

          <div className="mt-6">
            <Label className="mb-3 flex items-center justify-center text-lg">
              {t('Варіанти відповіді')}
            </Label>

            {typeQuestion === 'choice' ? (
              <>
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

                <div className="flex items-center justify-center">
                  <div className="flex gap-4 mt-3">
                    {choices.length > 0 && (
                      <Button
                        variant="outline"
                        className="text-sm hover:bg-gray-100 dark:hover:bg-gray-700 w-48"
                        onClick={() => {
                          setChoices(choices.slice(0, -1))
                          setCorrectAnswers(
                            correctAnswers.filter(
                              a => a !== choices[choices.length - 1]
                            )
                          )
                        }}
                      >
                        <Minus className="w-4 h-4 mr-2" />
                        {t('Видалити останній')}
                      </Button>
                    )}

                    <Button
                      className="w-48 text-sm text-white bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 "
                      onClick={() => setChoices([...choices, ''])}
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      {t('Додати варіант')}
                    </Button>
                  </div>
                </div>
                <p className="flex items-center justify-center text-sm text-gray-500 mt-3">
                  {t('Оберіть правильну відповідь, поставивши галочку')}
                </p>
              </>
            ) : (
              <div className="flex flex-col items-center mt-4 space-y-3">
                <Label className="text-lg">
                  {t('Оберіть правильну відповідь')}
                </Label>
                <div className="flex gap-6">
                  <label className="flex items-center space-x-2">
                    <input
                      type="radio"
                      name="yesno"
                      value="yes"
                      checked={correctAnswers.includes('yes')}
                      onChange={() => setCorrectAnswers(['yes'])}
                      className="w-5 h-5 accent-brand-600 cursor-pointer"
                    />
                    <span>{t('Так')}</span>
                  </label>
                  <label className="flex items-center space-x-2">
                    <input
                      type="radio"
                      name="yesno"
                      value="no"
                      checked={correctAnswers.includes('no')}
                      onChange={() => setCorrectAnswers(['no'])}
                      className="w-5 h-5 accent-brand-600 cursor-pointer"
                    />
                    <span>{t('Ні')}</span>
                  </label>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="flex justify-center space-x-6 mt-6">
          <div>
            <Button
              className="w-60 hover:bg-gray-100 dark:hover:bg-gray-700"
              variant="outline"
              onClick={() => onClose()}
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
                  {t('Збереження...')}
                </>
              ) : (
                <>
                  <Save className="w-4 h-4 mr-2" />
                  {initialData ? t('Оновити питання') : t('Зберегти питання')}
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
