import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'

export const useUrlParamNotification = (
  paramName: string,
  autoHideTime: number = 8000
): [boolean, () => void] => {
  const [searchParams] = useSearchParams()
  const [showNotification, setShowNotification] = useState(false)

  useEffect(() => {
    const shouldShowNotification = searchParams.get(paramName) === 'true'

    if (shouldShowNotification) {
      setShowNotification(true)

      const newUrl = window.location.pathname
      window.history.replaceState({}, document.title, newUrl)

      const timer = setTimeout(() => {
        setShowNotification(false)
      }, autoHideTime)

      return () => clearTimeout(timer)
    }
  }, [searchParams, paramName, autoHideTime])

  const hideNotification = () => setShowNotification(false)

  return [showNotification, hideNotification]
}
