import type { LanguageConfig } from './types'

export const SUPPORTED_LANGUAGES: LanguageConfig[] = [
  {
    code: 'en',
    name: 'English',
    nativeName: 'English',
    flag: 'en',
  },
  {
    code: 'uk',
    name: 'Ukrainian',
    nativeName: 'Українська',
    flag: 'ua',
  },
]

export const DEFAULT_LANGUAGE: LanguageConfig = SUPPORTED_LANGUAGES[0]

export const LANGUAGE_STORAGE_KEY = 'smartStudy_language'
