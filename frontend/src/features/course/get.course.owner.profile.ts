import { ClassTranslator, ensureCsrfToken } from '@/shared/lib'
import { apiClient } from '@/shared/api'

export interface CourseOwnerProfileRequest {
  course_id: string
}

export interface CourseOwnerProfileResponse {
  status: string
  message: string
  userData: {
    owner: {
      id: string
      name: string
      surname: string
      email?: string
      phone_number?: string | null
    }
    profile: {
      bio?: string | null
      profile_picture: string | null
      location?: string | null
      organization?: string | null
      specialization?: string | null
      education_level?: string | null
    }
    settings: {
      show_profile_to_others: boolean
      show_achievements: boolean
    }
  }
}

class GetCourseOwnerProfileService {
  private t = ClassTranslator.translate

  async getCourseOwnerProfile({
    course_id,
  }: CourseOwnerProfileRequest): Promise<CourseOwnerProfileResponse> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      const response = await apiClient.get<CourseOwnerProfileResponse>(
        `/course/course-owner-profile/${course_id}/`,
        {
          headers: {
            'X-CSRFToken': csrfToken || '',
          },
          withCredentials: true,
        }
      )
      return response.data
    } catch (error) {
      throw new Error(
        this.t('Не вдалось завантажити інформацію про автора курсу') + error
      )
    }
  }
}

export const getCourseOwnerProfileService = new GetCourseOwnerProfileService()
