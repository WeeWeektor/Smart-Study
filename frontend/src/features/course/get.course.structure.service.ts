import { ClassTranslator, ensureCsrfToken } from '@/shared/lib'
import { apiClient } from '@/shared/api'
import type { CourseStructureResponse } from '@/features/course'

export interface CourseStructureRequest {
  course_id: string
}

class GetCourseStructureService {
  private t = ClassTranslator.translate

  async getCourseStructure({
    course_id,
  }: CourseStructureRequest): Promise<CourseStructureResponse> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      const response = await apiClient.get<CourseStructureResponse>(
        `/course/course-structure/${course_id}/`,
        {
          headers: {
            'X-CSRFToken': csrfToken || '',
          },
          withCredentials: true,
        }
      )
      return response.data
    } catch (error) {
      throw new Error(this.t('Не вдалось завантажити структуру курсу') + error)
    }
  }
}

export const getCourseStructureService = new GetCourseStructureService()
