import { Button } from '@/shared/ui'
import { useI18n } from '@/shared/lib'

interface DeleteAccountButtonProps {
  onDelete: () => void
}

export const DeleteAccountButton = ({ onDelete }: DeleteAccountButtonProps) => {
  const { t } = useI18n()
  return (
    <Button
      variant="destructive"
      className="bg-destructive text-destructive-foreground hover:bg-destructive-hover"
      onClick={onDelete}
    >
      {t('Видалити акаунт')}
    </Button>
  )
}
