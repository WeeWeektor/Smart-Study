import { choicesGetService, type ChoicesResponse } from '@/features/choices-get'

class ChoicesStore {
  private choicesData: ChoicesResponse | null = null
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

  async loadChoices() {
    if (this.loadPromise) {
      return this.loadPromise
    }
    if (this.hasLoaded) {
      return
    }

    this.loadPromise = this.doLoadChoices()

    try {
      await this.loadPromise
    } finally {
      this.loadPromise = null
    }
  }

  private async doLoadChoices() {
    try {
      this.loading = true
      this.error = ''
      this.notify()

      const response = await choicesGetService.getChoices()
      this.choicesData = response
      this.hasLoaded = true
      console.log('Choices завантажено:', response)
    } catch (error) {
      console.error('Помилка завантаження choices:', error)
      this.error = 'Помилка завантаження choices'
    } finally {
      this.loading = false
      this.notify()
    }
  }

  async refreshChoices() {
    this.hasLoaded = false
    await this.loadChoices()
  }

  clearChoices() {
    this.choicesData = null
    this.hasLoaded = false
    this.loading = false
    this.error = ''
    this.notify()
  }

  getChoicesData() {
    return this.choicesData
  }

  isLoading() {
    return this.loading
  }

  getError() {
    return this.error
  }
}

const choicesStore = new ChoicesStore()

import { useEffect, useState } from 'react'

export const useChoicesData = () => {
  const [, forceUpdate] = useState({})

  useEffect(() => {
    const unsubscribe = choicesStore.subscribe(() => {
      forceUpdate({})
    })

    choicesStore.loadChoices()

    return unsubscribe
  }, [])

  return {
    choicesData: choicesStore.getChoicesData(),
    loading: choicesStore.isLoading(),
    error: choicesStore.getError(),
    refreshChoices: () => choicesStore.refreshChoices(),
    clearChoices: () => choicesStore.clearChoices(),
  }
}
