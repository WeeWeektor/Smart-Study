import {
  Input,
  Label,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Textarea,
} from '@/shared/ui'
import * as React from 'react'
import { UserFields } from '@/shared/ui/user-fields'
import { ProfileExtraFields } from '@/shared/ui/profile-extra-fields'

interface EditProfileFormProps {
  formData: {
    name: string
    surname: string
    phone: string
    location: string
    organization: string
    specialization: string
    bio: string
    education_level: string
  }
  isEditing: boolean
  onFormChange: (field: string, value: string) => void
}

export const EditProfileForm = ({
  formData,
  isEditing,
  onFormChange,
}: EditProfileFormProps) => {
  return (
    <>
      <UserFields
        formData={{
          name: formData.name,
          surname: formData.surname,
          phone: formData.phone,
        }}
        onChange={onFormChange}
        isEditing={isEditing}
        showEmail={false}
        showRole={false}
        requiredFields={['name', 'surname']}
      />
      <ProfileExtraFields
        formData={formData}
        onChange={onFormChange}
        isEditing={isEditing}
      />
    </>
  )
}
