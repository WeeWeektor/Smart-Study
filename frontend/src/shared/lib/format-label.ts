export function formatLabel(label: string, t: (key: string) => string): string {
  if (!label) return ''

  const words = label.split('_')
  const capitalizedWords = words.map(word =>
    word ? word[0].toUpperCase() + word.slice(1) : ''
  )
  const joined = capitalizedWords.join(' ')

  return t(joined)
}
