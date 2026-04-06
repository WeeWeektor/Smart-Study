import React from 'react'
import {
  Avatar,
  AvatarFallback,
  AvatarImage,
  Card,
  CardContent,
  CardHeader,
} from '@/shared/ui'
import {
  Briefcase,
  Building2,
  GraduationCap,
  Mail,
  MapPin,
  Phone,
  User,
} from 'lucide-react'
import { useI18n } from '@/shared/lib'
import { type CourseOwnerProfileResponse } from '@/features/course'

interface AuthorSectionProps {
  ownerData: CourseOwnerProfileResponse | null
}

export const AuthorSection: React.FC<AuthorSectionProps> = ({ ownerData }) => {
  const { t } = useI18n()

  if (!ownerData || !ownerData.userData) return null

  const { owner, profile, settings } = ownerData.userData
  const isPublic = settings.show_profile_to_others
  const fullName = `${owner.name} ${owner.surname}`
  const initials =
    `${owner.name?.charAt(0) || ''}${owner.surname?.charAt(0) || ''}`.toUpperCase()

  return (
    <Card className="mb-8 overflow-hidden border-l-4 border-l-brand-600 dark:border-l-brand-500 shadow-sm">
      <CardHeader className="pb-4">
        <div className="flex items-center gap-4">
          <Avatar className="h-16 w-16 border-2 border-white shadow-sm ring-1 ring-slate-100 dark:ring-slate-700">
            <AvatarImage
              src={profile.profile_picture || undefined}
              alt={fullName}
              className="object-cover"
            />
            <AvatarFallback className="bg-brand-100 text-brand-700 font-bold text-xl">
              {initials}
            </AvatarFallback>
          </Avatar>

          <div className="flex flex-col">
            <h3 className="text-xl font-bold text-slate-800 dark:text-slate-100">
              {fullName}
            </h3>
            <span className="text-sm text-slate-500 dark:text-slate-400 font-medium flex items-center gap-1.5">
              <User className="w-3.5 h-3.5" />
              {t('Автор курсу')}
            </span>
          </div>
        </div>
      </CardHeader>

      {isPublic && (
        <CardContent className="space-y-4 border-t border-slate-100 dark:border-slate-800 mt-4 pt-4">
          {profile.bio && (
            <div className="text-sm text-slate-600 dark:text-slate-300 bg-slate-50 dark:bg-slate-800/50 p-3 rounded-md italic line-clamp-2 break-words overflow-hidden">
              "{profile.bio}"
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-3 text-sm">
            {profile.specialization && (
              <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300">
                <Briefcase className="w-4 h-4 text-brand-500 shrink-0" />
                <span className="font-semibold text-slate-500 dark:text-slate-400">
                  {t('Спеціалізація')}:
                </span>
                <span>
                  {profile.specialization.length > 50
                    ? profile.specialization.slice(0, 50) + '...'
                    : profile.specialization}
                </span>
              </div>
            )}

            {profile.organization && (
              <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300">
                <Building2 className="w-4 h-4 text-blue-500 shrink-0" />
                <span className="font-semibold text-slate-500 dark:text-slate-400">
                  {t('Організація')}:
                </span>
                <span>
                  {profile.organization.length > 50
                    ? profile.organization.slice(0, 50) + '...'
                    : profile.organization}
                </span>
              </div>
            )}

            {profile.education_level && (
              <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300">
                <GraduationCap className="w-4 h-4 text-purple-500 shrink-0" />
                <span className="font-semibold text-slate-500 dark:text-slate-400">
                  {t('Освіта')}:
                </span>
                <span className="capitalize">
                  {profile.education_level.length > 50
                    ? profile.education_level.slice(0, 50) + '...'
                    : profile.education_level}
                </span>
              </div>
            )}

            {profile.location && (
              <div className="flex items-center gap-2 text-slate-700 dark:text-slate-300">
                <MapPin className="w-4 h-4 text-red-500 shrink-0" />
                <span className="font-semibold text-slate-500 dark:text-slate-400">
                  {t('Локація')}:
                </span>
                <span>
                  {profile.location.length > 50
                    ? profile.location.slice(0, 50) + '...'
                    : profile.location}
                </span>
              </div>
            )}
          </div>

          {(owner.email || owner.phone_number) && (
            <div className="border-t border-slate-100 dark:border-slate-800 pt-3 mt-2 flex flex-wrap gap-6">
              {owner.email && (
                <div className="flex items-center gap-2 text-xs text-slate-500 hover:text-brand-600 transition-colors cursor-pointer">
                  <Mail className="w-3.5 h-3.5" />
                  {owner.email}
                </div>
              )}
              {owner.phone_number && (
                <div className="flex items-center gap-2 text-xs text-slate-500 hover:text-brand-600 transition-colors cursor-pointer">
                  <Phone className="w-3.5 h-3.5" />
                  {owner.phone_number}
                </div>
              )}
            </div>
          )}
        </CardContent>
      )}
    </Card>
  )
}
