import { useEffect, useState } from 'react'
import { type ProfileData, profileService } from '@/entities/profile'

class ProfileStore {
  private profileData: ProfileData | null = null
  private loading = false
  private error = ''
  private listeners: Array<() => void> = []
  private hasLoaded = false
  private loadPromise: Promise<void> | null = null
  private statsLoaded = false
  private learningStats: {
    coursesCompleted: number
    coursesInProgress: number
    totalTests: number
    completedTopics: number
    certificates: number
  }
  private statsPromise: Promise<void> | null = null
  private isProfileFetching = false
  private isStatsFetching = false

  subscribe(listener: () => void) {
    this.listeners.push(listener)
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener)
    }
  }

  private notify() {
    this.listeners.forEach(listener => listener())
  }

  private async doLoadProfile() {
    if (this.loading) return
    if (this.isProfileFetching) return
    this.isProfileFetching = true

    try {
      this.loading = true
      this.error = ''
      this.notify()

      const response = await profileService.getProfile()

      if (response.status === 'success' && response.data) {
        this.profileData = response.data
        this.hasLoaded = true

        await this.loadLearningStats()
        console.log('Профіль завантажено:', response.data)
      } else {
        this.error = 'Не вдалося завантажити профіль'
      }
    } catch (error) {
      console.error('Помилка завантаження профілю:', error)
      this.error = 'Помилка завантаження профілю'
    } finally {
      this.loading = false
      this.isProfileFetching = false
      this.notify()
    }
  }

  async loadLearningStats() {
    if (this.isStatsFetching) return
    if (this.isStatsFetching || (this.statsLoaded && !this.statsPromise)) return

    if (this.statsPromise) return this.statsPromise

    this.isStatsFetching = true

    this.statsPromise = (async () => {
      try {
        const response = await profileService.getLearningStats()
        if (response.status === 'success' && response.data) {
          this.learningStats = { ...this.learningStats, ...response.data }
          this.statsLoaded = true
          console.log('Статистику оновлено:', this.learningStats)
          this.notify()
        }
      } catch (error) {
        console.error('Помилка завантаження статистики:', error)
      } finally {
        this.statsPromise = null
        this.isStatsFetching = false
      }
    })()

    return this.statsPromise
  }

  async loadProfile() {
    if (this.loadPromise) {
      return this.loadPromise
    }

    if (this.hasLoaded || this.loading) return

    this.loadPromise = this.doLoadProfile()

    try {
      await this.loadPromise
    } finally {
      this.loadPromise = null
    }
  }

  stopLoading() {
    this.loading = false
    this.isProfileFetching = false
    this.notify()
  }

  async refreshProfile() {
    this.hasLoaded = false
    await this.loadProfile()
  }

  updateProfile(newProfileData: ProfileData) {
    this.profileData = newProfileData
    this.notify()
  }

  clearProfile() {
    this.profileData = null
    this.hasLoaded = false
    this.loading = false
    this.error = ''
    this.notify()
  }

  async refreshStats() {
    this.statsLoaded = false
    await this.loadLearningStats()
  }

  getLearningStats() {
    return this.learningStats
  }

  getProfileData() {
    return this.profileData
  }

  isLoading() {
    return this.loading
  }

  getError() {
    return this.error
  }
}

const profileStore = new ProfileStore()

export const useProfileData = () => {
  const [, forceUpdate] = useState({})

  useEffect(() => {
    const unsubscribe = profileStore.subscribe(() => {
      forceUpdate({})
    })

    const hasSession =
      document.cookie.includes('sessionid') ||
      document.cookie.includes('csrftoken') ||
      localStorage.getItem('token')

    if (!hasSession) {
      profileStore.stopLoading()
    } else {
      if (!profileStore.getProfileData() && !profileStore.isLoading()) {
        profileStore.loadProfile()
      }
    }

    return unsubscribe
  }, [])

  return {
    profileData: profileStore.getProfileData(),
    loading: profileStore.isLoading(),
    error: profileStore.getError(),
    learningStats: profileStore.getLearningStats(),
    refreshProfile: () => profileStore.refreshProfile(),
    updateProfile: (data: ProfileData) => profileStore.updateProfile(data),
    refreshStats: () => profileStore.refreshStats(),
    clearProfile: () => profileStore.clearProfile(),
  }
}
