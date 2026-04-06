import { en } from './en'
import { uk } from './uk'
import type { Language, Translations } from '../types'

export const translations: Record<Language, Translations> = {
  en,
  uk,
}

export { en, uk }
