import { EmailVerificationNotification } from '@/features/email-verification-notification'
import { LogoutSuccessNotification } from '@/features/logout'
import { DeleteAccountSuccessNotification } from '@/features/delete-account'
import { useUrlParamNotification } from '@/shared/hooks/use-url-param-notification'
import { ThemeToggle } from '@/shared/ui/theme-toggle'
import { useI18n } from '@/shared/lib'

const Index = () => {
  const [showEmailVerification, hideEmailVerification] =
    useUrlParamNotification('showEmailVerification')
  const [showLogoutSuccess, hideLogoutSuccess] =
    useUrlParamNotification('showLogoutSuccess')
  const [showDeleteAccountSuccess, hideDeleteAccountSuccess] =
    useUrlParamNotification('showDeleteAccountSuccess')

  const { t } = useI18n()
  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-foreground">
            {t('Ласкаво просимо до Smart Study')}
          </h1>
          <ThemeToggle variant="secondary" size="default" />
        </div>
        <p className="text-lg text-muted-foreground mb-8">
          {t('Це головна сторінка програми.')}
        </p>

        {showEmailVerification && (
          <EmailVerificationNotification onClose={hideEmailVerification} />
        )}

        {showLogoutSuccess && (
          <LogoutSuccessNotification onClose={hideLogoutSuccess} />
        )}

        {showDeleteAccountSuccess && (
          <DeleteAccountSuccessNotification
            onClose={hideDeleteAccountSuccess}
          />
        )}
      </div>
    </div>
  )
}

export default Index
