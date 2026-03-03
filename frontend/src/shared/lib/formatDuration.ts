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
  if (!isoDuration) return { days: 0, hours: 0, minutes: 0 }

  if (isoDuration.startsWith('P')) {
    const regex = /P(?:(\d+)D)?T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/
    const matches = isoDuration.match(regex)

    if (matches) {
      return {
        days: matches[1] ? parseInt(matches[1], 10) : 0,
        hours: matches[2] ? parseInt(matches[2], 10) : 0,
        minutes: matches[3] ? parseInt(matches[3], 10) : 0,
      }
    }
  }

  if (isoDuration.includes(':')) {
    const parts = isoDuration.split(':').map(p => parseInt(p, 10) || 0)

    if (parts.length >= 3) {
      return {
        days: parts[0],
        hours: parts[1],
        minutes: parts[2],
      }
    } else if (parts.length === 2) {
      return {
        days: 0,
        hours: parts[0],
        minutes: parts[1],
      }
    }
  }

  if (!isNaN(Number(isoDuration))) {
    return { days: 0, hours: 0, minutes: Number(isoDuration) }
  }

  return { days: 0, hours: 0, minutes: 0 }
}
