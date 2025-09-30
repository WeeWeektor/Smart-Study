import { ClassTranslator, ensureCsrfToken } from '@/shared/lib'
import { apiClient } from '@/shared/api'
import type { AllCoursesResponse } from '@/features/courses/types.ts'

export interface AllCourseRequest {
  category?: string[]
  level?: string
  search?: string
  page: number
}

export interface CountCourseResponse {
  count: number
}

class GetCourseService {
  private t = ClassTranslator.translate

  async getCountAllCourses(): Promise<CountCourseResponse> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      const response = await apiClient.get<CountCourseResponse>(
        '/counter/all-published-courses/',
        {
          headers: {
            'X-CSRFToken': csrfToken || '',
          },
          withCredentials: true,
        }
      )
      return { count: response.data.count }
    } catch (error) {
      throw new Error(this.t('Не вдалось завантажити кількість курсів') + error)
    }
  }

  async getAllCourses({
    category,
    level,
    search,
    page,
  }: AllCourseRequest): Promise<AllCoursesResponse> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      const query: string[] = []
      if (category && category.length > 0) {
        query.push(`cate=${category.join(',')}`)
      }
      if (level) {
        query.push(`level=${level}`)
      }

      query.push(`page=${page}`)

      const response = await apiClient.get<AllCoursesResponse>(
        `/course/courses-list${'/' + search}/?${query.join('&')}`,
        {
          headers: {
            'X-CSRFToken': csrfToken || '',
          },
          withCredentials: true,
        }
      )

      return {
        status: response.data.status,
        message: response.data.message,
        page: response.data.page,
        total_courses: response.data.total_courses,
        total_pages: response.data.total_pages,
        courses: response.data.courses,
      }
    } catch (error) {
      throw new Error(this.t('Курси не вдалось завантажити') + error)
    }
  }
}

export const getCourseService = new GetCourseService()
