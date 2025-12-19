export interface AllCoursesResponse {
  status: string
  message: string
  page: number
  total_courses: number
  total_pages: number
  courses: CourseWrapper[]
  average_rating: number
  certificates_issued: number
  count_announcements: number
}

export interface CourseWrapper {
  course: Course
}

export interface Course {
  id: string
  title: string
  description: string
  category: string
  owner: Owner
  cover_image: string
  is_published: boolean
  created_at: string
  published_at: string
  updated_at: string | null
  version: number
  details: CourseDetails
  structure_ids: string
  structure: CourseStructure
}

export interface Owner {
  id: string
  name: string
  surname: string
  email: string
  profile_picture: string | null
}

export interface CourseDetails {
  total_modules: number
  total_lessons: number
  total_tests: number
  time_to_complete: string
  course_language: string
  rating: number
  level: 'beginner' | 'intermediate' | 'advanced'
  number_completed: number
  number_of_active: number
  feedback_count: number
  feedback_summary: FeedbackSummary
}

export interface CourseStructure {
  _id: string
  structure?: CourseStructureElement[]
}

export type FeedbackSummary = Partial<{
  '1': number
  '2': number
  '3': number
  '4': number
  '5': number
}>

export type CourseStructureElement = TestElement | ModuleElement

export type TestElement = {
  type: 'test'
  test_id: string
  title: string
  order: number
}

export type ModuleElement = {
  type: 'module'
  module_id: string
  title: string
  order: number
  structure?: ModuleStructureElement[]
}

export type ModuleStructureElement = LessonElement | TestElement

export type LessonElement = {
  type: 'lesson'
  lesson_id: string
  title: string
  order: number
}

export interface ReviewUser {
  id: string
  name: string
  surname: string
  profile_picture?: string | null
}

export interface Review {
  id: string
  course_id: string
  user: ReviewUser
  rating: number
  comment: string
  created_at: string
  is_verified?: boolean
}

export interface GetReviewsResponse {
  course_id: string
  reviews: Review[]
}

export interface CreateReviewResponse {
  message: string
  review: Review
}

export interface CreateReviewRequest {
  course_id: string
  rating: number
  comment: string
}
