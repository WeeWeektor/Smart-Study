import { translations } from './translations'
import { getNestedTranslation, interpolate } from './utils'
import { LANGUAGE_STORAGE_KEY, DEFAULT_LANGUAGE } from './config'
import type { Language } from './types'

export class ClassTranslator {
  private static getLanguage(): Language {
    const storedLanguage = localStorage.getItem(LANGUAGE_STORAGE_KEY)
    return storedLanguage === 'en' || storedLanguage === 'uk'
      ? (storedLanguage as Language)
      : DEFAULT_LANGUAGE.code
  }

  static translate(
    key: string,
    params?: Record<string, string | number>
  ): string {
    try {
      const language = this.getLanguage()
      const template = getNestedTranslation(translations[language], key)
      return params ? interpolate(template, params) : template
    } catch {
      return key
    }
  }

  static t = this.translate
}
