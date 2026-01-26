import { ClassTranslator, ensureCsrfToken } from '@/shared/lib'
import axios from 'axios'
import { apiClient } from '@/shared/api'

export interface ElementOfCourseRequest {
  elementId: string
  elementType: 'lesson' | 'module-test' | 'course-test'
}

export interface Question {
  questionText: string
  choices: string[]
  correct_answers: string[]
  points: number
  order: number
  explanation: string | null
  image_url: string
}

export interface Lesson {
  id: string
  module_id: string
  title: string
  description: string
  content_type: string
  content: string
  order: number
  duration: number
}

interface BaseTest {
  id: string
  title: string
  description: string
  time_limit: number
  count_attempts: number
  pass_score: number
  randomize_questions: boolean
  show_correct_answers: boolean
  test_data_ids: string
  order: number
  is_public: boolean
  questions: Question[]
}

export interface TestModuleInfo {
  id: string
  course: string
  title: string
  is_published: boolean
  description: string | null
}

export interface TestCourseInfo {
  id: string
  title: string
  'course owner': string
  is_published: boolean
  'course version': number
}

export interface ModuleTest extends BaseTest {
  module: TestModuleInfo
}

export interface CourseTest extends BaseTest {
  course: TestCourseInfo
}

export interface LessonResponse {
  status: string
  message: string
  lesson: Lesson
  'module-test'?: never
  'course-test'?: never
}

export interface ModuleTestResponse {
  status: string
  message: string
  'module-test': ModuleTest
  lesson?: never
  'course-test'?: never
}

export interface CourseTestResponse {
  status: string
  message: string
  'course-test': CourseTest
  lesson?: never
  'module-test'?: never
}

export type ElementOfCourseResponse =
  | LessonResponse
  | ModuleTestResponse
  | CourseTestResponse

class ElementOfCourseService {
  private t = ClassTranslator.translate

  async getElementOfCourse({
    elementId,
    elementType,
  }: ElementOfCourseRequest): Promise<ElementOfCourseResponse> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)
      let url = ''
      const params: Record<string, boolean> = {}

      if (elementType === 'lesson') {
        url = `/lesson/lesson/${elementId}/`
      } else {
        if (elementType === 'module-test') {
          url = `/test/module-test/${elementId}/`
          params.module = true
        } else if (elementType === 'course-test') {
          url = `/test/course-test/${elementId}/`
          params.course = true
        }
      }

      const response = await apiClient.get<ElementOfCourseResponse>(url, {
        params: params,

        headers: {
          'X-CSRFToken': csrfToken || '',
        },
        withCredentials: true,
      })

      return response.data
    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        let serverMessage =
          error.response?.data?.message ||
          error.response?.data ||
          this.t('Помилка з’єднання з сервером')

        if (typeof serverMessage === 'string') {
          const match = serverMessage.match(/\['(.+)'\]/)
          if (match && match[1]) {
            serverMessage = match[1]
          }
        }

        throw new Error(
          this.t('Не вдалось отримати елемент курсу') + serverMessage
        )
      }
      throw new Error(this.t('Невідома помилка при отримані елемента курсу.'))
    }
  }
}

export const elementOfCourseService = new ElementOfCourseService()
