import { useEffect, useState } from 'react'
import { type ProfileData, profileService } from '@/entities/profile'

class ProfileStore {
  private profileData: ProfileData | null = null
  private loading = false
  private error = ''
  private listeners: Array<() => void> = []
  private hasLoaded = false
  private loadPromise: Promise<void> | null = null

  subscribe(listener: () => void) {
    this.listeners.push(listener)
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener)
    }
  }

  private notify() {
    this.listeners.forEach(listener => listener())
  }

  async loadProfile() {
    if (this.loadPromise) {
      return this.loadPromise
    }

    if (this.hasLoaded) {
      return
    }

    this.loadPromise = this.doLoadProfile()

    try {
      await this.loadPromise
    } finally {
      this.loadPromise = null
    }
  }

  private async doLoadProfile() {
    try {
      this.loading = true
      this.error = ''
      this.notify()

      const response = await profileService.getProfile()

      if (response.status === 'success' && response.data) {
        this.profileData = response.data
        this.hasLoaded = true
        console.log('Профіль завантажено:', response.data)
      } else {
        this.error = 'Не вдалося завантажити профіль'
      }
    } catch (error) {
      console.error('Помилка завантаження профілю:', error)
      this.error = 'Помилка завантаження профілю'
    } finally {
      this.loading = false
      this.notify()
    }
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

    profileStore.loadProfile()

    return unsubscribe
  }, [])

  return {
    profileData: profileStore.getProfileData(),
    loading: profileStore.isLoading(),
    error: profileStore.getError(),
    refreshProfile: () => profileStore.refreshProfile(),
    updateProfile: (data: ProfileData) => profileStore.updateProfile(data),
    clearProfile: () => profileStore.clearProfile(),
  }
}
