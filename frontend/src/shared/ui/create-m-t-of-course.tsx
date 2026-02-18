import { useI18n } from '@/shared/lib'
import {
  Award,
  BookOpen,
  ChevronDown,
  ChevronUp,
  Clock,
  Eye,
  FileCheck,
  FileText,
  Plus,
  Repeat,
  Shuffle,
  Trash2,
} from 'lucide-react'
import {
  type BlockData,
  Button,
  Card,
  CardContent,
  CardTitle,
  CollapsibleSection,
  ConfirmModal,
  CreateLessonModal,
  CreateTestModal,
  Input,
  Label,
  type Question,
} from '@/shared/ui'
import React, { useState } from 'react'

export interface CourseStructure {
  type: 'course'
  courseStructure: (ModuleStructure | CourseTest)[]
}

interface ModuleStructure {
  type: 'module'
  order: number
  title: string
  moduleStructure: (Lesson | ModuleTest)[]
}

export interface BaseTest {
  title: string
  description: string
  time_limit: number
  count_attempts: number
  pass_score: number
  random_questions: boolean
  show_correct_answers: boolean
  questions: Question[]
  questions_len?: number
}

export interface ModuleTest extends BaseTest {
  type: 'module-test'
  order: number
}

export interface CourseTest extends BaseTest {
  type: 'course-test'
  order: number
}

export interface Lesson {
  type: 'lesson'
  typeCategory: string
  title: string
  order: number
  moduleOrder: number
  duration: { days: number; hours: number; minutes: number }
  description: string
  contentBlocks: { type: string; data: BlockData }[]
  singleContentData: BlockData
  comment: string
}

export const CreateMTOfCourse = ({
  courseStructure,
  setCourseStructure,
  lessonContentTypes,
}: {
  courseStructure: CourseStructure
  setCourseStructure: React.Dispatch<React.SetStateAction<CourseStructure>>
  lessonContentTypes: { value: string; label: string }[]
}) => {
  const { t } = useI18n()
  const [isConfirmDelOpen, setIsConfirmDelOpen] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState<{
    parentType: 'course' | 'module'
    parentOrder?: number
    itemOrder: number
    type: 'module' | 'course-test' | 'lesson' | 'module-test'
  } | null>(null)
  const [collapsedItems, setCollapsedItems] = useState<Record<string, boolean>>(
    {}
  )
  const [isCreateTestOpen, setIsCreateTestOpen] = useState(false)
  const [testModalData, setTestModalData] = useState<{
    moduleOrder?: number
    order: number
    type: 'module-test' | 'course-test'
  } | null>(null)
  const [isCreateLessonOpen, setIsCreateLessonOpen] = useState(false)
  const [lessonModalData, setLessonModalData] = useState<{
    moduleOrder: number
    order: number
  } | null>(null)

  const handleAddModule = () => {
    setCourseStructure(prev => {
      const nextOrder = prev.courseStructure.length + 1

      return {
        ...prev,
        courseStructure: [
          ...prev.courseStructure,
          {
            type: 'module',
            order: nextOrder,
            title: '',
            moduleStructure: [],
          } satisfies ModuleStructure,
        ],
      }
    })
  }

  const handleAddLesson = (moduleOrder: number) => {
    const module = courseStructure.courseStructure.find(
      item => item.type === 'module' && item.order === moduleOrder
    ) as ModuleStructure | undefined

    if (module) {
      const existingOrders = module.moduleStructure.map(item => item.order)

      const nextOrder =
        existingOrders.length > 0 ? Math.max(...existingOrders) + 1 : 1

      setLessonModalData({ moduleOrder, order: nextOrder })
      setIsCreateLessonOpen(true)
    }
  }

  const handleDelete = (order: number, isModule: boolean) => {
    setCourseStructure(prev => {
      const newStructure = prev.courseStructure
        .filter(item =>
          isModule
            ? !(item.type === 'module' && item.order === order)
            : !(item.type === 'course-test' && item.order === order)
        )
        .map((item, index) => {
          if (item.type === 'module' || item.type === 'course-test') {
            return { ...item, order: index + 1 }
          }
          return item
        })

      return { ...prev, courseStructure: newStructure }
    })

    setIsConfirmDelOpen(false)
    setDeleteTarget(null)
  }

  const handleDeleteModuleItem = (
    moduleOrder: number,
    itemOrder: number,
    isTest: boolean
  ) => {
    setCourseStructure(prev => ({
      ...prev,
      courseStructure: prev.courseStructure.map(item => {
        if (item.type !== 'module' || item.order !== moduleOrder) return item

        const filteredModuleStructure = item.moduleStructure.filter(subItem => {
          if (isTest) {
            return !(
              subItem.type === 'module-test' && subItem.order === itemOrder
            )
          }
          return !(subItem.type === 'lesson' && subItem.order === itemOrder)
        })

        const newModuleStructure = filteredModuleStructure.map(
          (subItem, index) => ({
            ...subItem,
            order: index + 1,
          })
        )

        return { ...item, moduleStructure: newModuleStructure }
      }),
    }))

    setIsConfirmDelOpen(false)
    setDeleteTarget(null)
  }

  const handleTitleChange = (
    parentType: 'course' | 'module',
    order: number,
    newTitle: string,
    type: 'module' | 'course-test' | 'lesson' | 'module-test'
  ) => {
    if (parentType === 'course') {
      setCourseStructure(prev => ({
        ...prev,
        courseStructure: prev.courseStructure.map(item =>
          item.type === type && item.order === order
            ? { ...item, title: newTitle }
            : item
        ),
      }))
    } else if (parentType === 'module') {
      setCourseStructure(prev => ({
        ...prev,
        courseStructure: prev.courseStructure.map(module => {
          if (module.type !== 'module') return module
          return {
            ...module,
            moduleStructure: module.moduleStructure.map(item =>
              item.type === type && item.order === order
                ? { ...item, title: newTitle }
                : item
            ),
          }
        }),
      }))
    }
  }

  interface DeleteButtonProps {
    parentType: 'course' | 'module'
    parentOrder?: number
    itemOrder: number
    type: 'module' | 'course-test' | 'lesson' | 'module-test'
  }

  const renderDeleteButton = ({
    parentType,
    parentOrder,
    itemOrder,
    type,
  }: DeleteButtonProps) => {
    return (
      <Button
        variant="ghost"
        size="icon"
        className="h-8 w-8 text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200"
        onClick={() => {
          setDeleteTarget({
            parentType,
            parentOrder: parentType === 'module' ? parentOrder : undefined,
            itemOrder,
            type,
          })
          setIsConfirmDelOpen(true)
        }}
      >
        <Trash2 className="w-4 h-4" />
      </Button>
    )
  }

  const toggleCollapse = (key: string) => {
    setCollapsedItems(prev => ({ ...prev, [key]: !prev[key] }))
  }

  const renderCollapsedButton = (key: string) => {
    return (
      <Button
        variant="ghost"
        size="icon"
        className="bg-white dark:bg-slate-800 dark:hover:bg-slate-600"
        onClick={() => toggleCollapse(key)}
      >
        {collapsedItems[key] ? <ChevronDown /> : <ChevronUp />}
      </Button>
    )
  }

  const renderTestData = ({ test }: { test: CourseTest | ModuleTest }) => {
    return (
      <div className="flex flex-col gap-3 text-sm">
        <div className="flex items-center font-semibold text-lg text-slate-800 dark:text-slate-100">
          <FileCheck className="w-5 h-5 mr-2 text-brand-600 dark:text-brand-400" />
          {(test.title.length > 150
            ? test.title.slice(0, 150) + '...'
            : test.title) || t('Тест')}
        </div>

        <div className="flex flex-wrap items-center gap-3 text-slate-500 dark:text-slate-400">
          <div className="flex items-center bg-slate-100 dark:bg-slate-700 px-2.5 py-1 rounded-md text-xs font-medium">
            <Clock className="w-3.5 h-3.5 mr-1.5" />
            {test.time_limit} {t('хв')}
          </div>

          <div className="flex items-center bg-slate-100 dark:bg-slate-700 px-2.5 py-1 rounded-md text-xs font-medium">
            <FileText className="w-3.5 h-3.5 mr-1.5" />
            {test.questions.length
              ? test.questions.length
              : test.questions_len}{' '}
            {t('питань')}
          </div>

          <div className="flex items-center bg-slate-100 dark:bg-slate-700 px-2.5 py-1 rounded-md text-xs font-medium">
            <Award className="w-3.5 h-3.5 mr-1.5" />
            {t('мін.')} {test.pass_score}%
          </div>

          <div className="flex items-center bg-slate-100 dark:bg-slate-700 px-2.5 py-1 rounded-md text-xs font-medium">
            <Repeat className="w-3.5 h-3.5 mr-1.5" />
            {test.count_attempts} {t('спроб')}
          </div>
        </div>

        <div className="flex flex-wrap gap-4 text-xs text-slate-500 dark:text-slate-400 mt-1">
          {test.random_questions && (
            <div className="flex items-center text-green-600 dark:text-green-400">
              <Shuffle className="w-3.5 h-3.5 mr-1" />
              {t('Перемішувати')}
            </div>
          )}
          {test.show_correct_answers && (
            <div className="flex items-center text-green-600 dark:text-green-400">
              <Eye className="w-3.5 h-3.5 mr-1" />
              {t('Показувати відповіді')}
            </div>
          )}
        </div>

        {test.description && (
          <div className="mt-1 text-slate-600 dark:text-slate-300 border-l-2 border-slate-200 dark:border-slate-600 pl-3 italic line-clamp-2">
            {test.description}
          </div>
        )}
      </div>
    )
  }

  const renderLessonData = ({ lesson }: { lesson: Lesson }) => {
    const formatDuration = (
      d: string | { days: number; hours: number; minutes: number }
    ) => {
      let days = 0
      let hours = 0
      let minutes = 0

      if (typeof d === 'string') {
        const timeParts = d.split(':').map(Number)
        if (timeParts.length >= 3) {
          days = timeParts[0] || 0
          hours = timeParts[1] || 0
          minutes = timeParts[2] || 0
        } else if (timeParts.length === 2) {
          hours = timeParts[0] || 0
          minutes = timeParts[1] || 0
        }
      } else if (d) {
        days = d.days || 0
        hours = d.hours || 0
        minutes = d.minutes || 0
      }

      const parts = []
      if (days > 0) parts.push(`${days} ${t('дн')}`)
      if (hours > 0) parts.push(`${hours} ${t('год')}`)
      if (minutes > 0) parts.push(`${minutes} ${t('хв')}`)

      return parts.length > 0 ? parts.join(' ') : t('0 хв')
    }

    const getTypeLabel = (category: string) => {
      const foundType = lessonContentTypes.find(type => type.value === category)
      return foundType?.label || category || t('Не вказано')
    }

    return (
      <div className="flex flex-col gap-3 text-sm">
        <div className="flex items-center font-semibold text-lg text-slate-800 dark:text-slate-100">
          <FileText className="w-5 h-5 mr-2 text-brand-600 dark:text-brand-400" />
          {lesson.title.length > 150
            ? lesson.title.slice(0, 150) + '...'
            : lesson.title}
        </div>

        <div className="flex flex-wrap items-center gap-4 text-slate-500 dark:text-slate-400">
          <div className="flex items-center bg-slate-100 dark:bg-slate-700 px-2.5 py-1 rounded-md text-xs font-medium">
            <BookOpen className="w-3 h-3 mr-1.5" />
            {getTypeLabel(lesson.typeCategory)}
          </div>

          <div className="flex items-center text-xs">
            <Clock className="w-3.5 h-3.5 mr-1.5" />
            {formatDuration(lesson.duration)}
          </div>
        </div>

        {lesson.description && (
          <div className="mt-1 text-slate-600 dark:text-slate-300 border-l-2 border-slate-200 dark:border-slate-600 pl-3 italic line-clamp-2">
            {lesson.description}
          </div>
        )}

        {lesson.comment && (
          <div className="text-xs text-slate-400 mt-1">
            <span className="font-semibold">{t('Коментар:')}</span>{' '}
            {lesson.comment}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="w-full">
      <CollapsibleSection title={t('Структура курсу')}>
        {courseStructure.courseStructure.length > 0 ? (
          courseStructure.courseStructure.map(item => {
            const collapseKey = `${item.type}-${item.order}`
            const isCollapsed = collapsedItems[collapseKey] || false
            if (item.type === 'module') {
              return (
                <Card
                  key={'module - ' + item.order}
                  className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer bg-white dark:bg-slate-800 dark:hover:shadow-gray-700 mt-4"
                >
                  <CardTitle className="text-slate-800 dark:text-slate-100 mt-6">
                    <div className="flex items-center justify-center relative">
                      <div className="absolute left-0 ml-6">
                        {renderCollapsedButton(collapseKey)}
                      </div>
                      <div className="text-center">
                        {t('Модуль')} {item.order}{' '}
                        {item.title &&
                          `- ${item.title.length > 30 ? item.title.slice(0, 30) + '...' : item.title}`}
                      </div>
                      <div className="absolute right-0 mr-6">
                        {renderDeleteButton({
                          parentType: 'course',
                          itemOrder: item.order,
                          type: 'module',
                        })}
                      </div>
                    </div>
                  </CardTitle>
                  {!isCollapsed ? (
                    <CardContent className="p-6 text-slate-700 dark:text-slate-200 transition-all duration-300 ease-in-out">
                      <Label>{t('Назва модуля *')}</Label>
                      <Input
                        value={item.title}
                        onChange={e =>
                          handleTitleChange(
                            'course',
                            item.order,
                            e.target.value,
                            'module'
                          )
                        }
                        placeholder={t('Введіть назву модуля')}
                        className="mt-1 mb-4"
                      />

                      <Card
                        key={'lessonOrder or testOrder' + item.order}
                        className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer bg-white dark:bg-slate-600 dark:hover:shadow-gray-500 mt-4"
                      >
                        <CardTitle className="text-slate-800 dark:text-slate-100 my-4">
                          <p className="text-center">{t('Структура модуля')}</p>
                        </CardTitle>
                        <CardContent className="p-6 pt-1 text-slate-700 dark:text-slate-200">
                          {item.moduleStructure.length === 0 ? (
                            <Card
                              key={'add-first-lesson-or-test'}
                              className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer bg-white dark:bg-slate-800 dark:hover:shadow-gray-700"
                            >
                              <CardContent className="text-slate-700 dark:text-slate-200">
                                <div className="text-center text-slate-500 mt-6">
                                  <BookOpen className="w-10 h-10 mx-auto mb-2 text-slate-700 dark:text-slate-200" />
                                  <p className="text-slate-500 dark:text-slate-400">
                                    {t(
                                      'Додавайте уроки та тест для цього модуля'
                                    )}
                                  </p>
                                </div>
                              </CardContent>
                            </Card>
                          ) : (
                            item.moduleStructure.map(moduleElem => {
                              const moduleElemCollapseKey = `${moduleElem.type}-${moduleElem.order}-${item.order}`
                              const ismoduleElemCollapsed =
                                collapsedItems[moduleElemCollapseKey] || false
                              return (
                                <Card
                                  key={`moduleElem-courseElem-${moduleElem.order}-${item.order}`}
                                  className="text-base overflow-hidden hover:shadow-md transition-shadow cursor-pointer bg-white dark:bg-slate-800 dark:hover:shadow-slate-700 mt-3 border border-slate-200 dark:border-slate-700"
                                >
                                  <div className="flex items-center relative mt-4">
                                    <div className="absolute left-0 ml-6">
                                      {renderCollapsedButton(
                                        moduleElemCollapseKey
                                      )}
                                    </div>
                                    <div
                                      key={'moduleElem' + moduleElem.order}
                                      className="pl-4 ml-16"
                                    >
                                      {moduleElem.type === 'lesson'
                                        ? `${t('Урок')} ${moduleElem.order} ${moduleElem.title && `- ${moduleElem.title.length > 30 ? moduleElem.title.slice(0, 30) + '...' : moduleElem.title}`}`
                                        : `${t('Тест')} ${moduleElem.order} ${moduleElem.title && `- ${moduleElem.title.length > 30 ? moduleElem.title.slice(0, 30) + '...' : moduleElem.title}`}`}
                                    </div>
                                    <div className="absolute right-0 pr-4 mb-1">
                                      {renderDeleteButton({
                                        parentType: 'module',
                                        parentOrder: item.order,
                                        itemOrder: moduleElem.order,
                                        type:
                                          moduleElem.type === 'lesson'
                                            ? 'lesson'
                                            : 'module-test',
                                      })}
                                    </div>
                                  </div>

                                  {!ismoduleElemCollapsed ? (
                                    <CardContent className="p-6 text-slate-700 dark:text-slate-200">
                                      {moduleElem.type === 'module-test'
                                        ? renderTestData({ test: moduleElem })
                                        : renderLessonData({
                                            lesson: moduleElem,
                                          })}
                                    </CardContent>
                                  ) : (
                                    <p className="pb-4" />
                                  )}
                                </Card>
                              )
                            })
                          )}

                          <div className="flex justify-center mt-6">
                            <Button
                              className="mr-3 w-52"
                              onClick={() => handleAddLesson(item.order)}
                            >
                              <Plus className="w-4 h-4 mr-2" />
                              {t('Додати урок')}
                            </Button>
                            <Button
                              className="ml-3 w-52"
                              onClick={() => {
                                const structureOrders =
                                  item.moduleStructure.map(i => i.order)
                                const nextOrder =
                                  structureOrders.length > 0
                                    ? Math.max(...structureOrders) + 1
                                    : 1

                                setTestModalData({
                                  moduleOrder: item.order,
                                  order: nextOrder,
                                  type: 'module-test',
                                })
                                setIsCreateTestOpen(true)
                              }}
                            >
                              <Plus className="w-4 h-4 mr-2" />
                              {t('Додати тест у модуль')}
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    </CardContent>
                  ) : (
                    <p className="pb-6" />
                  )}
                </Card>
              )
            } else {
              const testCollapseKey = `course-test-${item.order}`
              const isTestCollapsed = collapsedItems[testCollapseKey] || false
              return (
                <Card
                  key={'ret-item-order' + item.order}
                  className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer bg-white dark:bg-slate-800 dark:hover:shadow-gray-700 mt-4"
                >
                  <CardTitle className="text-slate-800 dark:text-slate-100 mt-6">
                    <div className="flex items-center justify-center relative">
                      <div className="absolute left-0 ml-6">
                        {renderCollapsedButton(testCollapseKey)}
                      </div>
                      <div className="text-center">
                        {t('Тест')} {item.order}{' '}
                        {item.title &&
                          `- ${item.title.length > 30 ? item.title.slice(0, 30) + '...' : item.title}`}
                      </div>
                      <div className="absolute right-0 mr-6">
                        {renderDeleteButton({
                          parentType: 'course',
                          itemOrder: item.order,
                          type: 'course-test',
                        })}
                      </div>
                    </div>
                  </CardTitle>
                  {!isTestCollapsed ? (
                    <CardContent className="p-6 text-slate-700 dark:text-slate-200">
                      {renderTestData({ test: item })}
                    </CardContent>
                  ) : (
                    <p className="pb-6" />
                  )}
                </Card>
              )
            }
          })
        ) : (
          <Card
            key={'add-first-module-or-test'}
            className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer bg-white dark:bg-slate-800 dark:hover:shadow-gray-700 mt-4"
          >
            <CardContent className="p-6 text-slate-700 dark:text-slate-200">
              <div className="text-center text-slate-500 mt-6">
                <BookOpen className="w-12 h-12 mx-auto mb-4 text-slate-700 dark:text-slate-200" />
                <p className="text-lg font-medium mb-2 text-slate-600 dark:text-slate-300">
                  {t('Почніть створення вашого курсу')}
                </p>
                <p className="text-slate-500 dark:text-slate-400">
                  {t(
                    'Додайте перший модуль або тест для початку створення курсу'
                  )}
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        <ConfirmModal
          isOpen={isConfirmDelOpen}
          onClose={() => setIsConfirmDelOpen(false)}
          onConfirm={() => {
            if (!deleteTarget) return
            const { parentType, parentOrder, itemOrder, type } = deleteTarget

            if (parentType === 'course') {
              handleDelete(itemOrder, type === 'module')
            } else if (parentType === 'module' && parentOrder !== undefined) {
              handleDeleteModuleItem(
                parentOrder,
                itemOrder,
                type === 'module-test'
              )
            }

            setIsConfirmDelOpen(false)
            setDeleteTarget(null)
          }}
          title={
            deleteTarget
              ? deleteTarget.type === 'module'
                ? t('Видалення модуля')
                : deleteTarget.type === 'course-test'
                  ? t('Видалення тесту')
                  : deleteTarget.type === 'lesson'
                    ? t('Видалення уроку модуля')
                    : t('Видалення тесту модуля')
              : ''
          }
          description={
            deleteTarget
              ? t(
                  'Ви впевнені, що хочете видалити цей елемент? Цю дію неможливо скасувати.'
                )
              : ''
          }
        />

        <div className="flex justify-center mt-6">
          <Button
            onClick={handleAddModule}
            className="mr-3 w-40 bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 text-white"
          >
            <Plus className="w-4 h-4 mr-2" />
            {t('Додати модуль')}
          </Button>
          <Button
            onClick={() => {
              const nextOrder = courseStructure.courseStructure.length + 1
              setTestModalData({ order: nextOrder, type: 'course-test' })
              setIsCreateTestOpen(true)
            }}
            className="ml-3 w-40 bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 text-white"
          >
            <Plus className="w-4 h-4 mr-2" />
            {t('Додати тест')}
          </Button>
        </div>

        {isCreateTestOpen && testModalData && (
          <CreateTestModal
            order={testModalData.order}
            type={testModalData.type}
            onClose={() => setIsCreateTestOpen(false)}
            onAddTest={newTest => {
              if (newTest.type === 'course-test') {
                setCourseStructure(prev => ({
                  ...prev,
                  courseStructure: [
                    ...prev.courseStructure,
                    newTest as CourseTest,
                  ],
                }))
              } else if (newTest.type === 'module-test') {
                setCourseStructure(prev => ({
                  ...prev,
                  courseStructure: prev.courseStructure.map(mod => {
                    if (
                      mod.type === 'module' &&
                      testModalData.moduleOrder !== undefined &&
                      mod.order === testModalData.moduleOrder
                    ) {
                      return {
                        ...mod,
                        moduleStructure: [
                          ...mod.moduleStructure,
                          newTest as ModuleTest,
                        ],
                      }
                    }
                    return mod
                  }),
                }))
              }
              setIsCreateTestOpen(false)
            }}
          />
        )}

        {isCreateLessonOpen && lessonModalData && (
          <CreateLessonModal
            order={lessonModalData.order}
            moduleOrder={lessonModalData.moduleOrder}
            onClose={() => setIsCreateLessonOpen(false)}
            lessonContentTypes={lessonContentTypes}
            onAddLesson={lesson => {
              if (lesson.type === 'lesson') {
                setCourseStructure(prev => ({
                  ...prev,
                  courseStructure: prev.courseStructure.map(mod => {
                    if (
                      mod.type === 'module' &&
                      mod.order === lessonModalData.moduleOrder
                    ) {
                      return {
                        ...mod,
                        moduleStructure: [
                          ...mod.moduleStructure,
                          lesson as unknown as Lesson,
                        ],
                      }
                    }
                    return mod
                  }),
                }))
              }
              setIsCreateLessonOpen(false)
            }}
          />
        )}
      </CollapsibleSection>
    </div>
  )
}
