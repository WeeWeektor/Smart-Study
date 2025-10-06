import { useI18n } from '@/shared/lib'
import { BookOpen, Plus } from 'lucide-react'
import { Button } from '@/shared/ui/button.tsx'
import { useState } from 'react'

export const TestsOfCourse = () => {
  const { t } = useI18n()
  const [countTest, setCountTest] = useState<number>(0)

  const handleAddTest = () => {
    setCountTest(countTest + 1)
  }

  return (
    <div className="w-full">
      {countTest === 0 ? (
        <div className="text-center text-slate-500">
          <BookOpen className="w-12 h-12 mx-auto mb-4 text-slate-300" />
          <p className="text-lg font-medium mb-2">{t('Тести не додано')}</p>
          <p>{t('Додайте перший тест для початку створення курсу')}</p>
        </div>
      ) : (
        <div>
          <p>asjflk</p>
        </div>
      )}
      <div className="flex justify-center mt-6">
        <Button
          onClick={handleAddTest}
          className="w-40 bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 text-white"
        >
          <Plus className="w-4 h-4 mr-2" />
          {t('Додати тест')}
        </Button>
      </div>
    </div>
  )
}
