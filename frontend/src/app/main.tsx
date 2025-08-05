import './index.css'
import { createRoot } from 'react-dom/client'
import App from './App'

const initializeTheme = () => {
  const storedTheme = localStorage.getItem('theme')
  const theme = storedTheme === 'dark' ? 'dark' : 'light'

  if (theme === 'dark') {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

initializeTheme()

createRoot(document.getElementById('root')!).render(<App />)
