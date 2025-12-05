import { useI18n } from '@/shared/lib'
import {
  Alert,
  AlertDescription,
  Button,
  Card,
  CardContent,
  CollapsibleSection,
  ConfirmModal,
  type CourseStructure,
  CreateMTOfCourse,
  ErrorProfile,
  Input,
  Label,
  LoadingProfile,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Textarea,
} from '@/shared/ui'
import { CourseHeader } from '@/widgets/course'
import { Sidebar } from '@/widgets/layout'
import {
  AlertCircle,
  ArrowLeft,
  Globe,
  Loader2,
  Save,
  Undo,
} from 'lucide-react'
import { useProfileData } from '@/shared/hooks'
import { useEffect, useState } from 'react'
import { useChoicesData } from '@/shared/hooks/useChoiceData'
import { useNavigate } from 'react-router-dom'
import CourseDurationPicker from '@/shared/ui/duration-picker.tsx'
import { createCourseService } from '@/features/course'

interface Option {
  value: string
  label: string
}

const CreateCourse = () => {
  const { t } = useI18n()
  const navigate = useNavigate()
  const { profileData, loading, error, refreshProfile } = useProfileData()
  const {
    choicesData,
    loading: choicesLoading,
    error: choicesError,
    refreshChoices,
  } = useChoicesData()
  const [createCourseError, setCreateCourseError] = useState<string>('')
  const [categories, setCategories] = useState<Option[]>([])
  const [levels, setLevels] = useState<Option[]>([])
  const [categoryLessonType, setCategoryLessonType] = useState<Option[]>([])
  const [isSaving, setIsSaving] = useState(false)
  const [courseStateTitle, setCourseStateTitle] = useState<string>('')
  const [courseStateDescription, setCourseStateDescription] =
    useState<string>('')
  const [courseStateCategory, setCourseStateCategory] = useState<string>('')
  const [courseStateImage, setCourseStateImage] = useState<string>('')
  const [courseStateImageFile, setCourseStateImageFile] = useState<File | null>(
    null
  )
  const [courseStateLevel, setCourseStateLevel] = useState<string>('')
  const [courseStateIsPublished, setCourseStateIsPublished] =
    useState<boolean>(false)
  const [courseStateTimeToComplete, setCourseStateTimeToComplete] = useState({
    days: 0,
    hours: 0,
    minutes: 0,
  })
  const [courseStateLanguage, setCourseStateLanguage] = useState<string>('')
  const [showPreview, setShowPreview] = useState<boolean>(false)
  const [showCanselModal, setShowCanselModal] = useState(false)
  const [showPublishModal, setShowPublishModal] = useState(false)
  const [courseStructure, setCourseStructure] = useState<CourseStructure>({
    type: 'course',
    courseStructure: [],
  })

  useEffect(() => {
    if (choicesData) {
      const categoriesData: Option[] = Object.entries(
        choicesData.category[0]
      ).map(([key, label]) => ({
        value: key,
        label,
      }))
      const levelsData: Option[] = Object.entries(choicesData.levels[0]).map(
        ([key, label]) => ({
          value: key,
          label,
        })
      )
      const lessonTypesData: Option[] = Object.entries(
        choicesData.lesson_content_types[0]
      ).map(([key, label]) => ({
        value: key,
        label,
      }))

      setCategories(categoriesData)
      setLevels(levelsData)
      setCategoryLessonType(lessonTypesData)
    }
  }, [choicesData])

  useEffect(() => {
    if (createCourseError) {
      const timer = setTimeout(() => setCreateCourseError(''), 15000)
      return () => clearTimeout(timer)
    }
  }, [createCourseError])

  if (loading || choicesLoading) {
    return <LoadingProfile message={t('Завантаження...')} />
  }

  if (error || choicesError || !profileData) {
    return (
      <ErrorProfile
        error={
          error || choicesError || t('Помилка завантаження даних користувача')
        }
        onRetry={() => {
          refreshProfile()
          refreshChoices()
        }}
      />
    )
  }

  const userInfo = {
    name: profileData.user.name,
    surname: profileData.user.surname,
    email: profileData.user.email,
    role: profileData.user.role,
  }

  const padTwoDigits = (num: number): string => num.toString().padStart(2, '0')
  const formatDuration = (
    days: number,
    hours: number,
    minutes: number
  ): string => {
    return `${padTwoDigits(days)}:${padTwoDigits(hours)}:${padTwoDigits(minutes)}`
  }

  const handleBackPage = () => {
    navigate('/my-created-courses')
  }

  const handleCancelCreateCourse = () => {
    setShowCanselModal(true)
  }

  const handleConfirmCancelCreateCourse = () => {
    setCourseStateTitle('')
    setCourseStateCategory('')
    setCourseStateLevel('')
    setCourseStateLanguage('')
    setCourseStateImage('')
    setShowPreview(false)
    setCourseStateTimeToComplete({ days: 0, hours: 0, minutes: 0 })
    setCourseStateDescription('')
    setShowCanselModal(false)
    handleBackPage()
  }

  const handleSaveCourse = async () => {
    try {
      setIsSaving(true)
      if (
        courseStateTimeToComplete.days < 0 ||
        courseStateTimeToComplete.hours < 0 ||
        courseStateTimeToComplete.hours > 23 ||
        courseStateTimeToComplete.minutes < 0 ||
        courseStateTimeToComplete.minutes > 59
      ) {
        setCreateCourseError(
          t('Невірний формат часу. Перевірте введені значення.')
        )
        setIsSaving(false)
        return
      }

      const response = await createCourseService.createCourse({
        title: courseStateTitle,
        description: courseStateDescription,
        category: courseStateCategory,
        is_published: courseStateIsPublished,
        level: courseStateLevel,
        course_language: courseStateLanguage,
        time_to_complete: formatDuration(
          courseStateTimeToComplete.days,
          courseStateTimeToComplete.hours,
          courseStateTimeToComplete.minutes
        ),
        cover_imageFile: courseStateImageFile,
        courseStructure: courseStructure.courseStructure,
      })

      if (response.status === 200 || response.status === 201) {
        handleCancelCreateCourse()
        navigate(
          `/my-created-courses/?Message=${encodeURIComponent(
            response.message
          )}&Status=${response.status}&Action=create`
        )
      } else {
        setCreateCourseError(
          t('Помилка при створенні курсу. ') + response.message
        )
      }
    } catch (error) {
      setCreateCourseError(
        error instanceof Error
          ? error.message
          : t('Помилка при створенні курсу. ')
      )
    } finally {
      setIsSaving(false)
    }
  }

  const handlePublishCourse = () => {
    setShowPublishModal(true)
  }

  const handleConfirmPublishCourse = async () => {
    setShowPublishModal(false)
    setCourseStateIsPublished(true)
    await handleSaveCourse()
  }

  return (
    <div className="min-h-screen bg-background">
      <Sidebar userInfo={userInfo} />

      <div className="ml-64">
        <CourseHeader
          title={t('Створення курсу')}
          description={t('Створюйте новий курс з нами!')}
          createCourse={true}
          actionOnClick={[
            handleCancelCreateCourse,
            handleSaveCourse,
            handlePublishCourse,
          ]}
          actionInfo={isSaving}
          actionText={[t('Скасувати'), t('Зберегти курс')]}
          actionsBackPage={
            <Button variant="outline" size="icon" onClick={handleBackPage}>
              <ArrowLeft className="w-5 h-5" />
            </Button>
          }
        />

        <main className="p-6">
          <div className="w-full max-w-6xl relative mx-auto">
            {createCourseError && (
              <Alert className="mb-6 border-destructive bg-destructive/10">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription className="text-destructive">
                  {createCourseError}
                </AlertDescription>
              </Alert>
            )}
          </div>

          <div className="flex flex-wrap justify-center">
            <CollapsibleSection title={t('Основна інформація про курс')}>
              <Card
                key={'course-main-info-card'}
                className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer bg-white dark:bg-slate-800 dark:hover:shadow-gray-700"
              >
                <CardContent className="p-6 text-slate-700 dark:text-slate-200">
                  <div className="gap-6">
                    <div>
                      <Label htmlFor="title">{t('Назва курсу *')}</Label>
                      <Input
                        id="title"
                        value={courseStateTitle}
                        onChange={e => setCourseStateTitle(e.target.value)}
                        placeholder={t('Введіть назву курсу')}
                        className="mt-1"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
                    <div>
                      <Label htmlFor="category">{t('Категорія *')}</Label>
                      <Select
                        value={courseStateCategory}
                        onValueChange={value => setCourseStateCategory(value)}
                      >
                        <SelectTrigger className="mt-1">
                          <SelectValue placeholder={t('Оберіть категорію')} />
                        </SelectTrigger>
                        <SelectContent>
                          {categories.map(category => (
                            <SelectItem
                              key={category.value}
                              value={category.value}
                            >
                              {category.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="level">{t('Рівень *')}</Label>
                      <Select
                        value={courseStateLevel}
                        onValueChange={value => setCourseStateLevel(value)}
                      >
                        <SelectTrigger className="mt-1">
                          <SelectValue placeholder={t('Оберіть рівень')} />
                        </SelectTrigger>
                        <SelectContent>
                          {levels.map(level => (
                            <SelectItem key={level.value} value={level.value}>
                              {level.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label htmlFor="language">{t('Мова курсу *')}</Label>
                      <Input
                        id="language"
                        value={courseStateLanguage}
                        onChange={e => setCourseStateLanguage(e.target.value)}
                        placeholder={t('Введіть мову курсу')}
                        className="mt-1"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
                    <div>
                      <Label>{t('Зображення курсу')}</Label>
                      <div className="flex flex-col gap-2 mt-1">
                        <input
                          type="file"
                          accept="image/*"
                          id="course-image-input"
                          className="hidden"
                          onChange={e => {
                            if (e.target.files && e.target.files[0]) {
                              const file = e.target.files[0]
                              setCourseStateImage(URL.createObjectURL(file))
                              setCourseStateImageFile(file)
                              setShowPreview(true)
                            }
                          }}
                        />

                        <Button
                          variant="outline"
                          className="hover:bg-gray-100 dark:hover:bg-gray-700"
                          onClick={() => {
                            const input = document.getElementById(
                              'course-image-input'
                            ) as HTMLInputElement
                            input?.click()
                          }}
                        >
                          {courseStateImage
                            ? t('Змінити зображення')
                            : t('Завантажити зображення')}
                        </Button>

                        {courseStateImage && (
                          <Button
                            variant="outline"
                            className="hover:bg-gray-100 dark:hover:bg-gray-700"
                            size="sm"
                            onClick={() => setShowPreview(prev => !prev)}
                          >
                            {showPreview
                              ? t('Сховати прев’ю')
                              : t('Переглянути прев’ю')}
                          </Button>
                        )}

                        {courseStateImage && showPreview && (
                          <img
                            src={courseStateImage}
                            alt="Preview"
                            className="w-full max-w-xs h-auto rounded-md border border-gray-300 mt-2 mx-auto"
                          />
                        )}
                      </div>
                    </div>
                    <div>
                      <CourseDurationPicker
                        value={courseStateTimeToComplete}
                        onChange={setCourseStateTimeToComplete}
                        maxDays={30}
                      />
                    </div>
                  </div>

                  <div className="mt-6">
                    <Label htmlFor="description">{t('Опис курсу *')}</Label>
                    <Textarea
                      id="description"
                      value={courseStateDescription}
                      onChange={e => setCourseStateDescription(e.target.value)}
                      placeholder={t('Детально опишіть курс...')}
                      rows={4}
                      className="mt-1"
                    />
                  </div>
                </CardContent>
              </Card>
            </CollapsibleSection>
          </div>

          <div className="w-full max-w-6xl relative mx-auto mt-6">
            <CreateMTOfCourse
              courseStructure={courseStructure}
              setCourseStructure={setCourseStructure}
              lessonContentTypes={categoryLessonType}
            />
          </div>

          <div className="flex flex-wrap justify-center mt-6">
            <CollapsibleSection title={t('Збереження та публікація')}>
              <Card
                key={'course-save-publish-card'}
                className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer bg-white dark:bg-slate-800 dark:hover:shadow-gray-700"
              >
                <CardContent className="p-6 text-slate-700 dark:text-slate-200">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
                    <div className="flex justify-center md:justify-start">
                      <Label
                        htmlFor="cancelcreatecourse"
                        className="text-center md:text-left"
                      >
                        {t(
                          'Очистити форму і повернутись на сторінку створених курсів'
                        )}
                      </Label>
                    </div>
                    <div className="flex justify-center">
                      <Button
                        variant="outline"
                        className="w-60 hover:bg-gray-100 dark:hover:bg-gray-700"
                        onClick={handleCancelCreateCourse}
                        disabled={isSaving}
                      >
                        <Undo className="w-4 h-4 mr-2" />
                        {t('Скасувати')}
                      </Button>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6 items-center">
                    <div className="flex justify-center md:justify-start">
                      <Label
                        htmlFor="savecourse"
                        className="text-center md:text-left"
                      >
                        {t(
                          'Зберегти поточний стан курсу (курс можна буде редагувати пізніше)'
                        )}
                      </Label>
                    </div>
                    <div className="flex justify-center">
                      <Button
                        className="w-60 bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 text-white"
                        onClick={handleSaveCourse}
                        disabled={isSaving}
                      >
                        {isSaving ? (
                          <>
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            {t('Збереження...')}
                          </>
                        ) : (
                          <>
                            <Save className="w-4 h-4 mr-2" />
                            {t('Зберегти')}
                          </>
                        )}
                      </Button>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6 items-center">
                    <div className="flex justify-center md:justify-start">
                      <Label
                        htmlFor="publishcourse"
                        className="text-center md:text-left"
                      >
                        {t(
                          'Зберегти поточний стан курсу і опублікувати (курс НЕ можна буде видалити)'
                        )}
                      </Label>
                    </div>
                    <div className="flex justify-center">
                      <Button
                        className="w-60 bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 text-white"
                        onClick={handlePublishCourse}
                        disabled={isSaving}
                      >
                        {isSaving ? (
                          <>
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            {t('Публікація...')}
                          </>
                        ) : (
                          <>
                            <Globe className="w-4 h-4 mr-2" />
                            {t('Опублікувати')}
                          </>
                        )}
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </CollapsibleSection>
          </div>
        </main>
      </div>

      {showCanselModal && (
        <ConfirmModal
          isOpen={showCanselModal}
          onConfirm={handleConfirmCancelCreateCourse}
          onClose={() => setShowCanselModal(false)}
          title={t('Ви дійсно бажаєте скасувати створення курсу?')}
          description={t('Всі дані будуть втрачені')}
          buttonText={t('Повернутись до курсів')}
        />
      )}
      {showPublishModal && (
        <ConfirmModal
          isOpen={showPublishModal}
          onConfirm={handleConfirmPublishCourse}
          onClose={() => setShowPublishModal(false)}
          title={t('Публікація курсу')}
          description={t(
            'Після публікації курс НЕ можна буде редагувати чи видалити курс'
          )}
          buttonText={t('Опублікувати курс')}
        />
      )}
    </div>
  )
}

export default CreateCourse
