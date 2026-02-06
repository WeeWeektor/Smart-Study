import type { Review } from '@/features/course'
import { getReviewStats } from '@/entities/review/lib/get-review-stats.ts'
import { useMemo } from 'react'

export const useReviewStats = (reviews: Review[]) => {
  return useMemo(() => getReviewStats(reviews), [reviews])
}
