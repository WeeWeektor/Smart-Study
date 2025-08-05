import { Button } from '@/shared/ui'
import { Camera } from 'lucide-react'
import * as React from 'react'

interface UploadAvatarProps {
  onFileSelect: (e: React.ChangeEvent<HTMLInputElement>) => void
}

export const UploadAvatar = ({ onFileSelect }: UploadAvatarProps) => {
  return (
    <div className="absolute -bottom-2 -right-2">
      <input
        type="file"
        id="profile-photo"
        accept="image/jpeg,image/png,image/webp"
        className="hidden"
        onChange={onFileSelect}
      />
      <Button
        size="sm"
        className="rounded-full w-8 h-8 p-0 bg-brand-600 dark:bg-brand-500 hover:bg-brand-700 dark:hover:bg-brand-400"
        onClick={() => document.getElementById('profile-photo')?.click()}
      >
        <Camera className="w-4 h-4 text-white" />
      </Button>
    </div>
  )
}
