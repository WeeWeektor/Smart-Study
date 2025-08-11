import { useSocialAuth } from './model/useSocialAuth'
import { Button } from '@/shared/ui'
import { useI18n } from '@/shared/lib'

export const SocialAuth = ({
  onError,
  onSocialDataReceived,
  onUserExists,
}: {
  onError?: (msg: string) => void
  onSocialDataReceived?: (data: {
    name: string
    surname: string
    email: string
    credential: string
    provider: 'google' | 'facebook'
  }) => void
  onUserExists?: (userData: {
    access?: string
    refresh?: string
    user?: any
    message?: string
  }) => void
}) => {
  const { t } = useI18n()
  const {
    isGoogleLoading,
    isFacebookLoading,
    handleGoogleClick,
    handleFacebookClick,
  } = useSocialAuth({ onError, onSocialDataReceived, onUserExists })

  return (
    <div>
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-border" />
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="px-2 bg-card text-muted-foreground">
            {t('auth.orLoginWith')}
          </span>
        </div>
      </div>
      <div className="mt-6 grid grid-cols-2 gap-3">
        <Button
          type="button"
          variant="outline"
          className="border-border text-foreground flex items-center justify-center w-full"
          onClick={handleGoogleClick}
          disabled={isGoogleLoading}
        >
          {isGoogleLoading ? (
            <div className="flex items-center">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-muted-foreground mr-2"></div>
              {t('common.loading')}
            </div>
          ) : (
            <>
              <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                <path
                  fill="currentColor"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="currentColor"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="currentColor"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="currentColor"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              Google
            </>
          )}
        </Button>
        <Button
          type="button"
          variant="outline"
          className="border-border text-foreground flex items-center justify-center w-full"
          onClick={handleFacebookClick}
          disabled={isFacebookLoading}
        >
          {isFacebookLoading ? (
            <div className="flex items-center">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-muted-foreground mr-2"></div>
              {t('common.loading')}
            </div>
          ) : (
            <>
              <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                <path
                  fill="#1877F2"
                  d="M22.675 0h-21.35C.595 0 0 .592 0 1.326v21.348C0 23.408.595 24 1.325 24h11.495v-9.294H9.692v-3.622h3.128V8.413c0-3.1 1.893-4.788 4.659-4.788 1.325 0 2.463.099 2.797.143v3.24l-1.918.001c-1.504 0-1.797.715-1.797 1.763v2.313h3.587l-.467 3.622h-3.12V24h6.116C23.406 24 24 23.408 24 22.674V1.326C24 .592 23.406 0 22.675 0"
                />
                <path
                  fill="#FFF"
                  d="M16.671 24v-9.294h3.12l.467-3.622h-3.587V8.771c0-1.048.293-1.763 1.797-1.763l1.918-.001v-3.24c-.334-.044-1.472-.143-2.797-.143-2.766 0-4.659 1.688-4.659 4.788v2.13H9.692v3.622h3.128V24h3.851"
                />
              </svg>
              Facebook
            </>
          )}
        </Button>
      </div>
    </div>
  )
}
