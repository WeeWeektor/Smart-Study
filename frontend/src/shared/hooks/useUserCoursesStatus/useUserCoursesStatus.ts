import { useCallback, useEffect, useState } from 'react'
import { getCourseService } from '@/features/course'

let cachedData: {
  wishlist: Set<string>
  enrolled: Map<string, number>
  completed: Set<string>
} | null = null

let isFetching = false
const listeners: (() => void)[] = []

export const useUserCoursesStatus = () => {
  const [loading, setLoading] = useState(false)
  const [, setTick] = useState(0)

  const fetchData = useCallback(async (force = false) => {
    if ((cachedData && !force) || isFetching) return

    isFetching = true
    setLoading(true)
    try {
      const response = await getCourseService.getMyCourseCatalog()
      cachedData = {
        wishlist: new Set(response.in_wishlist.map(i => i.course.id)),
        enrolled: new Map(
          response.is_enrolled.map(i => {
            const progress = (i.course as any).user_status?.progress || 0
            return [i.course.id, progress]
          })
        ),
        completed: new Set(response.is_completed.map(i => i.course.id)),
      }
      listeners.forEach(l => l())
    } catch (e) {
      console.error('Failed to fetch user courses status', e)
    } finally {
      setLoading(false)
      isFetching = false
    }
  }, [])

  useEffect(() => {
    const listener = () => setTick(t => t + 1)
    listeners.push(listener)

    if (!cachedData) {
      fetchData()
      if (isFetching) setLoading(true)
    }

    return () => {
      const index = listeners.indexOf(listener)
      if (index > -1) listeners.splice(index, 1)
    }
  }, [fetchData])

  const getItemStatus = useCallback((courseId: string) => {
    if (!cachedData)
      return {
        status: undefined,
        progress: 0,
        inWishlist: false,
      }

    let status: 'completed' | 'in_progress' | 'not_started' = 'not_started'
    let progress = 0
    const inWishlist = cachedData.wishlist.has(courseId)

    if (cachedData.completed.has(courseId)) {
      status = 'completed'
      progress = 100
    } else if (cachedData.enrolled.has(courseId)) {
      status = 'in_progress'
      progress = cachedData.enrolled.get(courseId) || 0
    }

    return { status, progress, inWishlist }
  }, [])

  return {
    loading: loading || (!cachedData && isFetching),
    refresh: () => fetchData(true),
    getItemStatus,
  }
}
