import { useI18n } from '@/shared/lib'
import { BookOpen, Plus, Trash2 } from 'lucide-react'
import { Button } from '@/shared/ui/button.tsx'
import React, { useState } from 'react'
import { Card, CardContent, CardTitle } from '@/shared/ui/card.tsx'
import { Label } from '@/shared/ui/label.tsx'
import { Input } from '@/shared/ui/input.tsx'
import { ConfirmModal } from '@/shared/ui/confirm-dialog.tsx'
import { CollapsibleSection } from '@/shared/ui/collapsible-section.tsx'

interface CourseModule {
  orderCourse: number
  title: string
  lessons: ModuleLesson[]
  tests: ModuleTest[]
}

interface CourseTest {
  orderCourse: number
  title: string
}

interface ModuleLesson {
  orderModule: number
  title: string
}

interface ModuleTest {
  orderModule: number
  title: string
}

export interface CreateMTOfCourseProps {
  type: 'module' | 'test'
}

export const CreateMTOfCourse = ({ type }: CreateMTOfCourseProps) => {
  const { t } = useI18n()
  const [courseModules, setCourseModules] = useState<CourseModule[]>([])
  const [courseTests, setCourseTests] = useState<CourseTest[]>([])
  const [isConfirmDelOpen, setIsConfirmDelOpen] = React.useState(false)
  const [deleteTarget, setDeleteTarget] = useState<number | null>(null)

  const handleAddModule = () => {
    setCourseModules(prev => [
      ...prev,
      { orderCourse: prev.length + 1, title: '', lessons: [], tests: [] },
    ])
  }

  const handleAddTest = () => {
    setCourseTests(prev => [
      ...prev,
      { orderCourse: prev.length + 1, title: '' },
    ])
  }

  const handleAddLesson = (moduleOrder: number) => {
    setCourseModules(prev =>
      prev.map(m =>
        m.orderCourse === moduleOrder
          ? {
              ...m,
              lessons: [
                ...m.lessons,
                { orderModule: m.lessons.length + 1, title: '' },
              ],
            }
          : m
      )
    )
  }

  const handleAddModuleTest = (moduleOrder: number) => {
    setCourseModules(prev =>
      prev.map(m =>
        m.orderCourse === moduleOrder
          ? {
              ...m,
              tests: [
                ...m.tests,
                { orderModule: m.tests.length + 1, title: '' },
              ],
            }
          : m
      )
    )
  }

  const handleDelete = (order: number, isModule: boolean) => {
    if (isModule) {
      setCourseModules(prev => prev.filter(m => m.orderCourse !== order))
    } else {
      setCourseTests(prev => prev.filter(t => t.orderCourse !== order))
    }
    setIsConfirmDelOpen(false)
    setDeleteTarget(null)
  }

  const handleDeleteModuleItem = (
    moduleOrder: number,
    itemOrder: number,
    isTest: boolean
  ) => {
    setCourseModules(prev =>
      prev.map(m => {
        if (m.orderCourse !== moduleOrder) return m
        if (isTest) {
          return {
            ...m,
            tests: m.tests.filter(t => t.orderModule !== itemOrder),
          }
        } else {
          return {
            ...m,
            lessons: m.lessons.filter(l => l.orderModule !== itemOrder),
          }
        }
      })
    )
    setIsConfirmDelOpen(false)
    setDeleteTarget(null)
  }

  const handleTitleChange = (
    order: number,
    newTitle: string,
    isModule: boolean
  ) => {
    if (isModule) {
      setCourseModules(prev =>
        prev.map(m => (m.orderCourse === order ? { ...m, title: newTitle } : m))
      )
    } else {
      setCourseTests(prev =>
        prev.map(t => (t.orderCourse === order ? { ...t, title: newTitle } : t))
      )
    }
  }

  const renderDeleteModuleStructureButton = (
    moduleOrder: number,
    itemOrder: number,
    isTest: boolean
  ) => (
    <>
      <Button
        variant="ghost"
        size="icon"
        className="h-8 w-8 text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200"
        onClick={() => {
          setDeleteTarget(itemOrder)
          setIsConfirmDelOpen(true)
        }}
      >
        <Trash2 className="w-4 h-4" />
      </Button>
      <ConfirmModal
        isOpen={isConfirmDelOpen && deleteTarget === itemOrder}
        onClose={() => setIsConfirmDelOpen(false)}
        onConfirm={() => handleDeleteModuleItem(moduleOrder, itemOrder, isTest)}
        title={
          isTest ? t('Видалення тесту модуля') : t('Видалення уроку модуля')
        }
        description={
          isTest
            ? t(
                'Ви впевнені, що хочете видалити цей тест? Цю дію неможливо скасувати.'
              )
            : t(
                'Ви впевнені, що хочете видалити цей урок? Цю дію неможливо скасувати.'
              )
        }
      />
    </>
  )

  const renderDeleteCourseStructureButton = (
    order: number,
    isModule: boolean
  ) => {
    return (
      <>
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8 text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200"
          onClick={() => {
            setDeleteTarget(order)
            setIsConfirmDelOpen(true)
          }}
        >
          <Trash2 className="w-4 h-4" />
        </Button>
        <ConfirmModal
          isOpen={isConfirmDelOpen && deleteTarget === order}
          onClose={() => setIsConfirmDelOpen(false)}
          onConfirm={() => handleDelete(order, isModule)}
          title={isModule ? t('Видалення модуля') : t('Видалення тесту')}
          description={
            isModule
              ? t(
                  'Ви впевнені, що хочете видалити цей модуль? Цю дію неможливо скасувати.'
                )
              : t(
                  'Ви впевнені, що хочете видалити цей тест? Цю дію неможливо скасувати.'
                )
          }
        />
      </>
    )
  }

  return (
    <div className="w-full">
      <CollapsibleSection
        title={type === 'module' ? t('Модулі курсу') : t('Тести курсу')}
      >
        {type === 'module' &&
          courseModules.map(module => (
            <Card
              key={module.orderCourse}
              className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer bg-white dark:bg-slate-800 dark:hover:shadow-gray-700 mt-4"
            >
              <CardTitle className="text-slate-800 dark:text-slate-100 mt-6">
                <div className="flex items-center justify-center relative">
                  <div className="text-center">
                    {t('Модуль')} {module.orderCourse}{' '}
                    {module.title && `- ${module.title}`}
                  </div>
                  <div className="absolute right-0 mr-6">
                    {renderDeleteCourseStructureButton(
                      module.orderCourse,
                      true
                    )}
                  </div>
                </div>
              </CardTitle>
              <CardContent className="p-6 text-slate-700 dark:text-slate-200">
                <Label>{t('Назва модуля *')}</Label>
                <Input
                  value={module.title}
                  onChange={e =>
                    handleTitleChange(module.orderCourse, e.target.value, true)
                  }
                  placeholder={t('Введіть назву модуля')}
                  className="mt-1 mb-4"
                />
                <div>
                  <Card
                    key={'previewLesson-' + module.orderCourse}
                    className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer bg-white dark:bg-slate-600 dark:hover:shadow-gray-500 mt-4"
                  >
                    <CardTitle className="text-slate-800 dark:text-slate-100 my-4">
                      <div className="flex items-center  relative">
                        <div className="left-0 ml-6">{t('Уроки')}</div>
                        <div className="absolute right-0 mr-6">
                          <Button
                            className="w-52"
                            onClick={() => handleAddLesson(module.orderCourse)}
                          >
                            <Plus className="w-4 h-4 mr-2" />
                            {t('Додати урок')}
                          </Button>
                        </div>
                      </div>
                    </CardTitle>
                    <CardContent className="p-6 pt-1 text-slate-700 dark:text-slate-200">
                      {module.lessons.length === 0 ? (
                        <p>{t('Уроки не додано')}</p>
                      ) : (
                        module.lessons.map(lesson => (
                          <Card
                            key={`lesson-${module.orderCourse}-${lesson.orderModule}`}
                            className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer bg-white dark:bg-slate-800 dark:hover:shadow-gray-700 mt-4"
                          >
                            <div className="flex items-center relative">
                              <div
                                key={lesson.orderModule}
                                className="pl-4 m-1 left-0"
                              >
                                {`${t('Урок')} ${lesson.orderModule} ${lesson.title && `- ${lesson.title}`}`}
                              </div>
                              <div className="absolute right-0 pr-4 mb-1">
                                {renderDeleteModuleStructureButton(
                                  module.orderCourse,
                                  lesson.orderModule,
                                  false
                                )}
                              </div>
                            </div>
                          </Card>
                        ))
                      )}
                    </CardContent>
                  </Card>
                  <Card
                    key={'previewTest-' + module.orderCourse}
                    className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer bg-white dark:bg-slate-600 dark:hover:shadow-gray-500 mt-4"
                  >
                    <CardTitle className="text-slate-800 dark:text-slate-100 my-4">
                      <div className="flex items-center  relative">
                        <div className="left-0 ml-6">{t('Тести')}</div>
                        <div className="absolute right-0 mr-6">
                          <Button
                            className="w-52"
                            onClick={() =>
                              handleAddModuleTest(module.orderCourse)
                            }
                          >
                            <Plus className="w-4 h-4 mr-2" />
                            {t('Додати тест у модуль')}
                          </Button>
                        </div>
                      </div>
                    </CardTitle>
                    <CardContent className="p-6 pt-1 text-slate-700 dark:text-slate-200">
                      {module.tests.length === 0 ? (
                        <p>{t('Тести не додано')}</p>
                      ) : (
                        module.tests.map(test => (
                          <Card
                            key={`test-${module.orderCourse}-${test.orderModule}`}
                            className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer bg-white dark:bg-slate-800 dark:hover:shadow-gray-700 mt-4"
                          >
                            <div className="flex items-center relative">
                              <div
                                key={test.orderModule}
                                className="pl-4 m-1 left-0"
                              >
                                {`${t('Тест')} ${test.orderModule} ${test.title && `- ${test.title}`}`}
                              </div>
                              <div className="absolute right-0 pr-4 mb-1">
                                {renderDeleteModuleStructureButton(
                                  module.orderCourse,
                                  test.orderModule,
                                  true
                                )}
                              </div>
                            </div>
                          </Card>
                        ))
                      )}
                    </CardContent>
                  </Card>
                </div>
              </CardContent>
            </Card>
          ))}

        {type === 'test' &&
          courseTests.map(test => (
            <Card
              key={test.orderCourse}
              className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer bg-white dark:bg-slate-800 dark:hover:shadow-gray-700 mt-4"
            >
              <CardTitle className="text-slate-800 dark:text-slate-100 mt-6">
                <div className="flex items-center justify-center relative">
                  <div className="text-center">
                    {t('Тест')} {test.orderCourse}{' '}
                    {test.title && `- ${test.title}`}
                  </div>
                  <div className="absolute right-0 mr-6">
                    {renderDeleteCourseStructureButton(test.orderCourse, false)}
                  </div>
                </div>
              </CardTitle>
              <CardContent className="p-6 text-slate-700 dark:text-slate-200">
                <Label>{t('Назва тесту *')}</Label>
                <Input
                  value={test.title}
                  onChange={e =>
                    handleTitleChange(test.orderCourse, e.target.value, false)
                  }
                  placeholder={t('Введіть назву тесту')}
                  className="mt-1"
                />
              </CardContent>
            </Card>
          ))}

        {((type === 'module' && courseModules.length === 0) ||
          (type === 'test' && courseTests.length === 0)) && (
          <Card
            key={'add-first-' + type}
            className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer bg-white dark:bg-slate-800 dark:hover:shadow-gray-700 mt-4"
          >
            <CardContent className="p-6 text-slate-700 dark:text-slate-200">
              <div className="text-center text-slate-500 mt-6">
                <BookOpen className="w-12 h-12 mx-auto mb-4 text-slate-700 dark:text-slate-200" />
                <p className="text-lg font-medium mb-2 text-slate-600 dark:text-slate-300">
                  {type === 'module'
                    ? t('Модулі не додано')
                    : t('Тести не додано')}
                </p>
                <p className="text-slate-500 dark:text-slate-400">
                  {type === 'module'
                    ? t('Додайте перший модуль для початку створення курсу')
                    : t('Додайте перший тест для початку створення курсу')}
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="flex justify-center mt-6">
          <Button
            onClick={type === 'module' ? handleAddModule : handleAddTest}
            className="w-40 bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 text-white"
          >
            <Plus className="w-4 h-4 mr-2" />
            {type === 'module' ? t('Додати модуль') : t('Додати тест')}
          </Button>
        </div>
      </CollapsibleSection>
    </div>
  )
}
