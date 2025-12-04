import React, { type FC, useMemo, useState } from 'react'
import { useI18n } from '@/shared/lib'
import {
  Button,
  Card,
  ConfirmModal,
  Input,
  Label,
  type Lesson,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Textarea,
} from '@/shared/ui'
import {
  ChevronDown,
  ChevronUp,
  Loader2,
  PlusSquareIcon,
  Save,
  Trash2,
  Undo,
} from 'lucide-react'
import { disablePageScroll, enablePageScroll } from '@/shared/scroll'
import CourseDurationPicker from '@/shared/ui/duration-picker.tsx'
import { getLessonFields } from '@/features/lesson-type-fields'

interface FileContentData {
  file: File
  previewUrl: string
}

interface CodeContentData {
  language: string
  code: string
}

export type BlockData = string | FileContentData | CodeContentData | null

interface ContentBlock {
  id: string
  type: string
  data: BlockData
}

interface DynamicFieldProps {
  value?: BlockData
  onChange: (value: BlockData) => void
  onError?: (hasError: boolean) => void
  initialValue?: string
  initialCode?: string
  initialLanguage?: string
}

interface CreateLessonModalProps {
  order: number
  onClose: () => void
  lessonContentTypes: { value: string; label: string }[]
  onAddLesson: (lesson: Lesson) => void
}

export const CreateLessonModal: FC<CreateLessonModalProps> = ({
  order,
  onClose,
  lessonContentTypes,
  onAddLesson,
}) => {
  const { t } = useI18n()
  const [error, setError] = useState<string | null>(null)
  const [isAdding, setIsAdding] = useState(false)
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState<string>('')
  const [comment, setComment] = useState<string>('')
  const [showCanselModal, setShowCanselModal] = useState(false)

  const [lessonStateCategoryType, setLessonStateCategoryType] =
    useState<string>('custom')
  const [customTypeContent, setCustomTypeContent] = useState<string>('')
  const [lessonDuration, setLessonDuration] = useState({
    days: 0,
    hours: 0,
    minutes: 0,
  })
  const [blockErrors, setBlockErrors] = useState<Record<string, boolean>>({})

  const Fields = getLessonFields(
    lessonStateCategoryType
  ) as React.ComponentType<DynamicFieldProps> | null

  const [extraData, setExtraData] = useState<BlockData>(null)
  const [customContentBlocks, setCustomContentBlocks] = useState<
    ContentBlock[]
  >([])
  const [collapsedQuestions, setCollapsedQuestions] = useState<
    Record<number, boolean>
  >({})

  React.useEffect(() => {
    disablePageScroll()
    return () => enablePageScroll()
  }, [])

  const hasValidationErrors = useMemo(() => {
    return Object.values(blockErrors).some(isError => isError)
  }, [blockErrors])

  const handleBlockError = (blockId: string, hasError: boolean) => {
    setBlockErrors(prev => {
      if (prev[blockId] === hasError) return prev
      return { ...prev, [blockId]: hasError }
    })
  }

  const handleContentClick = (e: React.MouseEvent) => e.stopPropagation()

  const renderCustomTypeFields = () => {
    return (
      <div className="mt-6">
        <Label htmlFor="lessonCustomType">
          {t('Оберіть тип контенту який хочете додати')}
        </Label>
        <Select
          value={customTypeContent}
          onValueChange={value => setCustomTypeContent(value)}
        >
          <SelectTrigger className="mt-1">
            <SelectValue placeholder={t('Оберіть тип контенту')} />
          </SelectTrigger>
          <SelectContent>
            {lessonTypesArray.map(customType => (
              <SelectItem key={customType.value} value={customType.value}>
                {customType.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    )
  }

  const handleAddContentToCustomType = () => {
    if (!customTypeContent) return

    setCustomContentBlocks(prev => [
      ...prev,
      { id: crypto.randomUUID(), type: customTypeContent, data: null },
    ])

    setCustomTypeContent('')
  }

  const handleRemoveBlock = (indexToRemove: number) => {
    const blockToRemove = customContentBlocks[indexToRemove]

    if (blockToRemove) {
      setBlockErrors(prev => {
        const newState = { ...prev }
        delete newState[blockToRemove.id]
        return newState
      })
    }

    setCustomContentBlocks(prev =>
      prev.filter((_, index) => index !== indexToRemove)
    )

    setCollapsedQuestions(prev => {
      const newState = { ...prev }
      delete newState[indexToRemove]
      return newState
    })
  }

  const checkData = () => {
    if (!title.trim()) {
      setError(t('Будь ласка, введіть назву уроку.'))
      return false
    }

    if (
      lessonDuration.days === 0 &&
      lessonDuration.hours === 0 &&
      lessonDuration.minutes === 0
    ) {
      setError(t('Будь ласка, встановіть орієнтовний час проходження уроку.'))
      return false
    }

    if (!description.trim()) {
      setError(t('Будь ласка, введіть опис уроку.'))
      return false
    }

    if (lessonStateCategoryType === 'custom') {
      let totalTextLength: number = 0

      if (customContentBlocks.length === 0) {
        setError(t('Будь ласка, додайте хоча б один блок контенту.'))
        return false
      }

      for (let i = 0; i < customContentBlocks.length; i++) {
        const block = customContentBlocks[i]

        if (block.data === null && !blockErrors[block.id]) {
          setError(t('Заповніть всі необхідні дані'))
          return false
        }

        if (block.data) {
          if (typeof block.data === 'string') {
            totalTextLength += block.data.length
          } else if (typeof block.data === 'object' && 'code' in block.data) {
            totalTextLength += (block.data as CodeContentData).code.length
          }
        }
      }

      if (totalTextLength > 5000) {
        setError(
          t(
            'Довжина текстового контенту не повинна перевищувати 5000 символів.'
          )
        )
        return false
      }
    } else {
      if (extraData === null) {
        setError(t('Будь ласка, заповніть дані для вибраного типу контенту.'))
        return false
      }
      if (comment === '' || comment.trim() === '') {
        setError(t('Будь ласка, додайте коментар до завдання.'))
        return false
      }
    }

    setError(null)
    return true
  }

  const handleAddLesson = () => {
    if (hasValidationErrors) {
      return
    }

    const isValid = checkData()
    if (!isValid) {
      return
    }

    setIsAdding(true)
    setError(null)

    const lessonData = {
      title,
      typeCategory: lessonStateCategoryType,
      duration: lessonDuration,
      description,
      contentBlocks: customContentBlocks.map(block => ({
        type: block.type,
        data: block.data,
      })),
      singleContentData: extraData,
      comment,
    }

    console.log('--- ЗІБРАНІ ДАНІ УРОКУ ---', lessonData)
    onAddLesson(lessonData as Lesson)
  }

  const resetForm = () => {
    setTitle('')
    setDescription('')
    setComment('')
    setLessonStateCategoryType('custom')
    setCustomTypeContent('')
    setLessonDuration({ days: 0, hours: 0, minutes: 0 })
    setBlockErrors({})
    setExtraData(null)
    setCustomContentBlocks([])
    setCollapsedQuestions({})
    setError(null)
    setIsAdding(false)
  }

  const handleCancelCreateLesson = () => {
    const hasData =
      title.trim() ||
      description.trim() ||
      customContentBlocks.length > 0 ||
      extraData

    if (hasData) {
      setShowCanselModal(true)
    } else handleCancelAddLesson()
  }

  const handleCancelAddLesson = () => {
    resetForm()
    onClose()
  }

  const buildLessonJson: Record<string, string> = {
    video: t('Відео'),
    image: t('Фото'),
    link: t('Посилання'),
    code: t('Код'),
    text: t('Текст'),
    assignment: t('Завдання'),
    live: t('Запрошення на зустріч'),
  }

  const lessonTypesArray = Object.entries(buildLessonJson).map(
    ([value, label]) => ({
      value,
      label,
    })
  )

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
          {`${t('Урок')} ${order}${title ? ` - ${title.length > 30 ? title.slice(0, 30) + '...' : title}` : ''}`}
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
              <Label htmlFor="lessonTitle">{t('Назва уроку *')}</Label>
              <Input
                id="lessonTitle"
                value={title}
                onChange={e => setTitle(e.target.value)}
                placeholder={t('Введіть назву уроку')}
                className="mt-1"
              />
            </div>
            <div>
              <Label htmlFor="lessonType">{t('Тип контенту *')}</Label>
              <Select
                value={lessonStateCategoryType}
                onValueChange={value => setLessonStateCategoryType(value)}
              >
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder={t('Оберіть тип контенту')} />
                </SelectTrigger>
                <SelectContent>
                  {lessonContentTypes.map(lessonType => (
                    <SelectItem key={lessonType.value} value={lessonType.value}>
                      {lessonType.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="mt-6">
            <CourseDurationPicker
              value={lessonDuration}
              onChange={setLessonDuration}
              maxDays={3}
              inputtedText={t('Встановіть орієнтовний час проходження уроку *')}
            />
          </div>
          <div className="mt-6">
            <Label htmlFor="lessonDescription">{t('Опис уроку *')}</Label>
            <Textarea
              id="lessonDescription"
              value={description}
              onChange={e => setDescription(e.target.value)}
              placeholder={t('Короктко опишіть урок...')}
              rows={4}
              className="mt-1"
            />
          </div>
          <div className="my-4 flex-grow h-0.5 bg-gray-400 dark:bg-gray-600" />

          <div className="mt-6">
            {lessonStateCategoryType === 'custom' ? (
              <>
                <div className="mt-6 space-y-6">
                  {customContentBlocks.map((block, index) => {
                    const FieldsComponent = getLessonFields(
                      block.type
                    ) as React.ComponentType<DynamicFieldProps> | null
                    const isVisible = collapsedQuestions[index] ?? true

                    const codeData =
                      typeof block.data === 'object' &&
                      block.data !== null &&
                      'code' in block.data
                        ? (block.data as CodeContentData)
                        : null

                    return (
                      <Card
                        key={block.id}
                        className={`px-4 rounded-lg overflow-hidden hover:shadow-lg transition-shadow bg-white dark:bg-slate-600 dark:hover:shadow-gray-700 mt-4`}
                      >
                        <div
                          className="flex justify-between items-center p-3 cursor-pointer"
                          onClick={() => toggleQuestionCollapse(index)}
                        >
                          <div className="flex items-center space-x-3">
                            {isVisible ? (
                              <ChevronUp className="w-5 h-5" />
                            ) : (
                              <ChevronDown className="w-5 h-5" />
                            )}
                            <h3 className="text-lg font-semibold">
                              {index + 1}.{' '}
                              {buildLessonJson[block.type] || block.type}
                            </h3>
                          </div>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200 z-10"
                            onClick={e => {
                              e.stopPropagation()
                              handleRemoveBlock(index)
                            }}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>

                        {FieldsComponent && (
                          <div
                            className="mb-4 py-0 cursor-default"
                            onClick={e => e.stopPropagation()}
                            style={{ display: isVisible ? 'block' : 'none' }}
                          >
                            <FieldsComponent
                              value={block.data}
                              onChange={(newData: BlockData) => {
                                setCustomContentBlocks(prev =>
                                  prev.map((b, i) =>
                                    i === index ? { ...b, data: newData } : b
                                  )
                                )
                              }}
                              onError={(hasError: boolean) =>
                                handleBlockError(block.id, hasError)
                              }
                              initialValue={
                                typeof block.data === 'string'
                                  ? block.data
                                  : undefined
                              }
                              initialCode={codeData?.code}
                              initialLanguage={codeData?.language}
                            />
                          </div>
                        )}
                      </Card>
                    )
                  })}
                </div>

                {renderCustomTypeFields()}

                <div className="flex justify-center space-x-6 mt-6">
                  <div>
                    <Button
                      className="w-60 bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 text-white"
                      variant="outline"
                      onClick={handleAddContentToCustomType}
                      disabled={isAdding}
                    >
                      <PlusSquareIcon className="w-4 h-4 mr-2" />
                      {t('Дадати контент')}
                    </Button>
                  </div>
                </div>
              </>
            ) : (
              <>
                {Fields && (
                  <Fields
                    value={extraData}
                    onChange={setExtraData}
                    onError={hasError =>
                      handleBlockError('single-content', hasError)
                    }
                  />
                )}

                <div className="mt-6">
                  <Label htmlFor="lessonComment">{t('Коментар*')}</Label>
                  <Textarea
                    id="lessonComment"
                    value={comment}
                    onChange={e => setComment(e.target.value)}
                    placeholder={t('Додайте коментар до завдання...')}
                    rows={4}
                    className="mt-1"
                  />
                </div>
              </>
            )}
          </div>
          <div className="my-4 flex-grow h-0.5 bg-gray-400 dark:bg-gray-600" />
        </div>

        <div className="flex justify-center space-x-6 mt-6">
          <div>
            <Button
              className="w-60 hover:bg-gray-100 dark:hover:bg-gray-700"
              variant="outline"
              onClick={handleCancelCreateLesson}
              disabled={isAdding}
            >
              <Undo className="w-4 h-4 mr-2" />
              {t('Скасувати')}
            </Button>
          </div>

          <div>
            <Button
              className="w-60 bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 text-white"
              onClick={handleAddLesson}
              disabled={isAdding || hasValidationErrors}
            >
              {isAdding ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  {t('Збереження уроку...')}
                </>
              ) : (
                <>
                  <Save className="w-4 h-4 mr-2" />
                  {t('Зберегти урок')}
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
      {showCanselModal && (
        <ConfirmModal
          isOpen={showCanselModal}
          onConfirm={handleCancelAddLesson}
          onClose={() => setShowCanselModal(false)}
          title={t('Ви дійсно бажаєте скасувати створення уроку?')}
          description={t('Всі внесені дані будуть втрачені')}
          buttonText={t('Підтвердити')}
        />
      )}
    </div>
  )
}
