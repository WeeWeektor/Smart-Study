import { Link } from 'react-router-dom'
import { Button } from '@/shared/ui'
import { ArrowLeft } from 'lucide-react'
import { AuthLayout } from '@/widgets/auth'
import { PrivacyPolicyContent } from '@/widgets/info'
import { useI18n } from '@/shared/lib'

const PrivacyPolicy = () => {
  const { t } = useI18n()
  return (
    <AuthLayout
      headerContent={
        <Link to="/register">
          <Button
            variant="ghost"
            className="text-muted-foreground hover:text-brand-600 dark:hover:text-brand-400"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            {t('Назад до реєстрації')}
          </Button>
        </Link>
      }
    >
      <PrivacyPolicyContent />
    </AuthLayout>
  )
}

export default PrivacyPolicy
