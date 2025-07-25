import { EmailVerificationNotification } from '@/features/email-verification-notification'
import { useUrlParamNotification } from '@/shared/hooks/use-url-param-notification'

const Index = () => {
  const [showEmailVerification, hideEmailVerification] =
    useUrlParamNotification('showEmailVerification')

  return (
    <div>
      <h1 className="text-xl font-bold">Welcome to the Index Page</h1>
      <p className="mt-2">This is the main page of the application.</p>

      {showEmailVerification && (
        <EmailVerificationNotification onClose={hideEmailVerification} />
      )}
    </div>
  )
}

export default Index
