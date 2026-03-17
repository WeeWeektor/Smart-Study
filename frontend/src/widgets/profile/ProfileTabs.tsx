import {
  Badge,
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Checkbox,
  LanguageSwitcher,
  Progress,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/shared/ui'
import { EditProfileForm } from '@/features/edit-profile'
import { DeleteAccountButton } from '@/features/delete-account'
import { CheckCircle, RotateCw } from 'lucide-react'
import { getAchievementColor } from '@/shared/lib/utils'
import React, { useMemo, useState } from 'react'
import { PasswordField } from '@/shared/ui/password-field'
import { FormAlert } from '@/shared/ui/form-alert'
import { profileService } from '@/entities/profile/profile.service'
import { useI18n } from '@/shared/lib'
import { useUserCoursesStatus } from '@/shared/hooks/useUserCoursesStatus'
import { useAchievements } from '@/entities/profile/model'

interface ProfileTabsProps {
  formData: any
  isEditing: boolean
  onFormChange: (field: string, value: string) => void
  onSettingsChange: (field: string, value: boolean) => void
  onDeleteAccount: () => void
}

function NotificationsBlock({ formData, onSettingsChange, isEditing }: any) {
  const { t } = useI18n()
  return (
    <div className="bg-card rounded-lg shadow p-6 mb-6 border border-border">
      <h3 className="font-medium text-foreground mb-4">{t('Сповіщення')}</h3>
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-muted-foreground">{t('Email сповіщення')}</span>
          <Checkbox
            checked={formData.email_notifications}
            onCheckedChange={checked =>
              onSettingsChange('email_notifications', Boolean(checked))
            }
            disabled={!isEditing}
          />
        </div>
        <div className="flex items-center justify-between">
          <span className="text-muted-foreground">{t('Push сповіщення')}</span>
          <Checkbox
            checked={formData.push_notifications}
            onCheckedChange={checked =>
              onSettingsChange('push_notifications', Boolean(checked))
            }
            disabled={!isEditing}
          />
        </div>
        <div className="flex items-center justify-between">
          <span className="text-muted-foreground">
            {t('Нагадування про дедлайни')}
          </span>
          <Checkbox
            checked={formData.deadline_reminders}
            onCheckedChange={checked =>
              onSettingsChange('deadline_reminders', Boolean(checked))
            }
            disabled={!isEditing}
          />
        </div>
      </div>
    </div>
  )
}

function PrivacyBlock({ formData, onSettingsChange, isEditing }: any) {
  const { t } = useI18n()
  return (
    <div className="bg-card rounded-lg shadow p-6 mb-6 border border-border">
      <h3 className="font-medium text-foreground mb-4">{t('Приватність')}</h3>
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-muted-foreground">
            {t('Показувати профіль іншим')}
          </span>
          <Checkbox
            checked={formData.show_profile_to_others}
            onCheckedChange={checked =>
              onSettingsChange('show_profile_to_others', Boolean(checked))
            }
            disabled={!isEditing}
          />
        </div>
        <div className="flex items-center justify-between">
          <span className="text-muted-foreground">
            {t('Показувати досягнення')}
          </span>
          <Checkbox
            checked={formData.show_achievements}
            onCheckedChange={checked =>
              onSettingsChange('show_achievements', Boolean(checked))
            }
            disabled={!isEditing}
          />
        </div>
      </div>
    </div>
  )
}

function ChangePasswordBlock({
  currentPassword,
  setCurrentPassword,
  newPassword,
  setNewPassword,
  confirmPassword,
  setConfirmPassword,
  passwordError,
  passwordSuccess,
  isPasswordLoading,
  handleChangePassword,
}: any) {
  const { t } = useI18n()
  return (
    <div className="bg-card rounded-lg shadow p-6 mb-6 border border-border">
      <h3 className="font-medium text-foreground mb-4">{t('Зміна паролю')}</h3>
      <form className="space-y-4" onSubmit={handleChangePassword}>
        {passwordError && <FormAlert type="error" message={passwordError} />}
        {passwordSuccess && (
          <FormAlert type="success" message={passwordSuccess} />
        )}
        <PasswordField
          value={currentPassword}
          onChange={setCurrentPassword}
          required
          label={t('Поточний пароль')}
          placeholder={t('Введіть поточний пароль')}
        />
        <PasswordField
          value={newPassword}
          onChange={setNewPassword}
          required
          label={t('Новий пароль')}
          placeholder={t('Введіть новий пароль')}
        />
        <PasswordField
          value={confirmPassword}
          onChange={setConfirmPassword}
          required
          label={t('Підтвердіть пароль')}
          placeholder={t('Підтвердіть новий пароль')}
        />
        <Button
          className="bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 w-full text-white"
          type="submit"
          disabled={isPasswordLoading}
        >
          {isPasswordLoading ? t('Зміна пароля...') : t('Змінити пароль')}
        </Button>
      </form>
    </div>
  )
}

function SwitchLanguageBlock() {
  const { t } = useI18n()
  return (
    <div className="bg-card rounded-lg shadow p-6 mb-6 border border-border">
      <h3 className="font-medium text-foreground mb-4">
        {t('Мова інтерфейсу')}
      </h3>
      <div className="space-y-3">
        <LanguageSwitcher className="w-full" />
      </div>
    </div>
  )
}

function DangerZoneBlock({ onDeleteAccount }: any) {
  const { t } = useI18n()
  return (
    <div className="bg-card rounded-lg shadow p-6 border border-destructive">
      <h3 className="font-medium text-destructive mb-4">
        {t('Небезпечна зона')}
      </h3>
      <div className="p-4 border border-destructive rounded-lg bg-destructive/10 dark:bg-destructive/20">
        <h4 className="font-medium text-destructive mb-2">
          {t('Видалення акаунта')}
        </h4>
        <p className="text-sm text-destructive mb-4">
          {t(
            'Після видалення акаунта всі ваші дані будуть назавжди втрачені. Ця дія не може бути скасована.'
          )}
        </p>
        <DeleteAccountButton onDelete={onDeleteAccount} />
      </div>
    </div>
  )
}

export const ProfileTabs = ({
  formData,
  isEditing,
  onFormChange,
  onSettingsChange,
  onDeleteAccount,
}: ProfileTabsProps) => {
  const { t } = useI18n()
  const { refresh, loading, rawStats } = useUserCoursesStatus()
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [passwordError, setPasswordError] = useState<string | null>(null)
  const [passwordSuccess, setPasswordSuccess] = useState<string | null>(null)
  const [isPasswordLoading, setIsPasswordLoading] = useState(false)
  const achievementsToRender = useAchievements(rawStats)

  const coursesToRender = useMemo(() => {
    if (!rawStats) return []

    const enrolled = rawStats.enrolled_list || []
    const completed = rawStats.completed_list || []

    return [...enrolled, ...completed].map(item => ({
      id: item.course.id,
      title: item.course.title,
      progress: Math.round(item.course.user_status?.progress || 0),
      isCompleted: item.course.user_status?.is_completed || false,
      enrolledAt: item.course.user_status?.enrolled_at,
      completedAt: item.course.user_status?.completed_at,
      totalLessons: item.course.details?.total_lessons || 0,
      completedLessons: item.course.user_status?.completed_lessons_count || 0,
    }))
  }, [rawStats])

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault()
    setPasswordError(null)
    setPasswordSuccess(null)
    if (!currentPassword || !newPassword || !confirmPassword) {
      setPasswordError(t('Всі поля обовʼязкові'))
      return
    }
    if (newPassword.length < 8) {
      setPasswordError(t('Пароль повинен містити щонайменше 8 символів'))
      return
    }
    if (newPassword !== confirmPassword) {
      setPasswordError(t('Паролі не співпадають'))
      return
    }
    setIsPasswordLoading(true)
    try {
      const res = await profileService.changePassword({
        current_password: currentPassword,
        new_password: newPassword,
        confirm_password: confirmPassword,
      })
      setPasswordSuccess(t('Пароль змінено успішно') || `${res.message}`)
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
    } catch (err: any) {
      setPasswordError(t('Не вдалося змінити пароль') || err.message)
    } finally {
      setIsPasswordLoading(false)
    }
  }

  return (
    <Tabs defaultValue="info" className="space-y-6">
      <TabsList className="grid w-full grid-cols-4">
        <TabsTrigger value="info">{t('Інформація')}</TabsTrigger>
        <TabsTrigger value="progress">{t('Прогрес')}</TabsTrigger>
        <TabsTrigger value="achievements">{t('Досягнення')}</TabsTrigger>
        <TabsTrigger value="settings">{t('Налаштування')}</TabsTrigger>
      </TabsList>

      {/* Personal Information */}
      <TabsContent value="info">
        <Card>
          <CardHeader>
            <CardTitle>{t('Особиста інформація')}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <EditProfileForm
              formData={formData}
              isEditing={isEditing}
              onFormChange={onFormChange}
            />
          </CardContent>
        </Card>
      </TabsContent>

      {/* Course Progress */}
      <TabsContent value="progress">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>{t('Прогрес по курсах')}</CardTitle>
            <Button
              variant="ghost"
              size="sm"
              onClick={refresh}
              disabled={loading}
            >
              <RotateCw
                className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`}
              />
            </Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {coursesToRender.length > 0 ? (
                coursesToRender.map(course => (
                  <div key={course.id} className="space-y-2">
                    <div className="flex justify-between items-center">
                      <h3 className="font-medium text-foreground">
                        {course.title}
                      </h3>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-muted-foreground">
                          {course.progress}%
                        </span>
                        <Badge
                          variant={course.isCompleted ? 'default' : 'secondary'}
                        >
                          {course.isCompleted ? t('Завершено') : t('В процесі')}
                        </Badge>
                      </div>
                    </div>
                    <Progress value={course.progress} className="h-2" />
                    <div className="flex justify-between text-sm text-muted-foreground">
                      <span>
                        {t('Записано')}:{' '}
                        {new Date(course.enrolledAt).toLocaleDateString()}
                      </span>
                      {course.isCompleted && (
                        <span className="flex items-center text-green-600 dark:text-green-400 font-medium">
                          <CheckCircle className="w-4 h-4 mr-1" />
                          {t('Курс пройдено')}
                        </span>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-10 text-muted-foreground">
                  {t('Ви ще не розпочали жодного курсу')}
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </TabsContent>

      {/* Achievements */}
      <TabsContent value="achievements">
        <Card>
          <CardHeader>
            <CardTitle>{t('Досягнення')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-4">
              {achievementsToRender.length > 0 ? (
                achievementsToRender.map(achievement => (
                  <div
                    key={achievement.id}
                    className="flex items-start space-x-4 p-4 border border-border rounded-lg hover:border-brand-300 dark:hover:border-brand-700 transition-colors bg-card/50"
                  >
                    <div className="text-3xl">{achievement.icon}</div>
                    <div className="flex-1">
                      <h3 className="font-bold text-foreground">
                        {achievement.title}
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {achievement.description}
                      </p>
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-xs text-muted-foreground">
                          {achievement.date}
                        </span>
                        <Badge
                          className={getAchievementColor(achievement.type)}
                        >
                          {achievement.type === 'gold'
                            ? t('Золото')
                            : achievement.type === 'silver'
                              ? t('Срібло')
                              : t('Бронза')}
                        </Badge>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="col-span-2 py-10 text-center border-2 border-dashed rounded-xl">
                  <p className="text-muted-foreground">
                    {t(
                      'У вас поки немає досягнень. Розпочніть навчання, щоб отримати першу нагороду!'
                    )}
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </TabsContent>

      {/* Settings */}
      <TabsContent value="settings">
        <Card>
          <CardHeader>
            <CardTitle>{t('Налаштування')}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <NotificationsBlock
              formData={formData}
              onSettingsChange={onSettingsChange}
              isEditing={isEditing}
            />
            <PrivacyBlock
              formData={formData}
              onSettingsChange={onSettingsChange}
              isEditing={isEditing}
            />
            <SwitchLanguageBlock />
            <ChangePasswordBlock
              currentPassword={currentPassword}
              setCurrentPassword={setCurrentPassword}
              newPassword={newPassword}
              setNewPassword={setNewPassword}
              confirmPassword={confirmPassword}
              setConfirmPassword={setConfirmPassword}
              passwordError={passwordError}
              passwordSuccess={passwordSuccess}
              isPasswordLoading={isPasswordLoading}
              handleChangePassword={handleChangePassword}
            />
            <DangerZoneBlock onDeleteAccount={onDeleteAccount} />
          </CardContent>
        </Card>
      </TabsContent>
    </Tabs>
  )
}
