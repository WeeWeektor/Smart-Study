import { useMemo } from 'react'
import { useI18n } from '@/shared/lib'

export type AchievementType = 'gold' | 'silver' | 'bronze'

export interface Achievement {
  id: string
  title: string
  description: string
  icon: string
  date: string
  type: AchievementType
}

export const useAchievements = (rawStats: any) => {
  const { t } = useI18n()

  return useMemo(() => {
    if (!rawStats) return []

    const enrolledList = rawStats.enrolled_list || []
    const completedList = rawStats.completed_list || []
    const wishlistCount = rawStats.wishlist?.size || 0

    const enrolledCount = enrolledList.length
    const completedCount = completedList.length

    const achievements: Achievement[] = []

    if (enrolledCount + completedCount >= 1) {
      achievements.push({
        id: 'enroll-1',
        title: t('Перший крок'),
        description: t('Ви записалися на свій перший курс'),
        icon: '🚀',
        date: new Date(
          enrolledList[0]?.course.user_status.enrolled_at || Date.now()
        ).toLocaleDateString(),
        type: 'bronze',
      })
    }

    if (enrolledCount + completedCount >= 5) {
      achievements.push({
        id: 'enroll-5',
        title: t('Дослідник'),
        description: t('Записано на 5 або більше курсів'),
        icon: '🔍',
        date: '',
        type: 'silver',
      })
    }

    if (completedCount >= 1) {
      achievements.push({
        id: 'complete-1',
        title: t('Перша перемога'),
        description: t('Ви успішно завершили свій перший курс'),
        icon: '🏆',
        date: new Date(
          completedList[0].course.user_status.completed_at
        ).toLocaleDateString(),
        type: 'bronze',
      })
    }

    if (completedCount >= 3) {
      achievements.push({
        id: 'complete-3',
        title: t('Потрійний удар'),
        description: t('Завершено 3 курси'),
        icon: '🥉',
        date: new Date(
          completedList[2].course.user_status.completed_at
        ).toLocaleDateString(),
        type: 'silver',
      })
    }

    if (completedCount >= 5) {
      achievements.push({
        id: 'complete-5',
        title: t('Знавець'),
        description: t('Завершено 5 курсів'),
        icon: '🥈',
        date: new Date(
          completedList[4].course.user_status.completed_at
        ).toLocaleDateString(),
        type: 'silver',
      })
    }

    if (completedCount >= 10) {
      achievements.push({
        id: 'complete-10',
        title: t('Майстер платформи'),
        description: t('Завершено 10 курсів'),
        icon: '🥇',
        date: new Date(
          completedList[9].course.user_status.completed_at
        ).toLocaleDateString(),
        type: 'gold',
      })
    }

    const highScored = completedList.filter(
      (i: any) => i.course.user_status.progress >= 100
    )
    if (highScored.length >= 1) {
      achievements.push({
        id: 'perfect-1',
        title: t('Перфекціоніст'),
        description: t('Завершено курс на всі 100%'),
        icon: '✨',
        date: '',
        type: 'bronze',
      })
    }

    if (wishlistCount >= 10) {
      achievements.push({
        id: 'wishlist-10',
        title: t('Великі плани'),
        description: t('Додано 10 курсів до списку бажань'),
        icon: '📝',
        date: '',
        type: 'bronze',
      })
    }

    return achievements
  }, [rawStats, t])
}
