import { LogOut } from 'lucide-react'
import { Button } from '@/shared/ui'
import { authService } from '../auth'

export const LogoutButton = () => {
  const handleLogout = async () => {
    try {
      await authService.logout()
      window.location.assign('/?showLogoutSuccess=true')
    } catch (error) {
      console.error('Logout failed:', error)
      window.location.assign('/?showLogoutSuccess=true')
    }
  }

  return (
    <Button variant="ghost" size="sm" onClick={handleLogout}>
      <LogOut className="w-4 h-4" />
    </Button>
  )
}
