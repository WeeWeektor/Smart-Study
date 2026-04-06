import type { CourseStructureResponse, NormalizedItem } from '@/features/course'

export const normalizeCourseStructure = (
  data: CourseStructureResponse | null
): NormalizedItem[] => {
  if (!data || !data.courseStructure) return []

  return data.courseStructure.map(item => {
    if (item.type === 'test') {
      return {
        id: item.test_id || `test-${item.order}`,
        type: 'course-test',
        title: item.title,
        order: item.order,
        meta: item.time_limit ? `${item.time_limit} хв` : undefined,
      }
    }

    if (item.type === 'module') {
      const structureKey = `moduleStructure_order_${item.order}`
      const rawChildren = data[structureKey] as any[] | undefined

      const children: NormalizedItem[] = rawChildren
        ? rawChildren.map(child => ({
            id: child.lesson_id || child.test_id || `child-${child.order}`,
            type: child.type === 'test' ? 'module-test' : 'lesson',
            title: child.title,
            order: child.order,
            meta:
              child.duration ||
              (child.time_limit ? `${child.time_limit} хв` : undefined),
          }))
        : []

      return {
        id: item.module_id || `module-${item.order}`,
        type: 'module',
        title: item.title,
        order: item.order,
        children,
        isOpen: false,
      }
    }

    return {
      id: `unknown-${item.order}`,
      type: 'lesson',
      title: item.title,
      order: item.order,
    }
  })
}
