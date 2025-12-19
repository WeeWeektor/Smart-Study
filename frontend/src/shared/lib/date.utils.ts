export const formatDate = (dateString: string | undefined | null): string => {
  if (!dateString) return ''

  const date = new Date(dateString)

  if (isNaN(date.getTime())) return ''

  return new Intl.DateTimeFormat('uk-UA', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  }).format(date)
}

export const formatShortDate = (
  dateString: string | undefined | null
): string => {
  if (!dateString) return ''
  const date = new Date(dateString)
  if (isNaN(date.getTime())) return ''

  return new Intl.DateTimeFormat('uk-UA', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(date)
}
