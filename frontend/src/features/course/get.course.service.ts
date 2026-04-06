import { ClassTranslator, ensureCsrfToken } from '@/shared/lib'
import { apiClient } from '@/shared/api'
import type {
  AllCoursesResponse,
  MyCourseCatalogResponse,
} from '@/features/course/types.ts'

export const sorting = (t: (key: string) => string) => [
  { value: 'most_popular', label: t('За Популярністю') },
  { value: 'highest_rated', label: t('За Рейтингом') },
  { value: 'newest', label: t('Спершу Нові') },
  { value: 'oldest', label: t('Спершу Старі') },
]

export const statues = (t: (key: string) => string) => [
  { value: 'is_published', label: t('Опубліковані') },
  { value: 'false', label: t('Неопубліковані') },
]

export interface AllCourseRequest {
  category?: string[]
  level?: string
  search?: string
  status?: string
  sort_keys?: string[]
  page: number
  author_id?: string
  is_owner?: boolean
}

export interface CountTeacherCourseRequest {
  author_id: string
  owner: boolean
}

export interface CountCourseResponse {
  count: number
}

export interface CountTeacherCourseResponse {
  allCourses: number
  publishedCourses: number
}

export interface CourseRequest {
  course_id: string
  for_edit?: boolean
}

export interface CourseResponse {
  status: string
  message: string
  course: any
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

  async getCountTeacherCourses({
    author_id,
    owner,
  }: CountTeacherCourseRequest): Promise<CountTeacherCourseResponse> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      const urls = `/counter/teacher-courses/?author=${author_id}&owner=${owner.toString()}`

      const response = await apiClient.get<CountTeacherCourseResponse>(urls, {
        headers: {
          'X-CSRFToken': csrfToken || '',
        },
        withCredentials: true,
      })
      return {
        allCourses: response.data.allCourses,
        publishedCourses: response.data.publishedCourses,
      }
    } catch (error) {
      throw new Error(this.t('Не вдалось завантажити кількість курсів') + error)
    }
  }

  async getAllCourses({
    category,
    level,
    search,
    status,
    sort_keys,
    page,
    author_id,
    is_owner,
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

      let query_search = ''
      if (search && search.length > 0) {
        query_search = '/' + search
      }

      let urls = ''
      if (author_id) {
        if (is_owner) {
          if (status === '') {
            status = 'all'
          }
          query.push(`status=${status}`)
        }

        urls = `/course/courses-list${query_search}/?author=${author_id}&${query.join('&')}`
      } else {
        urls = `/course/courses-list${query_search}/?${query.join('&')}`
      }

      const response = await apiClient.get<AllCoursesResponse>(urls, {
        headers: {
          'X-CSRFToken': csrfToken || '',
        },
        withCredentials: true,
      })

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

  async getCourse({
    course_id,
    for_edit = false,
  }: CourseRequest): Promise<CourseResponse> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      let urls = `/course/course/${course_id}/`
      if (for_edit) {
        urls = `/course/course/${course_id}/?edit=${for_edit}`
      }

      const response = await apiClient.get<CourseResponse>(urls, {
        headers: {
          'X-CSRFToken': csrfToken || '',
        },
        withCredentials: true,
      })
      return response.data
    } catch (error) {
      throw new Error(this.t('Не вдалось завантажити курс') + error)
    }
  }

  async getMyCourseCatalog(): Promise<MyCourseCatalogResponse> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      const response = await apiClient.get<MyCourseCatalogResponse>(
        '/course/get-user-course/',
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
        in_wishlist: response.data.in_wishlist,
        is_enrolled: response.data.is_enrolled,
        is_completed: response.data.is_completed,
      }
    } catch (error) {
      throw new Error(
        this.t('Не вдалось завантажити мій каталог курсів') + error
      )
    }
  }
}

export const getCourseService = new GetCourseService()
