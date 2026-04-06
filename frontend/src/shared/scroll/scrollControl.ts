let modalCount = 0

export const disablePageScroll = (): void => {
  modalCount++

  if (modalCount === 1) {
    document.body.dataset.scrollDisabled = 'true'
    document.body.style.overflow = 'hidden'
  }
}

export const enablePageScroll = (): void => {
  if (modalCount > 0) modalCount--

  if (modalCount === 0) {
    delete document.body.dataset.scrollDisabled
    document.body.style.overflow = ''
  }
}

export const resetScrollLock = (): void => {
  modalCount = 0
  delete document.body.dataset.scrollDisabled
  document.body.style.overflow = ''
}
