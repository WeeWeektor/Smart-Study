import { Button } from '@/shared/ui'

interface DeleteAccountButtonProps {
  onDelete: () => void
}

export const DeleteAccountButton = ({ onDelete }: DeleteAccountButtonProps) => {
  return (
    <Button
      variant="destructive"
      className="bg-destructive text-destructive-foreground hover:bg-destructive-hover"
      onClick={onDelete}
    >
      Видалити акаунт
    </Button>
  )
}
