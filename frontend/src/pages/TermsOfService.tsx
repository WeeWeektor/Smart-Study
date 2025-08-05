import { Link } from 'react-router-dom'
import { Button } from '@/shared/ui'
import { ArrowLeft } from 'lucide-react'
import { AuthLayout } from '@/widgets/auth'
import { TermsOfServiceContent } from '@/widgets/info'

const TermsOfService = () => {
  return (
    <AuthLayout
      headerContent={
        <Link to="/register">
          <Button
            variant="ghost"
            className="text-muted-foreground hover:text-brand-600 dark:hover:text-brand-400"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Назад до реєстрації
          </Button>
        </Link>
      }
    >
      <TermsOfServiceContent />
    </AuthLayout>
  )
}

export default TermsOfService
