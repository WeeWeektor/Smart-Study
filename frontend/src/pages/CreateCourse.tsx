import { useI18n } from '@/shared/lib'
import {
  Alert,
  AlertDescription,
  ErrorProfile,
  LoadingProfile,
} from '@/shared/ui'
import { CourseHeader } from '@/widgets/course'
import { Sidebar } from '@/widgets/layout'
import { AlertCircle } from 'lucide-react'
import { useProfileData } from '@/shared/hooks'
import { useEffect, useState } from 'react'
import { useChoicesData } from '@/shared/hooks/useChoiceData'

interface Option {
  value: string
  label: string
}

const CreateCourse = () => {
  const { t } = useI18n()
  const { profileData, loading, error, refreshProfile } = useProfileData()
  const {
    choicesData,
    loading: choicesLoading,
    error: choicesError,
    refreshChoices,
  } = useChoicesData()
  const [createCourseError, setCreateCourseError] = useState<string>('')
  const [categories, setCategories] = useState<Option[]>([])
  const [categoryChoice, setCategoryChoice] = useState<string>('')
  const [levels, setLevels] = useState<Option[]>([])
  const [levelChoice, setLevelChoice] = useState<string>('')
  const [isSaving, setIsSaving] = useState(false)

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
        </main>
      </div>
    </div>
  )
}

export default CreateCourse
