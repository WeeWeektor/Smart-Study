export interface BackendCourseItem {
  type: 'module' | 'test'
  module_id?: string
  test_id?: string
  title: string
  order: number
  time_limit?: number
}

export interface BackendModuleContentItem {
  type: 'lesson' | 'test'
  lesson_id?: string
  test_id?: string
  title: string
  order: number
  content_type?: string
  duration?: string
  time_limit?: number
}

export interface CourseStructureResponse {
  status: string
  message: string
  courseStructure: BackendCourseItem[]

  [key: string]: unknown
}

export interface NormalizedItem {
  id: string
  type: 'module' | 'lesson' | 'module-test' | 'course-test'
  title: string
  order: number
  meta?: string
  children?: NormalizedItem[]
  isOpen?: boolean
}
