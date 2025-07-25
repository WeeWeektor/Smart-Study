import { useEffect, useState } from 'react'
import { authService } from '../../auth/auth.service'
import { tokenService } from '../../../shared/api/token-manager'

interface UseSocialAuthProps {
	onError?: (msg: string) => void
}

export function useSocialAuth({ onError }: UseSocialAuthProps) {
	const [showExtraFields, setShowExtraFields] = useState(false)
	const [extraFields, setExtraFields] = useState({
		role: '',
		surname: '',
		name: '',
		phone_number: '',
		credential: '',
	})

	useEffect(() => {
		// @ts-ignore
		if (window.google) {
			// @ts-ignore
			window.google.accounts.id.initialize({
				client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
				callback: handleGoogleResponse,
			})
		}
		// eslint-disable-next-line
	}, [])

	const setErrorWithProp = (msg: string) => {
		if (onError) onError(msg)
	}

	const handleGoogleResponse = async (response: any) => {
		if (onError) onError('')
		try {
			const res = await authService.googleOAuth({
				credential: response.credential,
			})
			if (res.access) {
				tokenService.setToken(res.access)
			}
			if (res.refresh) {
				tokenService.setRefreshToken(res.refresh)
			}
			window.location.href = '/'
		} catch (e: any) {
			if (
				e.response &&
				e.response.data &&
				e.response.data.error?.includes('role')
			) {
				setExtraFields({
					...extraFields,
					credential: response.credential,
				})
				setShowExtraFields(true)
			} else {
				setErrorWithProp(
					e.response?.data?.error || 'Помилка Google авторизації'
				)
			}
		}
	}

	const handleExtraFieldsChange = (field: string, value: string) => {
		setExtraFields(prev => ({ ...prev, [field]: value }))
	}

	const handleExtraFieldsSubmit = async (e: React.FormEvent) => {
		e.preventDefault()
		if (onError) onError('')
		if (!extraFields.role || !extraFields.surname || !extraFields.name) {
			setErrorWithProp('Всі поля, крім телефону, обовʼязкові')
			return
		}
		try {
			const res = await authService.googleOAuth({
				credential: extraFields.credential,
				role: extraFields.role,
				surname: extraFields.surname,
				name: extraFields.name,
				phone_number: extraFields.phone_number,
			})
			if (res.access) {
				tokenService.setToken(res.access)
			}
			if (res.refresh) {
				tokenService.setRefreshToken(res.refresh)
			}
			window.location.href = '/'
		} catch (e: any) {
			setErrorWithProp(e.response?.data?.error || 'Помилка Google авторизації')
		}
	}

	const handleGoogleClick = () => {
		// @ts-ignore
		if (window.google) {
			// @ts-ignore
			window.google.accounts.id.prompt()
		}
	}

	const handleFacebookClick = () => {
		setErrorWithProp('Facebook авторизація ще не реалізована')
	}

	return {
		showExtraFields,
		extraFields,
		handleExtraFieldsChange,
		handleExtraFieldsSubmit,
		handleGoogleClick,
		handleFacebookClick,
	}
}
