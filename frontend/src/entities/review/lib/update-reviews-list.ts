import type { Review } from '@/features/course'

/**
 * Додає новий відгук на початок списку або оновлює існуючий, якщо ID збігаються.
 */
export const updateReviewsList = (
  currentReviews: Review[],
  incomingReview: Review
): Review[] => {
  const existingIndex = currentReviews.findIndex(
    r => r.id === incomingReview.id
  )

  if (existingIndex !== -1) {
    const updatedList = [...currentReviews]
    updatedList[existingIndex] = incomingReview
    return updatedList
  } else {
    return [incomingReview, ...currentReviews]
  }
}
