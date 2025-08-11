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
        <Label htmlFor="education_level">{t('profile.educationLevel')}</Label>
        <Select
          value={formData.education_level || 'not_specified'}
          onValueChange={(value: string) => onChange('education_level', value)}
          disabled={!isEditing}
        >
          <SelectTrigger>
            <SelectValue placeholder={t('common.notSpecified')} />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="not_specified" className="text-muted-foreground">
              {t('common.notSpecified')}
            </SelectItem>
            <SelectItem value="bachelor">Bachelor</SelectItem>
            <SelectItem value="master">Master</SelectItem>
            <SelectItem value="doctor of science">Doctor of Science</SelectItem>
            <SelectItem value="diploma">Diploma</SelectItem>
            <SelectItem value="certificate">Certificate</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div>
        <Label htmlFor="location">{t('profile.location')}</Label>
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
        <Label htmlFor="organization">{t('profile.organization')}</Label>
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
        <Label htmlFor="specialization">{t('profile.specialization')}</Label>
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
        <Label htmlFor="bio">{t('profile.bio')}</Label>
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
