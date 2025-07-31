import { EmailVerificationNotification } from '@/features/email-verification-notification'
import { LogoutSuccessNotification } from '@/features/logout'
import { DeleteAccountSuccessNotification } from '@/features/delete-account'
import { useUrlParamNotification } from '@/shared/hooks/use-url-param-notification'

const Index = () => {
	const [showEmailVerification, hideEmailVerification] =
		useUrlParamNotification('showEmailVerification')
	const [showLogoutSuccess, hideLogoutSuccess] =
		useUrlParamNotification('showLogoutSuccess')
	const [showDeleteAccountSuccess, hideDeleteAccountSuccess] =
		useUrlParamNotification('showDeleteAccountSuccess')

	return (
		<div>
			<h1 className="text-xl font-bold">Welcome to the Index Page</h1>
			<p className="mt-2">This is the main page of the application.</p>

			{showEmailVerification && (
				<EmailVerificationNotification onClose={hideEmailVerification} />
			)}

			{showLogoutSuccess && (
				<LogoutSuccessNotification onClose={hideLogoutSuccess} />
			)}

			{showDeleteAccountSuccess && (
				<DeleteAccountSuccessNotification onClose={hideDeleteAccountSuccess} />
			)}
		</div>
	)
}

export default Index
