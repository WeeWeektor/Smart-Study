import { Button } from '@/shared/ui'
import { Edit, Loader2, Save, User } from 'lucide-react'
import { useI18n } from '@/shared/lib'
import { EditableHeader } from '@/shared/ui'

interface ProfileHeaderProps {
  isEditing: boolean
  isSaving: boolean
  onEdit: () => void
  onSave: () => void
  onCancel: () => void
  disabledSave?: boolean
  is_user_login?: boolean
}

export const ProfileHeader = ({
  isEditing,
  isSaving,
  onEdit,
  onSave,
  onCancel,
  disabledSave,
  is_user_login = true,
}: ProfileHeaderProps) => {
  const { t } = useI18n()

  const actions = (
    <>
      {isEditing ? (
        <div className="flex space-x-2">
          <Button variant="outline" onClick={onCancel} disabled={isSaving}>
            {t('Скасувати')}
          </Button>
          <Button
            className="bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 text-white"
            onClick={onSave}
            disabled={isSaving || disabledSave}
          >
            {isSaving ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                {t('Збереження...')}
              </>
            ) : (
              <>
                <Save className="w-4 h-4 mr-2" />
                {t('Зберегти')}
              </>
            )}
          </Button>
        </div>
      ) : (
        <Button
          className="bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 text-white"
          onClick={onEdit}
        >
          <Edit className="w-4 h-4 mr-2" />
          {t('Редагувати')}
        </Button>
      )}
    </>
  )

  return (
    <EditableHeader
      title={t('Мій профіль')}
      description={t('Керуйте своїм профілем та налаштуваннями')}
      icon={<User className="w-6 h-6 text-brand-600 dark:text-brand-400" />}
      actions={actions}
      is_user_login={is_user_login}
    />
  )
}
