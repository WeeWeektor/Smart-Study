import React, { type FC, useState } from 'react'
import { useI18n } from '@/shared/lib'
import {
  Button,
  Card,
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
  Undo,
} from 'lucide-react'
import { disablePageScroll, enablePageScroll } from '@/shared/scroll'
import CourseDurationPicker from '@/shared/ui/duration-picker.tsx'
import { getLessonFields } from '@/features/lesson-type-fields'

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
  const [lessonStateCategoryType, setLessonStateCategoryType] =
    useState<string>('custom')
  const [customTypeContent, setCustomTypeContent] = useState<string>('')
  const [lessonDuration, setLessonDuration] = useState({
    days: 0,
    hours: 0,
    minutes: 0,
  })
  const Fields = getLessonFields(lessonStateCategoryType)
  const [extraData, setExtraData] = useState<unknown>(null)
  const [customContentBlocks, setCustomContentBlocks] = useState<
    { type: string; data: unknown }[]
  >([])
  const [collapsedQuestions, setCollapsedQuestions] = useState<
    Record<number, boolean>
  >({})

  React.useEffect(() => {
    disablePageScroll()
    return () => enablePageScroll()
  }, [])

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
      { type: customTypeContent, data: {} },
    ])

    setCustomTypeContent('')
  }

  const handleAddLesson = () => {
    setIsAdding(true)
    console.log('Adding lesson...')
  }

  const handleCancelAddLesson = () => {
    console.log('Canceling lesson...')
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
                    const FieldsComponent = getLessonFields(block.type)
                    const isCollapsed = collapsedQuestions[index] ?? true
                    return (
                      <Card
                        key={index}
                        className="px-4 rounded-lg overflow-hidden hover:shadow-lg transition-shadow cursor-pointer bg-white dark:bg-slate-600 dark:hover:shadow-gray-700 mt-4"
                      >
                        <div
                          className="flex justify-between items-center p-3 cursor-pointer"
                          onClick={() => toggleQuestionCollapse(index)}
                        >
                          <div className="flex items-center space-x-3">
                            {isCollapsed ? (
                              <ChevronUp className="w-5 h-5" />
                            ) : (
                              <ChevronDown className="w-5 h-5" />
                            )}
                            <h3 className="text-lg font-semibold">
                              {index + 1}.{' '}
                              {buildLessonJson[block.type] || block.type}
                            </h3>
                          </div>
                        </div>
                        {isCollapsed && FieldsComponent && (
                          <div className="mb-4 py-0">
                            <FieldsComponent
                              value={block.data}
                              onChange={(newData: unknown) => {
                                setCustomContentBlocks(prev =>
                                  prev.map((b, i) =>
                                    i === index ? { ...b, data: newData } : b
                                  )
                                )
                              }}
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
                {Fields && <Fields value={extraData} onChange={setExtraData} />}

                <div className="mt-6">
                  <Label htmlFor="lessonComment">{t('Коментар')}</Label>
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
              onClick={handleCancelAddLesson}
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
              disabled={isAdding}
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
    </div>
  )
}
