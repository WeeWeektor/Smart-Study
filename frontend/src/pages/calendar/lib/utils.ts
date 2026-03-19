export const getImportanceColor = (importance: string) => {
  switch (importance) {
    case 'high':
      return 'bg-red-500 text-white'
    case 'medium':
      return 'bg-amber-500 text-white'
    case 'low':
      return 'bg-green-500 text-white'
    default:
      return 'bg-brand-500 text-white'
  }
}

export const getImportanceColorText = (importance: string) => {
  switch (importance) {
    case 'high':
      return 'text-red-500'
    case 'medium':
      return 'text-amber-500'
    case 'low':
      return 'text-green-500'
    default:
      return 'text-brand-500'
  }
}

export const getImportanceColorBackground = (
  importance: string,
  style?: number
) => {
  switch (importance) {
    case 'high':
      if (style === 2) {
        return 'bg-red-100 dark:bg-red-900/30'
      }
      return 'bg-red-50 dark:bg-red-900/10 border-red-100 dark:border-red-900/50'
    case 'medium':
      if (style === 2) {
        return 'bg-amber-100 dark:bg-amber-900/30'
      }
      return 'bg-amber-50 dark:bg-amber-900/10 border-amber-100 dark:border-amber-900/50'
    case 'low':
      if (style === 2) {
        return 'bg-green-100 dark:bg-green-900/30'
      }
      return 'bg-green-50 dark:bg-green-900/10 border-green-100 dark:border-green-900/50'
    default:
      if (style === 2) {
        return 'bg-brand-100 dark:bg-brand-900/30'
      }
      return 'bg-brand-50 dark:bg-brand-900/10 border-brand-100 dark:border-brand-900/50'
  }
}
