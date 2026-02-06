import {
  Button,
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/shared/ui'
import {
  ChevronDown,
  Download,
  Eye,
  EyeOff,
  FileImage,
  FileText,
  ImagePlusIcon,
  Loader2,
  MessageSquarePlus,
  Trophy,
} from 'lucide-react'
import { useI18n } from '@/shared/lib'
import { CourseResults } from '@/pages/course-completion'
import React, { useState } from 'react'

interface CourseSuccessProps {
  courseId: string
  certificateUrl: string | null
  isGenerating: boolean
  onDownload: (format?: 'pdf' | 'png' | 'view') => void
  onGenerate: () => void
  onLeaveReview: () => void
  returnButtons: () => React.ReactNode
}

export const CourseSuccess = ({
  courseId,
  certificateUrl,
  isGenerating,
  onDownload,
  onGenerate,
  onLeaveReview,
  returnButtons,
}: CourseSuccessProps) => {
  const { t } = useI18n()
  const [showResults, setShowResults] = useState<boolean>(false)
  const [isImgLoaded, setIsImgLoaded] = useState(false)

  const toggleResults = () => {
    setShowResults(prev => !prev)
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <Card className="w-full max-w-4xl mx-auto overflow-hidden bg-white dark:bg-slate-800 border-green-200 dark:border-green-900/50 shadow-md">
        <div className="flex flex-col items-center text-center p-6 sm:p-10">
          {certificateUrl ? (
            <div className="mb-8 relative group w-full max-w-[600px] mx-auto animate-in zoom-in-50 duration-500">
              <div className="absolute -inset-1 bg-gradient-to-r from-green-400 to-emerald-600 rounded-lg blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200" />

              <div className="relative rounded-lg overflow-hidden border-4 border-white dark:border-slate-700 shadow-xl bg-slate-100 dark:bg-slate-900">
                {!isImgLoaded && (
                  <div className="flex items-center justify-center h-[300px] w-full">
                    <Loader2 className="h-8 w-8 animate-spin text-green-600" />
                  </div>
                )}
                <img
                  src={certificateUrl}
                  alt="Course Certificate"
                  className={`w-full h-auto object-contain transition-opacity duration-300 ${isImgLoaded ? 'opacity-100' : 'opacity-0'}`}
                  onLoad={() => setIsImgLoaded(true)}
                />

                <div
                  className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center cursor-pointer"
                  onClick={() => onDownload('view')}
                >
                  <Button
                    variant="secondary"
                    className="gap-2 pointer-events-none"
                  >
                    <Eye className="w-4 h-4" />
                    {t('Відкрити у новій вкладці')}
                  </Button>
                </div>
              </div>
            </div>
          ) : (
            <div className="mb-6 flex h-24 w-24 items-center justify-center rounded-full bg-green-50 dark:bg-green-900/20">
              {isGenerating ? (
                <Loader2 className="h-12 w-12 animate-spin text-green-600 dark:text-green-400" />
              ) : (
                <Trophy className="h-12 w-12 text-green-600 dark:text-green-400" />
              )}
            </div>
          )}

          <CardHeader className="p-0 mb-4">
            <h3 className="text-2xl font-bold tracking-tight text-foreground">
              {t('Вітаємо з успішним завершенням!')}
            </h3>
          </CardHeader>

          <CardContent className="p-0 mb-8 max-w-lg mx-auto">
            <p className="text-muted-foreground text-lg leading-relaxed">
              {certificateUrl
                ? t(
                    'Ви успішно пройшли всі етапи курсу. Ваш іменний сертифікат вже сформовано та готовий до завантаження.'
                  )
                : t(
                    'Ви успішно пройшли всі етапи курсу. Тепер ви можете згенерувати та отримати свій сертифікат.'
                  )}
            </p>
          </CardContent>

          <CardFooter className="p-0 w-full flex flex-col items-center gap-4">
            {certificateUrl ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    size="lg"
                    className="w-full sm:w-auto min-w-[240px] gap-2 bg-green-600 hover:bg-green-700 text-white shadow-lg transition-all hover:scale-105"
                  >
                    <Download className="w-5 h-5" />
                    {t('Завантажити сертифікат')}
                    <ChevronDown className="w-4 h-4 ml-1 opacity-70" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="center" className="w-[240px]">
                  <DropdownMenuItem onClick={() => onDownload('pdf')}>
                    <FileText className="w-4 h-4 mr-2" />
                    {t('Завантажити як PDF')}
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => onDownload('png')}>
                    <FileImage className="w-4 h-4 mr-2" />
                    {t('Завантажити як PNG')}
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => onDownload('view')}>
                    <Eye className="w-4 h-4 mr-2" />
                    {t('Відкрити у новій вкладці')}
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <Button
                onClick={onGenerate}
                disabled={isGenerating}
                size="lg"
                className="w-full sm:w-auto min-w-[240px] gap-2 text-base font-medium"
                variant={isGenerating ? 'outline' : 'default'}
              >
                {isGenerating ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <ImagePlusIcon className="w-5 h-5" />
                )}
                {isGenerating ? t('Генерація...') : t('Отримати сертифікат')}
              </Button>
            )}

            <div className="flex items-center gap-4">
              <Button
                onClick={toggleResults}
                variant="outline"
                className="text-muted-foreground hover:text-foreground gap-2 mt-2 w-64"
              >
                {showResults ? (
                  <>
                    <EyeOff className="w-4 h-4" />
                    {t('Приховати результати')}
                  </>
                ) : (
                  <>
                    <Eye className="w-4 h-4" />
                    {t('Переглянути бали за тести')}
                  </>
                )}
              </Button>
              <Button
                onClick={onLeaveReview}
                variant="outline"
                className="text-muted-foreground hover:text-foreground gap-2 mt-2 w-64"
              >
                <MessageSquarePlus className="w-4 h-4" />
                {t('Залишити відгук')}
              </Button>
            </div>

            {returnButtons()}
          </CardFooter>
        </div>

        <div className="h-1.5 w-full bg-gradient-to-r from-green-400 to-emerald-500" />
      </Card>

      {showResults && (
        <div className="animate-in slide-in-from-top-4 fade-in duration-300 w-full max-w-4xl mx-auto">
          <CourseResults courseId={courseId} />
        </div>
      )}
    </div>
  )
}
