import { useEffect, useState } from 'react'
import type { Language } from '@/shared/lib/i18n/types'
import {
  LANGUAGE_STORAGE_KEY,
  DEFAULT_LANGUAGE,
} from '@/shared/lib/i18n/config'

export function useLanguage(): [Language, (language: Language) => void] {
  const [language, setLanguage] = useState<Language>(() => {
    const storedLanguage = localStorage.getItem(LANGUAGE_STORAGE_KEY)
    const isSupported = storedLanguage === 'en' || storedLanguage === 'uk'
    return isSupported ? (storedLanguage as Language) : DEFAULT_LANGUAGE.code
  })

  useEffect(() => {
    localStorage.setItem(LANGUAGE_STORAGE_KEY, language)
    document.documentElement.setAttribute('lang', language)
  }, [language])

  return [language, setLanguage]
}
