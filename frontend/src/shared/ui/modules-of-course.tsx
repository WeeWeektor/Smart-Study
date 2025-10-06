import { useI18n } from '@/shared/lib'
import { BookOpen, Plus } from 'lucide-react'
import { Button } from '@/shared/ui/button.tsx'
import { useState } from 'react'
import { Card, CardContent, CardTitle } from '@/shared/ui/card.tsx'
import { Label } from '@/shared/ui/label.tsx'
import { Input } from '@/shared/ui/input.tsx'

export const ModulesOfCourse = () => {
  const { t } = useI18n()
  const [countModule, setCountModule] = useState<number>(0)
  const [title, setTitle] = useState<string>('')

  const handleAddModule = () => {
    setCountModule(countModule + 1)
  }

  return (
    <div className="w-full">
      {countModule === 0 ? (
        <div className="text-center text-slate-500">
          <BookOpen className="w-12 h-12 mx-auto mb-4 text-slate-300" />
          <p className="text-lg font-medium mb-2">{t('Модулі не додано')}</p>
          <p>{t('Додайте перший модуль для початку створення курсу')}</p>
        </div>
      ) : (
        <div>
          <Card
            key={`module-${countModule}`}
            className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer bg-white dark:bg-slate-800 dark:hover:shadow-gray-700"
          >
            <CardTitle className="text-center text-slate-800 dark:text-slate-100 mt-6">
              {t('Модуль')} {countModule} {title && `- ${title}`}
            </CardTitle>
            <CardContent className="p-6 text-slate-700 dark:text-slate-200">
              <div className="gap-6">
                <Label htmlFor="title">{t('Назва модуля *')}</Label>
                <Input
                  id="title"
                  value={title}
                  onChange={e => setTitle(e.target.value)}
                  placeholder={t('Введіть назву модуля')}
                  className="mt-1"
                />
              </div>
            </CardContent>
          </Card>
        </div>
      )}
      <div className="flex justify-center mt-6">
        <Button
          onClick={handleAddModule}
          className="w-40 bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 text-white"
        >
          <Plus className="w-4 h-4 mr-2" />
          {t('Додати модуль')}
        </Button>
      </div>
    </div>
  )
}
