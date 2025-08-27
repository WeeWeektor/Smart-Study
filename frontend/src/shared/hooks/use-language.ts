import { useEffect, useState } from 'react'
import type { Language } from '@/shared/lib/i18n/types'
import {
  LANGUAGE_STORAGE_KEY,
  DEFAULT_LANGUAGE,
} from '@/shared/lib/i18n/config'

function setCookie(name: string, value: string, days: number = 365) {
  const expires = new Date()
  expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000)
  document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/;SameSite=Lax`
}

function getCookie(name: string): string | null {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop()?.split(';').shift() || null
  return null
}

export function useLanguage(): [Language, (language: Language) => void] {
  const [language, setLanguage] = useState<Language>(() => {
    const cookieLanguage = getCookie('django_language')
    if (cookieLanguage === 'en' || cookieLanguage === 'uk') {
      return cookieLanguage as Language
    }

    const storedLanguage = localStorage.getItem(LANGUAGE_STORAGE_KEY)
    if (storedLanguage === 'en' || storedLanguage === 'uk') {
      return storedLanguage as Language
    }

    return DEFAULT_LANGUAGE.code
  })

  const changeLanguage = (newLanguage: Language) => {
    setLanguage(newLanguage)

    localStorage.setItem(LANGUAGE_STORAGE_KEY, newLanguage)
    setCookie('django_language', newLanguage)
    document.documentElement.setAttribute('lang', newLanguage)

    window.addEventListener('languageChanged', ((event: CustomEvent) => {
      if (event.detail !== newLanguage) {
        setLanguage(event.detail)
      }
    }) as EventListener)
  }

  useEffect(() => {
    const cookieLanguage = getCookie('django_language')
    if (
      cookieLanguage &&
      cookieLanguage !== language &&
      (cookieLanguage === 'en' || cookieLanguage === 'uk')
    ) {
      setLanguage(cookieLanguage as Language)
    }
  }, [])

  return [language, changeLanguage]
}
