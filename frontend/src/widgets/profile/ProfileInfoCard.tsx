import {
  Card,
  CardContent,
  Badge,
  Avatar,
  AvatarFallback,
  AvatarImage,
  Button,
} from '@/shared/ui'
import {
  Mail,
  Phone,
  MapPin,
  GraduationCap,
  Camera,
  Book,
  User as UserIcon,
  Award,
} from 'lucide-react'
import * as React from 'react'
import { useState } from 'react'
import { useI18n } from '@/shared/lib'

interface ProfileInfoCardProps {
  profileData: {
    user: {
      name: string
      surname: string
      email: string
      phone_number?: string
      role: string
    }
    profile: {
      profile_picture?: string
      location?: string
      organization?: string
      specialization?: string
      bio?: string
      education_level?: string
    }
  }
  previewUrl: string
  onFileSelect: (e: React.ChangeEvent<HTMLInputElement>) => void
  isEditing: boolean
}

const getInitials = (name: string, surname: string) => {
  const firstLetter = name.charAt(0).toUpperCase()
  const lastLetter = surname.charAt(0).toUpperCase()
  return firstLetter + lastLetter
}

const RoleText: React.FC<{ role: string }> = ({ role }) => {
  const { t } = useI18n()
  if (role === 'student') return <>{t('auth.student')}</>
  if (role === 'teacher') return <>{t('auth.teacher')}</>
  if (role === 'admin') return <>Admin</>
  return null
}

function truncateWithEllipsis(str: string, max: number) {
  return str.length > max ? str.slice(0, max) + '...' : str
}

export const ProfileInfoCard = ({
  profileData,
  previewUrl,
  onFileSelect,
  isEditing,
}: ProfileInfoCardProps) => {
  const [showMore, setShowMore] = useState(false)
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="text-center">
          <div className="relative inline-block">
            <Avatar className="w-24 h-24 mx-auto">
              <AvatarImage
                src={previewUrl || profileData?.profile?.profile_picture}
                alt="Profile picture"
              />
              <AvatarFallback className="text-xl bg-brand-100 dark:bg-brand-900 text-brand-600 dark:text-brand-400">
                {getInitials(profileData.user.name, profileData.user.surname)}
              </AvatarFallback>
            </Avatar>
          </div>

          {isEditing && (
            <div className="mt-4">
              <input
                type="file"
                id="profile-photo"
                accept="image/jpeg,image/png,image/webp"
                className="hidden"
                onChange={onFileSelect}
              />
              <Button
                variant="outline"
                size="sm"
                className="text-brand-600 dark:text-brand-400 border-brand-300 dark:border-brand-700 hover:bg-brand-50 dark:hover:bg-brand-900"
                onClick={() =>
                  document.getElementById('profile-photo')?.click()
                }
              >
                <Camera className="w-4 h-4 mr-2" />
                Change photo
              </Button>
            </div>
          )}

          <h2
            className="text-xl font-semibold text-foreground mt-4 truncate max-w-xs mx-auto overflow-hidden whitespace-nowrap"
            title={`${profileData.user.name} ${profileData.user.surname}`}
          >
            {profileData.user.name} {profileData.user.surname}
          </h2>
          <Badge className="mt-2 bg-brand-100 dark:bg-brand-900 text-brand-700 dark:text-brand-300">
            <RoleText role={profileData?.user?.role} />
          </Badge>
        </div>

        <div className="space-y-4 mt-6">
          {profileData?.user?.email && (
            <div className="flex items-center text-sm text-muted-foreground">
              <Mail className="w-4 h-4 mr-2 flex-shrink-0" />
              <span className="pl-1">{profileData.user.email}</span>
            </div>
          )}
          {profileData?.user?.phone_number && (
            <div className="flex items-center text-sm text-muted-foreground">
              <Phone className="w-4 h-4 mr-2 flex-shrink-0" />
              <span className="pl-1">{profileData.user.phone_number}</span>
            </div>
          )}
          {profileData?.profile?.organization && (
            <div
              className="flex items-center text-sm text-muted-foreground"
              title={profileData.profile.organization}
            >
              <GraduationCap className="w-4 h-4 mr-2 flex-shrink-0" />
              <span className="pl-1">
                {truncateWithEllipsis(profileData.profile.organization, 30)}
              </span>
            </div>
          )}

          {showMore && (
            <>
              {profileData?.profile?.location && (
                <div
                  className="flex items-center text-sm text-muted-foreground"
                  title={profileData.profile.location}
                >
                  <MapPin className="w-4 h-4 mr-2 flex-shrink-0" />
                  <span className="pl-1">
                    {truncateWithEllipsis(profileData.profile.location, 30)}
                  </span>
                </div>
              )}
              {profileData?.profile?.specialization && (
                <div className="flex items-center text-sm text-muted-foreground">
                  <Book className="w-4 h-4 mr-2 flex-shrink-0" />
                  <span className="pl-1">
                    {profileData.profile.specialization}
                  </span>
                </div>
              )}
              {profileData?.profile?.bio && (
                <div className="flex items-center text-sm text-muted-foreground">
                  <UserIcon className="w-4 h-4 mr-2 flex-shrink-0" />
                  <span className="pl-1">{profileData.profile.bio}</span>
                </div>
              )}
              {profileData?.profile?.education_level && (
                <div className="flex items-center text-sm text-muted-foreground">
                  <Award className="w-4 h-4 mr-2 flex-shrink-0" />
                  <span className="pl-1">
                    {profileData.profile.education_level}
                  </span>
                </div>
              )}
            </>
          )}
          <div className="flex justify-center mt-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowMore(v => !v)}
            >
              {showMore ? 'Show less' : 'Show more'}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
