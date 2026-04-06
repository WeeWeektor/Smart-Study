import { Button, Card, CardContent, CardFooter, CardHeader } from '@/shared/ui'
import { ArrowRight, BookOpenText } from 'lucide-react'
import { useI18n } from '@/shared/lib'

interface CourseInProgressProps {
  onContinue: () => void
}

export const CourseInProgress = ({ onContinue }: CourseInProgressProps) => {
  const { t } = useI18n()

  return (
    <Card className="w-full max-w-4xl mx-auto overflow-hidden bg-white dark:bg-slate-800 border-blue-200 dark:border-blue-900/50 shadow-md">
      <div className="flex flex-col items-center text-center p-6 sm:p-10">
        <div className="mb-6 flex h-24 w-24 items-center justify-center rounded-full bg-blue-50 dark:bg-blue-900/20">
          <BookOpenText className="h-12 w-12 text-blue-600 dark:text-blue-400" />
        </div>

        <CardHeader className="p-0 mb-4">
          <h3 className="text-2xl font-bold tracking-tight text-foreground">
            {t('Навчання в процесі')}
          </h3>
        </CardHeader>

        <CardContent className="p-0 mb-8 max-w-lg mx-auto">
          <p className="text-muted-foreground text-lg leading-relaxed">
            {t(
              'Ви ще не завершили цей курс. Продовжуйте навчання та виконайте всі завдання, щоб отримати сертифікат.'
            )}
          </p>
        </CardContent>

        <CardFooter className="p-0 w-full flex justify-center">
          <Button
            onClick={onContinue}
            size="lg"
            className="w-full sm:w-auto min-w-[200px] gap-2 text-base font-medium"
          >
            {t('Продовжити навчання')}
            <ArrowRight className="w-5 h-5" />
          </Button>
        </CardFooter>
      </div>

      <div className="h-1.5 w-full bg-gradient-to-r from-blue-400 to-indigo-500" />
    </Card>
  )
}
