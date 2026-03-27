import React from 'react'
import { Button, Card, CardContent, ConfirmModal } from '@/shared/ui'
import {
  ArrowRight,
  BarChart,
  CalendarDays,
  FileText,
  Heart,
  Loader2,
  MessageCirclePlusIcon,
  RefreshCw,
  Rocket,
  Trash2,
  UploadCloud,
} from 'lucide-react'
import { useI18n } from '@/shared/lib'
import { type CourseResponse } from '@/features/course'

interface CourseFooterSectionProps {
  course: CourseResponse | null
  userStatus: string | null
  inWishlist: boolean
  onStartCourse: () => void
  onAddToWishlist: () => void
  onRemoveFromWishlist: () => void
  onPublishCourse: () => void
  onRemoveCourse: () => void
  onChangeCourse: () => void
  onShowStatistics?: () => void
  showPublishModal: boolean
  setShowPublishModal: (open: boolean) => void
  isConfirmDelOpen: boolean
  setIsConfirmDelOpen: (open: boolean) => void
  isEnrolling?: boolean
  isCourseOwner: boolean
  onPlanCourse?: () => void
}

export const CourseFooterSection: React.FC<CourseFooterSectionProps> = ({
  course,
  userStatus,
  inWishlist,
  onStartCourse,
  onAddToWishlist,
  onRemoveFromWishlist,
  onPublishCourse,
  onRemoveCourse,
  onChangeCourse,
  onShowStatistics,
  showPublishModal,
  setShowPublishModal,
  isConfirmDelOpen,
  setIsConfirmDelOpen,
  isEnrolling = false,
  isCourseOwner,
  onPlanCourse,
}) => {
  const { t } = useI18n()

  if (!course || !course.course) return null

  if (!course.course.is_published) {
    return (
      <Card className="mt-8 border-t-4 border-t-brand-600 shadow-lg bg-slate-50 dark:bg-slate-900/50">
        <CardContent className="p-8 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex flex-col gap-2">
            <h3 className="text-xl font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
              <UploadCloud className="w-6 h-6 text-brand-600" />
              {t('Цей курс ще не опублікований')}
            </h3>
            <p className="text-slate-600 dark:text-slate-400">
              {t(
                'Наразі курс знаходиться в режимі чернетки. Перевірте наповнення та опублікуйте його для студентів.'
              )}
            </p>
          </div>

          <div className="flex flex-wrap gap-4 items-center justify-center md:justify-end min-w-[200px]">
            <Button
              onClick={onChangeCourse}
              variant="outline"
              size="lg"
              className="min-w-[140px] w-60"
            >
              <FileText className="w-5 h-5 mr-2" />
              {t('Редагувати курс')}
            </Button>

            <Button
              onClick={() => setShowPublishModal(true)}
              size="lg"
              className="w-60 bg-brand-600 hover:bg-brand-700 min-w-[160px] shadow-md shadow-brand-600/20"
            >
              <UploadCloud className="w-5 h-5 mr-2" />
              {t('Опублікувати')}
            </Button>
            <ConfirmModal
              isOpen={showPublishModal}
              onConfirm={onPublishCourse}
              onClose={() => setShowPublishModal(false)}
              title={t('Публікація курсу')}
              description={t(
                'Після публікації курс НЕ можна буде редагувати чи видалити курс'
              )}
              buttonText={t('Опублікувати курс')}
            />

            <Button
              variant="outline"
              size="lg"
              className="w-60 border-red-200 text-red-600 hover:bg-red-50 hover:text-red-700 dark:border-red-900/50 dark:hover:bg-red-900/20"
              onClick={() => setIsConfirmDelOpen(true)}
            >
              <Trash2 className="w-5 h-5 mr-2" />
              {t('Видалити')}
            </Button>
            <ConfirmModal
              isOpen={isConfirmDelOpen}
              onClose={() => setIsConfirmDelOpen(false)}
              onConfirm={onRemoveCourse}
              title={t('Видалення курсу')}
              description={t(
                'Ви впевнені, що хочете видалити цей курс? Цю дію неможливо скасувати.'
              )}
            />
          </div>
        </CardContent>
      </Card>
    )
  }

  const StatisticsButton = () => (
    <Button
      onClick={onShowStatistics}
      variant="outline"
      size="lg"
      className="w-60 min-w-[180px] border-brand-200 text-brand-700 hover:bg-brand-50 hover:text-brand-800 dark:border-brand-900/50 dark:hover:bg-brand-900/20"
      disabled={isEnrolling}
    >
      <BarChart className="w-5 h-5 mr-2" />
      {t('Статистика курсу')}
    </Button>
  )

  const AddMessageToCourseStudents = () => (
    // TODO: add real action to modal with form to send message to students and api call
    <Button
      onClick={onShowStatistics}
      variant="outline"
      size="lg"
      className="w-60 min-w-[180px] border-brand-200 text-brand-700 hover:bg-brand-50 hover:text-brand-800 dark:border-brand-900/50 dark:hover:bg-brand-900/20"
      disabled={isEnrolling}
    >
      <MessageCirclePlusIcon className="w-5 h-5 mr-2" />
      {t('Повідомлення студентам')}
    </Button>
  )

  return (
    <Card className="mt-8 border-t-4 border-t-brand-600 shadow-lg bg-slate-50 dark:bg-slate-900/50">
      <CardContent className="p-8 flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex flex-col gap-2">
          <h3 className="text-xl font-bold text-slate-900 dark:text-slate-100">
            {isCourseOwner
              ? t('Управління курсом')
              : userStatus === 'completed'
                ? t('Ви успішно завершили цей курс!')
                : userStatus === 'in_progress'
                  ? t('Продовжуйте навчання')
                  : t('Готові розпочати навчання?')}
          </h3>
          <p className="text-slate-600 dark:text-slate-400">
            {isCourseOwner
              ? t(
                  'Ви можете переглядати статистику або пройти курс для перевірки (попередній перегляд).'
                )
              : userStatus === 'completed'
                ? t('Ви можете переглянути матеріали курсу в будь-який час.')
                : t(
                    'Отримайте повний доступ до всіх матеріалів та сертифікат по завершенню.'
                  )}
          </p>
        </div>

        <div className="flex flex-wrap gap-4 items-center justify-center md:justify-end min-w-[200px]">
          {isCourseOwner && (
            <>
              <StatisticsButton />
              <AddMessageToCourseStudents />
            </>
          )}

          {userStatus === 'completed' ? (
            <Button
              onClick={onStartCourse}
              size="lg"
              variant="outline"
              className="min-w-[160px] w-60"
              disabled={isEnrolling}
            >
              {isEnrolling ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <RefreshCw className="w-4 h-4 mr-2" />
              )}
              {t('Переглянути знову')}
            </Button>
          ) : userStatus === 'in_progress' ? (
            <>
              <Button
                onClick={onPlanCourse}
                variant="outline"
                size="lg"
                className="w-60 min-w-[180px] border-brand-200 text-brand-700 hover:bg-brand-50 dark:border-brand-900/50 dark:hover:bg-brand-900/20"
                disabled={isEnrolling}
              >
                <CalendarDays className="w-5 h-5 mr-2" />
                {t('Запланувати проходження')}
              </Button>

              <Button
                onClick={onStartCourse}
                size="lg"
                className="w-60 bg-brand-600 hover:bg-brand-700 min-w-[160px] shadow-md shadow-brand-600/20"
                disabled={isEnrolling}
              >
                {isEnrolling ? (
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                ) : (
                  <ArrowRight className="w-5 h-5 mr-2" />
                )}{' '}
                {t('Продовжити навчання')}
              </Button>
            </>
          ) : (
            <>
              {!isCourseOwner &&
                (inWishlist ? (
                  <Button
                    onClick={onRemoveFromWishlist}
                    variant="outline"
                    size="lg"
                    className="w-60 border-red-200 text-red-600 hover:bg-red-50 hover:text-red-700 dark:border-red-900/50 dark:hover:bg-red-900/20"
                    disabled={isEnrolling}
                  >
                    <Trash2 className="w-5 h-5 mr-2" />
                    {t('Прибрати з вішліста')}
                  </Button>
                ) : (
                  <Button
                    onClick={onAddToWishlist}
                    variant="outline"
                    size="lg"
                    className="w-60 min-w-[180px]"
                    disabled={isEnrolling}
                  >
                    <Heart className="w-5 h-5 mr-2" />
                    {t('У вішліст')}
                  </Button>
                ))}

              <Button
                onClick={onStartCourse}
                size="lg"
                className="w-60 bg-brand-600 hover:bg-brand-700 min-w-[180px] shadow-lg shadow-brand-600/20 animate-pulse-slow"
                disabled={isEnrolling}
              >
                {isEnrolling ? (
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                ) : (
                  <Rocket className="w-5 h-5 mr-2" />
                )}{' '}
                {isCourseOwner ? t('Переглянути курс') : t('Розпочати курс')}
              </Button>
            </>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
