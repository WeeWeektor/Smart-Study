import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function getInitials(name: string, surname: string) {
  const firstLetter = name.charAt(0).toUpperCase()
  const lastLetter = surname.charAt(0).toUpperCase()
  return firstLetter + lastLetter
}

export function getAchievementColor(type: string) {
  switch (type) {
    case 'gold':
      return 'bg-yellow-100 text-yellow-800'
    case 'silver':
      return 'bg-gray-100 text-gray-800'
    case 'bronze':
      return 'bg-orange-100 text-orange-800'
    default:
      return 'bg-blue-100 text-blue-800'
  }
}
