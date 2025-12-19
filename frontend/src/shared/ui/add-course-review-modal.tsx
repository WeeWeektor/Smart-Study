import React, { type FC, useEffect, useState } from 'react'
import { useI18n } from '@/shared/lib'
import {
  Button,
  Card,
  ConfirmModal,
  Label,
  Textarea,
  Alert,
  AlertDescription,
} from '@/shared/ui'
import {
  AlertTriangle,
  Loader2,
  Save,
  Star,
  Undo,
  X,
  MessageSquare,
} from 'lucide-react'
import { disablePageScroll, enablePageScroll } from '@/shared/scroll'
import { courseReviewService, type Review } from '@/features/course'

interface AddCourseReviewModalProps {
  isOpen: boolean
  onClose: () => void
  courseId: string
  onReviewAdded: (review: Review) => void
}

export const AddCourseReviewModal: FC<AddCourseReviewModalProps> = ({
  isOpen,
  onClose,
  courseId,
  onReviewAdded,
}) => {
  const { t } = useI18n()

  const [rating, setRating] = useState(0)
  const [comment, setComment] = useState('')
  const [hoverRating, setHoverRating] = useState(0)

  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showCancelModal, setShowCancelModal] = useState(false)

  useEffect(() => {
    if (isOpen) {
      disablePageScroll()
    } else {
      enablePageScroll()
    }
    return () => enablePageScroll()
  }, [isOpen])

  if (!isOpen) return null

  const handleSubmit = async () => {
    if (rating === 0) {
      setError(t('Будь ласка, поставте оцінку.'))
      return
    }
    if (comment.trim().length < 10) {
      setError(t('Коментар має містити щонайменше 10 символів.'))
      return
    }

    setIsSubmitting(true)
    setError(null)

    try {
      const newReview = await courseReviewService.createReview({
        course_id: courseId,
        rating,
        comment,
      })

      onReviewAdded(newReview)
      resetForm()
      onClose()
    } catch (err) {
      setError(
        err instanceof Error ? err.message : t('Не вдалось додати відгук')
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  const resetForm = () => {
    setRating(0)
    setComment('')
    setError(null)
    setHoverRating(0)
    setIsSubmitting(false)
  }

  const handleCloseAttempt = () => {
    const hasData = rating > 0 || comment.trim().length > 0
    if (hasData) {
      setShowCancelModal(true)
    } else {
      handleCloseConfirmed()
    }
  }

  const handleCloseConfirmed = () => {
    resetForm()
    onClose()
  }

  const handleContentClick = (e: React.MouseEvent) => e.stopPropagation()

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 backdrop-blur-sm animate-in fade-in duration-200">
      <div
        className="bg-white dark:bg-slate-800 rounded-xl w-full max-w-lg max-h-[90vh]
           overflow-y-auto p-6 relative shadow-2xl border border-slate-200 dark:border-slate-700
           scrollbar-thin scrollbar-thumb-transparent hover:scrollbar-thumb-gray-400 dark:hover:scrollbar-thumb-gray-600
           transition-colors animate-in zoom-in-95 duration-200"
        onClick={handleContentClick}
        role="dialog"
        aria-modal="true"
      >
        <div className="flex flex-col items-center justify-center mb-6 relative">
          <h2 className="text-2xl font-semibold flex items-center gap-2">
            <MessageSquare className="w-6 h-6 text-brand-600" />
            {t('Залишити відгук')}
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-2 text-center">
            {t('Поділіться своїми враженнями про цей курс')}
          </p>

          <button
            onClick={handleCloseAttempt}
            className="absolute top-0 right-0 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md text-sm font-medium border border-red-200">
            {error}
          </div>
        )}

        <div className="space-y-6">
          <Card className="p-4 bg-slate-50 dark:bg-slate-700/30 border border-slate-100 dark:border-slate-700">
            <div className="flex flex-col items-center gap-3">
              <Label className="text-base font-medium">
                {t('Ваша оцінка')}
              </Label>
              <div className="flex gap-2">
                {[1, 2, 3, 4, 5].map(star => (
                  <button
                    key={star}
                    type="button"
                    className="focus:outline-none transition-transform hover:scale-110 p-1"
                    onClick={() => setRating(star)}
                    onMouseEnter={() => setHoverRating(star)}
                    onMouseLeave={() => setHoverRating(0)}
                  >
                    <Star
                      className={`w-8 h-8 transition-all duration-200 ${
                        star <= (hoverRating || rating)
                          ? 'fill-yellow-400 text-yellow-400 drop-shadow-sm'
                          : 'text-slate-300 dark:text-slate-600'
                      }`}
                    />
                  </button>
                ))}
              </div>
              <span className="text-sm font-medium text-brand-600 min-h-[20px] transition-all">
                {rating > 0 || hoverRating > 0
                  ? t(
                      [
                        'Дуже погано',
                        'Погано',
                        'Нормально',
                        'Добре',
                        'Чудово!',
                      ][(hoverRating || rating) - 1]
                    )
                  : ''}
              </span>
            </div>
          </Card>

          <div>
            <Label htmlFor="reviewComment" className="mb-2 block">
              {t('Ваш коментар *')}
            </Label>
            <Textarea
              id="reviewComment"
              value={comment}
              onChange={e => setComment(e.target.value)}
              placeholder={t(
                'Що вам сподобалось, а що можна покращити? (мінімум 10 символів)'
              )}
              className="min-h-[140px] resize-none focus:ring-brand-500"
            />
          </div>

          <Alert
            variant="destructive"
            className="bg-orange-50 text-orange-800 border-orange-200 dark:bg-orange-900/20 dark:text-orange-300 dark:border-orange-800"
          >
            <AlertTriangle className="h-4 w-4 stroke-orange-600 dark:stroke-orange-400" />
            <AlertDescription className="text-xs font-medium ml-2 leading-relaxed">
              {t(
                'Увага: Після публікації ви НЕ зможете редагувати або видалити цей відгук. Будь ласка, перевірте написане перед відправкою.'
              )}
            </AlertDescription>
          </Alert>

          <div className="my-4 flex-grow h-px bg-gray-200 dark:bg-gray-700" />

          <div className="flex justify-center space-x-4 mt-6">
            <Button
              className="w-40 hover:bg-gray-100 dark:hover:bg-gray-700 border-slate-200 dark:border-slate-600"
              variant="outline"
              onClick={handleCloseAttempt}
              disabled={isSubmitting}
            >
              <Undo className="w-4 h-4 mr-2" />
              {t('Скасувати')}
            </Button>

            <Button
              className="w-40 bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 text-white shadow-md hover:shadow-lg transition-all"
              onClick={handleSubmit}
              disabled={isSubmitting || rating === 0}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  {t('Публікація...')}
                </>
              ) : (
                <>
                  <Save className="w-4 h-4 mr-2" />
                  {t('Опублікувати')}
                </>
              )}
            </Button>
          </div>
        </div>
      </div>

      {showCancelModal && (
        <ConfirmModal
          isOpen={showCancelModal}
          onConfirm={handleCloseConfirmed}
          onClose={() => setShowCancelModal(false)}
          title={t('Скасувати відгук?')}
          description={t(
            'Ви ввели дані, які будуть втрачені при закритті. Ви впевнені?'
          )}
          buttonText={t('Так, закрити')}
        />
      )}
    </div>
  )
}
