import axios from 'axios'

/**
 * Універсальний обробник помилок API
 * @param error - об'єкт помилки (unknown)
 * @param prefix - префікс, який додається перед повідомленням сервера (напр. 'Не вдалось зберегти: ')
 * @param t - функція перекладу
 * @param defaultErrorMsg - дефолтне повідомлення, якщо помилка не від Axios
 */
export const handleApiError = (
  error: unknown,
  prefix: string,
  t: (key: string) => string,
  defaultErrorMsg: string = 'Невідома помилка'
): Error => {
  if (axios.isAxiosError(error)) {
    let serverMessage =
      error.response?.data?.message ||
      error.response?.data ||
      t('Помилка з’єднання з сервером')

    if (typeof serverMessage === 'string') {
      const match = serverMessage.match(/\['(.+)'\]/)
      if (match && match[1]) {
        serverMessage = match[1]
      }
    }

    throw new Error(t(prefix) + serverMessage)
  }

  throw new Error(t(defaultErrorMsg))
}
