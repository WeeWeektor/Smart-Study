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

interface ProfileTabsProps {
  formData: any
  isEditing: boolean
  onFormChange: (field: string, value: string) => void
  onSettingsChange: (field: string, value: boolean) => void
  onDeleteAccount: () => void
}

function NotificationsBlock({ formData, onSettingsChange, isEditing }: any) {
  return (
    <div className="bg-white rounded-lg shadow p-6 mb-6 border border-slate-200">
      <h3 className="font-medium text-slate-900 mb-4">Сповіщення</h3>
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-slate-700">Email сповіщення</span>
          <Checkbox
            checked={formData.email_notifications}
            onCheckedChange={checked =>
              onSettingsChange('email_notifications', Boolean(checked))
            }
            disabled={!isEditing}
          />
        </div>
        <div className="flex items-center justify-between">
          <span className="text-slate-700">Push сповіщення</span>
          <Checkbox
            checked={formData.push_notifications}
            onCheckedChange={checked =>
              onSettingsChange('push_notifications', Boolean(checked))
            }
            disabled={!isEditing}
          />
        </div>
        <div className="flex items-center justify-between">
          <span className="text-slate-700">Нагадування про дедлайни</span>
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
  return (
    <div className="bg-white rounded-lg shadow p-6 mb-6 border border-slate-200">
      <h3 className="font-medium text-slate-900 mb-4">Приватність</h3>
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-slate-700">Показувати профіль іншим</span>
          <Checkbox
            checked={formData.show_profile_to_others}
            onCheckedChange={checked =>
              onSettingsChange('show_profile_to_others', Boolean(checked))
            }
            disabled={!isEditing}
          />
        </div>
        <div className="flex items-center justify-between">
          <span className="text-slate-700">Показувати досягнення</span>
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
  return (
    <div className="bg-white rounded-lg shadow p-6 mb-6 border border-slate-200">
      <h3 className="font-medium text-slate-900 mb-4">Зміна паролю</h3>
      <form className="space-y-4" onSubmit={handleChangePassword}>
        {passwordError && <FormAlert type="error" message={passwordError} />}
        {passwordSuccess && (
          <FormAlert type="success" message={passwordSuccess} />
        )}
        <PasswordField
          value={currentPassword}
          onChange={setCurrentPassword}
          required
          label="Поточний пароль"
          placeholder="Введіть поточний пароль"
        />
        <PasswordField
          value={newPassword}
          onChange={setNewPassword}
          required
          label="Новий пароль"
          placeholder="Введіть новий пароль"
        />
        <PasswordField
          value={confirmPassword}
          onChange={setConfirmPassword}
          required
          label="Підтвердіть пароль"
          placeholder="Підтвердіть новий пароль"
        />
        <Button
          className="bg-brand-600 hover:bg-brand-700 w-full"
          type="submit"
          disabled={isPasswordLoading}
        >
          {isPasswordLoading ? 'Зміна пароля...' : 'Змінити пароль'}
        </Button>
      </form>
    </div>
  )
}

function DangerZoneBlock({ onDeleteAccount }: any) {
  return (
    <div className="bg-white rounded-lg shadow p-6 border border-red-200">
      <h3 className="font-medium text-slate-900 mb-4">Небезпечна зона</h3>
      <div className="p-4 border border-red-200 rounded-lg bg-red-50">
        <h4 className="font-medium text-red-900 mb-2">Видалення акаунта</h4>
        <p className="text-sm text-red-700 mb-4">
          Після видалення акаунта всі ваші дані будуть назавжди втрачені. Ця дія
          не може бути скасована.
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
  // --- Додаємо стейт для зміни паролю ---
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
      setPasswordError('Всі поля обовʼязкові')
      return
    }
    if (newPassword.length < 8) {
      setPasswordError('Пароль повинен містити щонайменше 8 символів')
      return
    }
    if (newPassword !== confirmPassword) {
      setPasswordError('Паролі не співпадають')
      return
    }
    setIsPasswordLoading(true)
    try {
      const res = await profileService.changePassword({
        current_password: currentPassword,
        new_password: newPassword,
        confirm_password: confirmPassword,
      })
      setPasswordSuccess(res.message || 'Пароль змінено успішно')
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
    } catch (err: any) {
      setPasswordError(err.message || 'Не вдалося змінити пароль')
    } finally {
      setIsPasswordLoading(false)
    }
  }

  return (
    <Tabs defaultValue="info" className="space-y-6">
      <TabsList className="grid w-full grid-cols-4">
        <TabsTrigger value="info">Інформація</TabsTrigger>
        <TabsTrigger value="progress">Прогрес</TabsTrigger>
        <TabsTrigger value="achievements">Досягнення</TabsTrigger>
        <TabsTrigger value="settings">Налаштування</TabsTrigger>
      </TabsList>

      {/* Personal Information */}
      <TabsContent value="info">
        <Card>
          <CardHeader>
            <CardTitle>Особиста інформація</CardTitle>
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
            <CardTitle>Прогрес по курсах</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {courseProgress.map((course, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <h3 className="font-medium text-slate-900">
                      {course.course}
                    </h3>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-slate-600">
                        {course.completed}/{course.total} уроків
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
                  <div className="flex justify-between text-sm text-slate-500">
                    <span>Остання активність: {course.lastActivity}</span>
                    {course.progress === 100 && (
                      <span className="flex items-center text-green-600">
                        <CheckCircle className="w-4 h-4 mr-1" />
                        Завершено
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
            <CardTitle>Досягнення</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-4">
              {achievements.map(achievement => (
                <div
                  key={achievement.id}
                  className="flex items-start space-x-4 p-4 border border-slate-200 rounded-lg hover:border-brand-300 transition-colors"
                >
                  <div className="text-3xl">{achievement.icon}</div>
                  <div className="flex-1">
                    <h3 className="font-medium text-slate-900">
                      {achievement.title}
                    </h3>
                    <p className="text-sm text-slate-600">
                      {achievement.description}
                    </p>
                    <div className="flex items-center justify-between mt-2">
                      <span className="text-xs text-slate-500">
                        {achievement.date}
                      </span>
                      <Badge className={getAchievementColor(achievement.type)}>
                        {achievement.type === 'gold'
                          ? 'Золото'
                          : achievement.type === 'silver'
                            ? 'Срібло'
                            : 'Бронза'}
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
            <CardTitle>Налаштування</CardTitle>
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
