import { Button } from '@/shared/ui'

interface DeleteAccountButtonProps {
  onDelete: () => void
}

export const DeleteAccountButton = ({ onDelete }: DeleteAccountButtonProps) => {
  return (
    <Button
      variant="destructive"
      className="bg-red-600 hover:bg-red-700"
      onClick={onDelete}
    >
      Видалити акаунт
    </Button>
  )
}
