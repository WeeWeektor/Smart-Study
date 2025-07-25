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
import { X } from 'lucide-react'

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
}) => (
  <>
    <div className="relative">
      <Label htmlFor="education_level">Рівень освіти</Label>
      <Select
        value={formData.education_level || 'not_specified'}
        onValueChange={(value: string) => onChange('education_level', value)}
        disabled={!isEditing}
      >
        <SelectTrigger>
          <SelectValue placeholder="Не вказано" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="not_specified" className="text-slate-400">
            Не вказано
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
      <Label htmlFor="location">Місцезнаходження</Label>
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
      <Label htmlFor="organization">Організація</Label>
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
      <Label htmlFor="specialization">Спеціалізація</Label>
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
      <Label htmlFor="bio">Про себе</Label>
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
