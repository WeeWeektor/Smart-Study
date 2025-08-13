import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
  Badge,
  Progress,
  Checkbox,
  Button,
  LanguageSwitcher,
} from '@/shared/ui'
import { EditProfileForm } from '@/features/edit-profile'
import { DeleteAccountButton } from '@/features/delete-account'
import { CheckCircle } from 'lucide-react'
import { courseProgress, achievements } from '@/shared/lib/mock-data'
import { getAchievementColor } from '@/shared/lib/utils'
import { useState } from 'react'
import { PasswordField } from '@/shared/ui/password-field'
import { FormAlert } from '@/shared/ui/form-alert'
import { profileService } from '@/entities/profile/profile.service'
import React from 'react'
import { useI18n } from '@/shared/lib'

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
      <h3 className="font-medium text-foreground mb-4">
        {t('settings.notifications')}
      </h3>
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-muted-foreground">
            {t('settings.emailNotifications')}
          </span>
          <Checkbox
            checked={formData.email_notifications}
            onCheckedChange={checked =>
              onSettingsChange('email_notifications', Boolean(checked))
            }
            disabled={!isEditing}
          />
        </div>
        <div className="flex items-center justify-between">
          <span className="text-muted-foreground">
            {t('settings.pushNotifications')}
          </span>
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
            {t('settings.deadlineReminders')}
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
      <h3 className="font-medium text-foreground mb-4">
        {t('settings.privacy')}
      </h3>
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-muted-foreground">
            {t('settings.showProfileToOthers')}
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
            {t('settings.showAchievements')}
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
      <h3 className="font-medium text-foreground mb-4">
        {t('auth.changePassword.title')}
      </h3>
      <form className="space-y-4" onSubmit={handleChangePassword}>
        {passwordError && <FormAlert type="error" message={passwordError} />}
        {passwordSuccess && (
          <FormAlert type="success" message={passwordSuccess} />
        )}
        <PasswordField
          value={currentPassword}
          onChange={setCurrentPassword}
          required
          label={t('auth.currentPassword')}
          placeholder={t('auth.enterCurrentPassword')}
        />
        <PasswordField
          value={newPassword}
          onChange={setNewPassword}
          required
          label={t('auth.newPassword')}
          placeholder={t('auth.enterNewPassword')}
        />
        <PasswordField
          value={confirmPassword}
          onChange={setConfirmPassword}
          required
          label={t('auth.confirmPassword')}
          placeholder={t('auth.confirmNewPassword')}
        />
        <Button
          className="bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400 w-full text-white"
          type="submit"
          disabled={isPasswordLoading}
        >
          {isPasswordLoading
            ? t('auth.changePassword.processing')
            : t('auth.changePassword.action')}
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
        {t('settings.language')}
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
        {t('settings.dangerZone')}
      </h3>
      <div className="p-4 border border-destructive rounded-lg bg-destructive/10 dark:bg-destructive/20">
        <h4 className="font-medium text-destructive mb-2">
          {t('settings.deleteAccount')}
        </h4>
        <p className="text-sm text-destructive mb-4">
          {t('settings.deleteAccountWarning')}
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
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [passwordError, setPasswordError] = useState<string | null>(null)
  const [passwordSuccess, setPasswordSuccess] = useState<string | null>(null)
  const [isPasswordLoading, setIsPasswordLoading] = useState(false)

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault()
    setPasswordError(null)
    setPasswordSuccess(null)
    if (!currentPassword || !newPassword || !confirmPassword) {
      setPasswordError(`${t('validation.allFieldsRequired')}`)
      return
    }
    if (newPassword.length < 8) {
      setPasswordError(`${(t('validation.passwordMinLength'), { min: 8 })}`)
      return
    }
    if (newPassword !== confirmPassword) {
      setPasswordError(`${t('validation.passwordMismatch')}`)
      return
    }
    setIsPasswordLoading(true)
    try {
      const res = await profileService.changePassword({
        current_password: currentPassword,
        new_password: newPassword,
        confirm_password: confirmPassword,
      })
      setPasswordSuccess(res.message || `${t('auth.passwordChanged')}`)
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
    } catch (err: any) {
      setPasswordError(err.message || `${t('auth.passwordChangeError')}`)
    } finally {
      setIsPasswordLoading(false)
    }
  }

  return (
    <Tabs defaultValue="info" className="space-y-6">
      <TabsList className="grid w-full grid-cols-4">
        <TabsTrigger value="info">{t('common.info')}</TabsTrigger>
        <TabsTrigger value="progress">{t('common.progress')}</TabsTrigger>
        <TabsTrigger value="achievements">
          {t('common.achievements')}
        </TabsTrigger>
        <TabsTrigger value="settings">{t('common.settings')}</TabsTrigger>
      </TabsList>

      {/* Personal Information */}
      <TabsContent value="info">
        <Card>
          <CardHeader>
            <CardTitle>{t('profile.personalInfo')}</CardTitle>
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
          <CardHeader>
            <CardTitle>{t('profile.progressInCourses')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {courseProgress.map((course, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <h3 className="font-medium text-foreground">
                      {course.course}
                    </h3>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-muted-foreground">
                        {course.completed}/{course.total} {t('profile.lessons')}
                      </span>
                      <Badge
                        variant={
                          course.progress === 100 ? 'default' : 'secondary'
                        }
                      >
                        {course.progress}%
                      </Badge>
                    </div>
                  </div>
                  <Progress value={course.progress} />
                  <div className="flex justify-between text-sm text-muted-foreground">
                    <span>
                      {t('profile.lastActivity')}: {course.lastActivity}
                    </span>
                    {course.progress === 100 && (
                      <span className="flex items-center text-success-text">
                        <CheckCircle className="w-4 h-4 mr-1 text-success-icon" />
                        {t('common.ending')}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </TabsContent>

      {/* Achievements */}
      <TabsContent value="achievements">
        <Card>
          <CardHeader>
            <CardTitle>{t('profile.achievements')}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-4">
              {achievements.map(achievement => (
                <div
                  key={achievement.id}
                  className="flex items-start space-x-4 p-4 border border-border rounded-lg hover:border-brand-300 dark:hover:border-brand-700 transition-colors"
                >
                  <div className="text-3xl">{achievement.icon}</div>
                  <div className="flex-1">
                    <h3 className="font-medium text-foreground">
                      {achievement.title}
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      {achievement.description}
                    </p>
                    <div className="flex items-center justify-between mt-2">
                      <span className="text-xs text-muted-foreground">
                        {achievement.date}
                      </span>
                      <Badge className={getAchievementColor(achievement.type)}>
                        {achievement.type === 'gold'
                          ? `${t('profile.gold')}`
                          : achievement.type === 'silver'
                            ? `${t('profile.silver')}`
                            : `${t('profile.bronze')}`}
                      </Badge>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </TabsContent>

      {/* Settings */}
      <TabsContent value="settings">
        <Card>
          <CardHeader>
            <CardTitle>{t('profile.settings')}</CardTitle>
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
