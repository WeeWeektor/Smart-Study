type ValidationResult = {
  isValid: boolean
  errorMessage: string | null
}

type ValidationOptions = {
  file: File | undefined
  maxSizeMB: number
  acceptedTypes?: string[]
}

export const validateFile = ({
  file,
  maxSizeMB,
  acceptedTypes,
}: ValidationOptions): ValidationResult => {
  if (!file) {
    return {
      isValid: false,
      errorMessage: null,
    }
  }

  if (acceptedTypes && acceptedTypes.length > 0) {
    const fileType = file.type

    const isTypeValid = acceptedTypes.some(allowedType => {
      if (allowedType.endsWith('/*')) {
        const baseType = allowedType.slice(0, -2) // "image"
        return fileType.startsWith(baseType)
      }
      return fileType === allowedType
    })

    if (!isTypeValid) {
      return {
        isValid: false,
        errorMessage: 'Невірний формат файлу',
      }
    }
  }

  const maxSizeBytes = maxSizeMB * 1024 * 1024
  if (file.size > maxSizeBytes) {
    return {
      isValid: false,
      errorMessage: `Файл занадто великий (макс. ${maxSizeMB} МБ)`,
    }
  }

  return {
    isValid: true,
    errorMessage: null,
  }
}

type CodeValidationResult = {
  isValid: boolean
  errorKey: 'empty_lang' | 'empty_code' | null
}

export const validateCodeBlock = (
  language: string,
  code: string
): CodeValidationResult => {
  if (!language || language.trim().length === 0) {
    return {
      isValid: false,
      errorKey: 'empty_lang',
    }
  }

  if (!code || code.trim().length === 0) {
    return {
      isValid: false,
      errorKey: 'empty_code',
    }
  }

  return {
    isValid: true,
    errorKey: null,
  }
}

type UrlValidationResult = {
  isValid: boolean
  errorKey: 'empty' | 'invalid_format' | null
}

export const validateUrl = (url: string): UrlValidationResult => {
  if (!url || url.trim().length === 0) {
    return {
      isValid: false,
      errorKey: 'empty',
    }
  }

  try {
    new URL(url)
    return {
      isValid: true,
      errorKey: null,
    }
  } catch (_) {
    return {
      isValid: false,
      errorKey: 'invalid_format',
    }
  }
}

type TextValidationResult = {
  isValid: boolean
  errorKey: 'empty' | null
}

export const validateText = (text: string): TextValidationResult => {
  if (!text || text.trim().length === 0) {
    return {
      isValid: false,
      errorKey: 'empty',
    }
  }

  return {
    isValid: true,
    errorKey: null,
  }
}
