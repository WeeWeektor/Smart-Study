export function parseISODuration(
  duration: string,
  t: (s: string) => string
): string {
  const match = duration.match(/P(?:(\d+)D)?T(?:(\d+)H)?(?:(\d+)M)?/)

  if (!match) return duration

  const [, days, hours, minutes] = match

  const parts: string[] = []
  if (days && Number(days) > 0) parts.push(`${Number(days)} ${t('дн.')}`)
  if (hours && Number(hours) > 0) parts.push(`${Number(hours)} ${t('год.')}`)
  if (minutes && Number(minutes) > 0)
    parts.push(`${Number(minutes)} ${t('хв.')}`)

  return parts.length > 0 ? parts.join(' ') : `0 ${t('хв.')}`
}
