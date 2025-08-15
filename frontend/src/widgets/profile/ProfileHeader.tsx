import { Button } from '@/shared/ui'
import { Loader2, Save, Edit, User, Bell } from 'lucide-react'
import { ThemeToggle } from '@/shared/ui'
import { useI18n } from '@/shared/lib'

interface ProfileHeaderProps {
  isEditing: boolean
  isSaving: boolean
  onEdit: () => void
  onSave: () => void
  onCancel: () => void
  disabledSave?: boolean
}

export const ProfileHeader = ({
  isEditing,
  isSaving,
  onEdit,
  onSave,
  onCancel,
  disabledSave,
}: ProfileHeaderProps) => {
  const { t } = useI18n()
  return (
    <header className="bg-card border-b border-border text-card-foreground">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold flex items-center text-foreground">
              <User className="w-6 h-6 mr-2 text-brand-600 dark:text-brand-400" />
              {t('Мій профіль')}
            </h1>
            <p className="text-muted-foreground">
              {t('Керуйте своїм профілем та налаштуваннями')}
            </p>
          </div>
          <div className="flex items-center space-x-4">
            {isEditing ? (
              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  onClick={onCancel}
                  disabled={isSaving}
                >
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
            <ThemeToggle variant="secondary" size="default" />
            <Button variant="ghost" size="sm" className="relative">
              <Bell className="w-5 h-5" />
              <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></span>
            </Button>
          </div>
        </div>
      </div>
    </header>
  )
}
