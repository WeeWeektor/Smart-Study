import type { TranslationNamespace } from './types'

export function getNestedTranslation(
  obj: TranslationNamespace,
  path: string
): string {
  if (obj && typeof obj === 'object' && path in obj) {
    const value = obj[path]
    if (typeof value === 'string') {
      return value
    }
  }

  const keys = path.split('.')
  let result: any = obj

  for (const key of keys) {
    if (result && typeof result === 'object' && key in result) {
      result = result[key]
    } else {
      return path
    }
  }

  return typeof result === 'string' ? result : path
}

export function interpolate(
  template: string,
  params: Record<string, string | number>
): string {
  return template.replace(/\{(\w+)\}/g, (match, key) => {
    return params[key]?.toString() || match
  })
}
