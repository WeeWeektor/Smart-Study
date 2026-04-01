export const getFormattedTime = (language: string) => {
  const locale =
    language === 'ua' ? 'uk-UA' : language === 'en' ? 'en-US' : 'uk-UA'

  return new Date().toLocaleTimeString(locale, {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  })
}
