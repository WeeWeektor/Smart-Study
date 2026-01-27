import React from 'react'
import {
  Avatar,
  AvatarFallback,
  AvatarImage,
  Button,
  Card,
  CardContent,
  CardHeader,
} from '@/shared/ui'
import {
  Calendar,
  ChevronDown,
  ChevronUp,
  MessageSquare,
  Plus,
  Star,
} from 'lucide-react'
import { formatShortDate, useI18n } from '@/shared/lib'
import { type Review } from '@/features/course'

interface ReviewsSectionProps {
  reviews: Review[]
  isReviewsExpanded: boolean
  setIsReviewsExpanded: React.Dispatch<React.SetStateAction<boolean>>
  setIsAddReviewModalOpen: React.Dispatch<React.SetStateAction<boolean>>
}

export const ReviewsSection: React.FC<ReviewsSectionProps> = ({
  reviews,
  isReviewsExpanded,
  setIsReviewsExpanded,
  setIsAddReviewModalOpen,
}) => {
  const { t } = useI18n()

  const AddReviewButton = () => (
    <Button
      variant="outline"
      size="sm"
      onClick={() => setIsAddReviewModalOpen(true)}
    >
      <Plus className="w-4 h-4 mr-2" />
      {t('Додати відгук')}
    </Button>
  )

  if (!reviews || reviews.length === 0) {
    return (
      <Card className="mb-8 overflow-hidden shadow-sm border border-slate-200 dark:border-slate-800">
        <CardHeader className="pb-4 border-b border-slate-100 dark:border-slate-800 flex flex-row items-center justify-between">
          <h3 className="text-xl font-bold text-slate-800 dark:text-slate-100 flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-brand-600" />
            {t('Відгуки студентів')}
            <span className="ml-2 text-sm font-normal text-slate-500 bg-slate-100 dark:bg-slate-800 px-2.5 py-0.5 rounded-full">
              0
            </span>
          </h3>
          <AddReviewButton />
        </CardHeader>
        <CardContent className="p-8 text-center">
          <div className="w-16 h-16 bg-slate-100 dark:bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-4">
            <MessageSquare className="w-8 h-8 text-slate-400 dark:text-slate-500" />
          </div>
          <h3 className="text-lg font-medium text-slate-900 dark:text-slate-100 mb-1">
            {t('Відгуків поки немає')}
          </h3>
          <p className="text-slate-500 dark:text-slate-400">
            {t('Будьте першим, хто поділиться враженнями про цей курс!')}
          </p>
        </CardContent>
      </Card>
    )
  }

  const hasManyReviews = reviews.length > 3
  const displayedReviews = isReviewsExpanded ? reviews : reviews.slice(0, 3)

  return (
    <Card className="mb-8 overflow-hidden shadow-sm border border-slate-200 dark:border-slate-800">
      <CardHeader className="pb-4 border-b border-slate-100 dark:border-slate-800 flex flex-row items-center justify-between">
        <h3 className="text-xl font-bold text-slate-800 dark:text-slate-100 flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-brand-600" />
          {t('Відгуки студентів')}
          <span className="ml-2 text-sm font-normal text-slate-500 bg-slate-100 dark:bg-slate-800 px-2.5 py-0.5 rounded-full">
            {reviews.length}
          </span>
        </h3>

        <AddReviewButton />
      </CardHeader>

      <CardContent className="p-0">
        <div className="divide-y divide-slate-100 dark:divide-slate-800">
          {displayedReviews.map(review => {
            const userInitials =
              `${review.user.name.charAt(0)}${review.user.surname.charAt(0)}`.toUpperCase()
            const fullName = `${review.user.name} ${review.user.surname}`

            return (
              <div
                key={review.id}
                className="p-6 hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors"
              >
                <div className="flex items-start gap-4">
                  <Avatar className="w-10 h-10 border border-slate-200 dark:border-slate-700">
                    <AvatarImage
                      src={review.user.profile_picture || undefined}
                      alt={fullName}
                    />
                    <AvatarFallback className="bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400 font-medium">
                      {userInitials}
                    </AvatarFallback>
                  </Avatar>

                  <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-center justify-between gap-2 mb-1">
                      <h4 className="text-sm font-semibold text-slate-900 dark:text-slate-100 truncate">
                        {fullName}
                      </h4>
                      <span className="text-xs text-slate-500 dark:text-slate-400 flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {formatShortDate(review.created_at)}
                      </span>
                    </div>

                    <div className="flex items-center mb-2">
                      {[...Array(5)].map((_, i) => (
                        <Star
                          key={i}
                          className={`w-3.5 h-3.5 ${i < review.rating ? 'fill-yellow-400 text-yellow-400' : 'fill-slate-200 text-slate-200 dark:fill-slate-700 dark:text-slate-700'}`}
                        />
                      ))}
                    </div>

                    <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
                      {review.comment}
                    </p>
                  </div>
                </div>
              </div>
            )
          })}
        </div>

        {hasManyReviews && (
          <div className="p-4 border-t border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/20 flex justify-center">
            <Button
              variant="ghost"
              onClick={() => setIsReviewsExpanded(prev => !prev)}
              className="text-slate-600 dark:text-slate-400 hover:text-brand-600 dark:hover:text-brand-400"
            >
              {isReviewsExpanded ? (
                <>
                  <ChevronUp className="w-4 h-4 mr-2" />
                  {t('Згорнути відгуки')}
                </>
              ) : (
                <>
                  <ChevronDown className="w-4 h-4 mr-2" />
                  {t('Показати більше відгуків')}
                </>
              )}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
