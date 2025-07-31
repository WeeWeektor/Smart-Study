import { useNavigate } from 'react-router-dom'
import { LogOut } from 'lucide-react'
import { Button } from '@/shared/ui'
import { authService } from '../auth'

export const LogoutButton = () => {
  const navigate = useNavigate()

  const handleLogout = async () => {
    try {
      await authService.logout()
      navigate('/')
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  return (
    <Button variant="ghost" size="sm" onClick={handleLogout}>
      <LogOut className="w-4 h-4" />
    </Button>
  )
}
