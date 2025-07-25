import {
  Input,
  Label,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './index'
import React from 'react'

interface UserFieldsProps {
  formData: {
    name: string
    surname: string
    phone?: string
    email?: string
    role?: string
  }
  onChange: (field: string, value: string) => void
  isEditing?: boolean
  showEmail?: boolean
  showRole?: boolean
  requiredFields?: string[]
}

export const UserFields: React.FC<UserFieldsProps> = ({
  formData,
  onChange,
  isEditing = true,
  showEmail = false,
  showRole = false,
  requiredFields = ['name', 'surname'],
}) => (
  <>
    <div className="grid grid-cols-2 gap-4">
      <div className="space-y-2">
        <Label htmlFor="name">Ім'я</Label>
        <Input
          id="name"
          type="text"
          placeholder="Ваше ім'я"
          value={formData.name}
          onChange={e => onChange('name', e.target.value)}
          required={requiredFields.includes('name')}
          disabled={!isEditing}
          className="border-slate-300 focus:border-brand-500 focus:ring-brand-500"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="surname">Прізвище</Label>
        <Input
          id="surname"
          type="text"
          placeholder="Ваше прізвище"
          value={formData.surname}
          onChange={e => onChange('surname', e.target.value)}
          required={requiredFields.includes('surname')}
          disabled={!isEditing}
          className="border-slate-300 focus:border-brand-500 focus:ring-brand-500"
        />
      </div>
    </div>
    {showEmail && (
      <div className="space-y-2">
        <Label htmlFor="email">Email адреса</Label>
        <Input
          id="email"
          type="email"
          placeholder="your.email@example.com"
          value={formData.email || ''}
          onChange={e => onChange('email', e.target.value)}
          required={requiredFields.includes('email')}
          disabled={!isEditing}
          className="border-slate-300 focus:border-brand-500 focus:ring-brand-500"
        />
      </div>
    )}
    <div className="space-y-2">
      <Label htmlFor="phone">Номер телефону</Label>
      <Input
        id="phone"
        type="tel"
        placeholder="+380 XX XXX XX XX"
        value={formData.phone || ''}
        onChange={e => onChange('phone', e.target.value)}
        disabled={!isEditing}
        className="border-slate-300 focus:border-brand-500 focus:ring-brand-500"
      />
    </div>
    {showRole && (
      <div className="space-y-2">
        <Label htmlFor="role">Роль</Label>
        <Select
          value={formData.role || ''}
          onValueChange={value => onChange('role', value)}
          disabled={!isEditing}
          required={requiredFields.includes('role')}
        >
          <SelectTrigger className="border-slate-300 focus:border-brand-500 focus:ring-brand-500">
            <SelectValue placeholder="Оберіть свою роль" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="student">Студент</SelectItem>
            <SelectItem value="teacher">Викладач</SelectItem>
          </SelectContent>
        </Select>
      </div>
    )}
  </>
)
