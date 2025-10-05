import { useI18n } from '@/shared/lib'
import {
  Alert,
  AlertDescription,
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
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
import { AlertCircle, ArrowLeft } from 'lucide-react'
import { useProfileData } from '@/shared/hooks'
import { useEffect, useState } from 'react'
import { useChoicesData } from '@/shared/hooks/useChoiceData'
import { useNavigate } from 'react-router-dom'
import CourseDurationPicker from '@/shared/ui/duration-picker.tsx'

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
  const [isSaving, setIsSaving] = useState(false)
  const [courseStateTitle, setCourseStateTitle] = useState<string>('')
  const [courseStateDescription, setCourseStateDescription] =
    useState<string>('')
  const [courseStateCategory, setCourseStateCategory] = useState<string>('')
  const [courseStateImage, setCourseStateImage] = useState<string>('')
  const [courseStateLevel, setCourseStateLevel] = useState<string>('')
  const [courseStateTimeToComplete, setCourseStateTimeToComplete] = useState({
    days: 0,
    hours: 0,
    minutes: 0,
  })
  const [courseStateLanguage, setCourseStateLanguage] = useState<string>('')
  const [showPreview, setShowPreview] = useState<boolean>(false)

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

      setCategories(categoriesData)
      setLevels(levelsData)
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

  const handleCancelCreateCourse = () => {
    console.log('cancel create course')
  }

  const handleSaveCourse = () => {
    console.log('save course')
  }

  const handlePublishCourse = () => {
    handleSaveCourse()
    console.log('publish course')
  }

  const handleBackPage = () => {
    navigate(-1)
  }

  return (
    <div className="min-h-screen bg-background">
      <Sidebar userInfo={userInfo} />

      <div className="ml-64">
        <CourseHeader
          title={t('Створення курсу')}
          description={t('Створюйте новий курс з нами!')}
          createCourse={true}
          actionOnClick={[handleCancelCreateCourse, handleSaveCourse]}
          actionInfo={isSaving}
          actionText={[t('Скасувати'), t('Зберегти курс')]}
          actionsBackPage={
            <Button variant="outline" size="icon" onClick={handleBackPage}>
              <ArrowLeft className="w-5 h-5" />
            </Button>
          }
        />

        <main className="p-6">
          {createCourseError && (
            <Alert className="mb-6 border-destructive bg-destructive/10">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription className="text-destructive">
                {createCourseError}
              </AlertDescription>
            </Alert>
          )}

          <div className="flex flex-wrap justify-center">
            <Card className="w-full max-w-6xl">
              <CardHeader>
                <CardTitle>{t('Основна інформація про курс')}</CardTitle>
              </CardHeader>
              <CardContent>
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
                            setShowPreview(true)
                          }
                        }}
                      />

                      <Button
                        variant="outline"
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
                          variant="secondary"
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
                          className="w-full max-w-xs h-auto rounded-md border border-gray-300 mt-2"
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
          </div>
        </main>
      </div>
    </div>
  )
}

export default CreateCourse
