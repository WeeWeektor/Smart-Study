import { ClassTranslator, ensureCsrfToken } from '@/shared/lib'
import { apiClient } from '@/shared/api'
import type { AllCoursesResponse } from '@/features/courses/types.ts'

export const sorting = (t: (key: string) => string) => [
  { value: 'most_popular', label: t('За Популярністю') },
  { value: 'highest_rated', label: t('За Рейтингом') },
  { value: 'newest', label: t('Спершу Нові') },
  { value: 'oldest', label: t('Спершу Старі') },
]

export interface AllCourseRequest {
  category?: string[]
  level?: string
  search?: string
  sort_keys?: string[]
  page: number
  author_id?: number
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
    sort_keys,
    page,
    author_id,
  }: AllCourseRequest): Promise<AllCoursesResponse> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      const query: string[] = []
      if (category && category.length > 0 && !author_id) {
        query.push(`cate=${category.join(',')}`)
      }
      if (level && level !== '' && !author_id) {
        query.push(`level=${level}`)
      }
      if (sort_keys && sort_keys.length > 0) {
        query.push(`sort=${sort_keys.join(',')}`)
      }

      query.push(`page=${page}`)

      const response = await apiClient.get<AllCoursesResponse>(
        `/course/courses-list${'/' + author_id}${'/' + search}/?${query.join('&')}`,
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
        average_rating: response.data.average_rating,
        certificates_issued: response.data.certificates_issued,
        count_announcements: response.data.count_announcements,
      }
    } catch (error) {
      throw new Error(this.t('Курси не вдалось завантажити') + error)
    }
  }
}

export const getCourseService = new GetCourseService()
