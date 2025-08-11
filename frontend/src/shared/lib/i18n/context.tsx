import { createContext, useContext, type ReactNode } from 'react'
import { useLanguage } from '@/shared/hooks/use-language'
import { translations } from './translations'
import { getNestedTranslation, interpolate } from './utils'
import type { Language, TranslationNamespace } from './types'

interface I18nContextType {
  language: Language
  setLanguage: (language: Language) => void
  t: (key: string, params?: Record<string, string | number>) => string
  tNamespace: (namespace: string) => TranslationNamespace
}

const I18nContext = createContext<I18nContextType | undefined>(undefined)

interface I18nProviderProps {
  children: ReactNode
}

export function I18nProvider({ children }: I18nProviderProps) {
  const [language, setLanguage] = useLanguage()

  const t = (key: string, params?: Record<string, string | number>): string => {
    const translation = getNestedTranslation(translations[language], key)
    return params ? interpolate(translation, params) : translation
  }

  const tNamespace = (namespace: string): TranslationNamespace => {
    return translations[language]?.[namespace] || {}
  }

  const value: I18nContextType = {
    language,
    setLanguage,
    t,
    tNamespace,
  }

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>
}

export function useI18n(): I18nContextType {
  const context = useContext(I18nContext)
  if (!context) {
    throw new Error('useI18n must be used within an I18nProvider')
  }
  return context
}
