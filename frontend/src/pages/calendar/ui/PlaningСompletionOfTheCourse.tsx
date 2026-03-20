import { useI18n } from '@/shared/lib'

interface PlaningProps {
  courseId: string
  courseTitle: string
  onSave: (data: any) => void
  onCancel: () => void
}

export const PlaningCompletionOfTheCourse = ({
  courseId,
  courseTitle,
  onSave,
  onCancel,
}: PlaningProps) => {
  const { t } = useI18n()

  return <div></div>
}
