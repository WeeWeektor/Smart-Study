import { useI18n } from '@/shared/lib'
import { Sidebar } from '@/widgets/layout'
import { CourseHeader } from '@/widgets/course'
import { ErrorProfile, Input, LoadingProfile, MultiSelect } from '@/shared/ui'
import { useProfileData } from '@/shared/hooks/useProfileData'
import { Search } from 'lucide-react'
import { useEffect, useState } from 'react'
import { choicesGetService } from '@/features/choices-get'

interface Option {
  value: string
  label: string
}

const CoursesCatalog = () => {
  const { t } = useI18n()
  const { profileData, loading, error, refreshProfile } = useProfileData()
  const [searchQuery, setSearchQuery] = useState('')

  const [categoryFilter, setCategoryFilter] = useState<string[]>([])
  const [levelFilter, setLevelFilter] = useState<string[]>([])

  const [categories, setCategories] = useState<Option[]>([])
  const [levels, setLevels] = useState<Option[]>([])

  useEffect(() => {
    async function fetchChoices() {
      try {
        const response = await choicesGetService.getChoices()

        const categoriesData: Option[] = Object.entries(
          response.category[0]
        ).map(([key, label]) => ({
          value: key,
          label,
        }))
        const levelsData: Option[] = Object.entries(response.levels[0]).map(
          ([key, label]) => ({
            value: key,
            label,
          })
        )

        setCategories(categoriesData)
        setLevels(levelsData)
      } catch (err) {
        console.error('Помилка завантаження choices:', err)
      }
    }

    fetchChoices()
  }, [])

  if (loading) {
    return <LoadingProfile message={t('Завантаження...')} />
  }

  if (error || !profileData) {
    return (
      <ErrorProfile
        error={error || t('Помилка завантаження даних користувача')}
        onRetry={refreshProfile}
      />
    )
  }

  const userInfo = {
    name: profileData.user.name,
    surname: profileData.user.surname,
    email: profileData.user.email,
    role: profileData.user.role,
  }

  return (
    <div className="min-h-screen bg-background">
      <Sidebar userInfo={userInfo} />

      <div className="ml-64">
        <CourseHeader
          title={t('Підібрати курс')}
          description={t('Підберіть курс за вашими інтересами та цілями')}
        />

        <main className="p-6">
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
              <Input
                placeholder={t('Шукати курси...')}
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>

            <MultiSelect
              options={categories}
              selected={categoryFilter}
              onChange={setCategoryFilter}
              placeholder={t('Категорії')}
              className="w-48"
              countLabel={t('вибраних категорій')}
            />

            <MultiSelect
              options={levels}
              selected={levelFilter}
              onChange={setLevelFilter}
              placeholder={t('Рівень')}
              className="w-48"
              countLabel={t('вибраних рівні')}
            />
          </div>
        </main>
      </div>
    </div>
  )
}

export default CoursesCatalog
