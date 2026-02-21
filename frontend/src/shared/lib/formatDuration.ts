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

export const formatDurationForBackend = (
  days: number,
  hours: number,
  minutes: number
): string => {
  const padTwoDigits = (num: number): string => num.toString().padStart(2, '0')
  return `${padTwoDigits(days)}:${padTwoDigits(hours)}:${padTwoDigits(minutes)}`
}

export const parseDurationFromISO = (isoDuration: string) => {
  const regex = /P(?:(\d+)D)?T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/
  const matches = isoDuration.match(regex)

  if (!matches) return { days: 0, hours: 0, minutes: 0 }

  return {
    days: matches[1] ? parseInt(matches[1], 10) : 0,
    hours: matches[2] ? parseInt(matches[2], 10) : 0,
    minutes: matches[3] ? parseInt(matches[3], 10) : 0,
  }
}
