import { useI18n } from '@/shared/lib'
import { Loader2, Save, Undo } from 'lucide-react'
import React, { type FC, useState } from 'react'
import { Button, type Question } from '@/shared/ui'

interface CreateQuestionTestProps {
  order: number
  onClose: () => void
  onAddTest: (question: Question) => void
}

export const AddQuestionToTestModal: FC<CreateQuestionTestProps> = ({
  order,
  onClose,
  onAddTest,
}) => {
  const { t } = useI18n()
  const [error, setError] = useState<string | null>(null)
  const [isAdding, setIsAdding] = useState(false)
  const [questionText, setQuestionText] = useState<string>('')
  const [points, setPoints] = useState<number>(1)
  const [explanation, setExplanation] = useState<string | null>(null)
  const [correctAnswers, setCorrectAnswers] = useState<string[]>([])
  const [choices, setChoices] = useState<string[]>([])
  const [image, setImage] = useState<string | null>(null)
  const [imageFile, setImageFile] = useState<File | null>(null)

  const handleContentClick = (e: React.MouseEvent) => e.stopPropagation()

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
    onAddTest(newQuestion)
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
        className="bg-white dark:bg-slate-800 rounded-xl w-9/12 max-w-6xl max-h-[80vh]
           overflow-y-auto p-6 relative shadow-2xl
           scrollbar-thin
           scrollbar-thumb-transparent
           hover:scrollbar-thumb-gray-400 dark:hover:scrollbar-thumb-gray-600
           transition-colors"
        onClick={handleContentClick}
      >
        <h2 className="flex items-center justify-center text-2xl font-semibold mb-4">
          {t('Питання')} ${order}
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
                  {t('Додавання...')}
                </>
              ) : (
                <>
                  <Save className="w-4 h-4 mr-2" />
                  {t('Додати')}
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
