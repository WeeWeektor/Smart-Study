import {
  Input,
  Label,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Textarea,
} from './index'
import React from 'react'
import { useI18n } from '@/shared/lib'

interface ProfileExtraFieldsProps {
  formData: {
    education_level: string | null
    location: string
    organization: string
    specialization: string
    bio: string
  }
  onChange: (field: string, value: string | null) => void
  isEditing?: boolean
}

export const ProfileExtraFields: React.FC<ProfileExtraFieldsProps> = ({
  formData,
  onChange,
  isEditing = true,
}) => {
  const { t } = useI18n()
  return (
    <>
      <div className="relative">
        <Label htmlFor="education_level">{t('Рівень освіти')}</Label>
        <Select
          value={formData.education_level || 'not_specified'}
          onValueChange={(value: string) => onChange('education_level', value)}
          disabled={!isEditing}
        >
          <SelectTrigger>
            <SelectValue placeholder={t('Не вказано')} />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="not_specified" className="text-muted-foreground">
              {t('Не вказано')}
            </SelectItem>
            <SelectItem value="bachelor">{t('Бакалавр')}</SelectItem>
            <SelectItem value="master">{t('Магістр')}</SelectItem>
            <SelectItem value="doctor of science">
              {t('Доктор наук')}
            </SelectItem>
            <SelectItem value="diploma">{t('Диплом')}</SelectItem>
            <SelectItem value="certificate">{t('Сертифікат')}</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div>
        <Label htmlFor="location">{t('Місцезнаходження')}</Label>
        <Input
          id="location"
          value={formData.location}
          disabled={!isEditing}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
            onChange('location', e.target.value)
          }
        />
      </div>
      <div>
        <Label htmlFor="organization">{t('Організація')}</Label>
        <Input
          id="organization"
          value={formData.organization}
          disabled={!isEditing}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
            onChange('organization', e.target.value)
          }
        />
      </div>
      <div>
        <Label htmlFor="specialization">{t('Спеціалізація')}</Label>
        <Input
          id="specialization"
          value={formData.specialization}
          disabled={!isEditing}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
            onChange('specialization', e.target.value)
          }
        />
      </div>
      <div>
        <Label htmlFor="bio">{t('Про себе')}</Label>
        <Textarea
          id="bio"
          value={formData.bio}
          disabled={!isEditing}
          onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
            onChange('bio', e.target.value)
          }
          rows={4}
        />
      </div>
    </>
  )
}
