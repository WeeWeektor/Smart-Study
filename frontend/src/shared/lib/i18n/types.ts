export type Language = 'en' | 'uk'

export interface LanguageConfig {
  code: Language
  name: string
  nativeName: string
  flag: string
}

export interface TranslationNamespace {
  [key: string]: string | TranslationNamespace
}

export interface Translations {
  [namespace: string]: TranslationNamespace
}

export interface FlatTranslations {
  [key: string]: string
}
