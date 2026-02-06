import type { Review } from '@/features/course'

export interface ReviewStats {
  averageRating: number
  distribution: Record<string, number>
}

export const getReviewStats = (reviews: Review[]): ReviewStats => {
  const totalReviews = reviews.length

  const initialDistribution: Record<string, number> = {
    1: 0,
    2: 0,
    3: 0,
    4: 0,
    5: 0,
  }

  if (!reviews || totalReviews === 0) {
    return {
      averageRating: 0,
      distribution: initialDistribution,
    }
  }

  const sum = reviews.reduce((acc, review) => acc + review.rating, 0)
  const averageRating = sum / totalReviews

  const distribution = { ...initialDistribution }

  reviews.forEach(review => {
    const ratingKey = Math.round(review.rating)
    if (distribution[ratingKey] !== undefined) {
      distribution[ratingKey] += 1
    }
  })

  return { averageRating, distribution }
}
