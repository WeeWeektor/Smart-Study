import { ClassTranslator, ensureCsrfToken } from '@/shared/lib'
import { apiClient, handleApiError } from '@/shared/api'

export interface CreateCourseResponse {
  message: string
  status: number
}

export interface CourseRequestData {
  title: string
  description: string
  category: string
  is_published: boolean
  level: string
  course_language: string
  time_to_complete: string
  cover_imageFile?: File | null
  courseStructure?: any[]
  change_info_course?: boolean
  change_structure_course?: boolean
}

class CreateCourseService {
  private t = ClassTranslator.translate

  async createCourse(
    requestData: CourseRequestData
  ): Promise<CreateCourseResponse> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)
      const formData = new FormData()

      const {
        cover_imageFile,
        courseStructure,
        change_info_course,
        change_structure_course,
        ...data
      } = requestData

      const cleanNestedStructure = this.processStructureAndExtractFiles(
        courseStructure,
        formData
      )

      const jsonData = {
        ...data,
        courseStructure: cleanNestedStructure,
      }
      formData.append('data', JSON.stringify(jsonData))

      if (cover_imageFile) {
        formData.append('cover_image', cover_imageFile)
      }

      const response = await apiClient.post<CreateCourseResponse>(
        `/course/create-course/`,
        formData,
        {
          headers: {
            'X-CSRFToken': csrfToken || '',
            'Content-Type': 'multipart/form-data',
          },
          withCredentials: true,
        }
      )

      return { message: response.data.message, status: response.status }
    } catch (error: unknown) {
      console.error(error)
      throw handleApiError(
        error,
        'Не вдалось створити курс: ',
        this.t,
        'Невідома помилка при створенні курсу'
      )
    }
  }

  async updateCourse({
    courseId,
    requestData,
  }: {
    courseId: string
    requestData: CourseRequestData
  }): Promise<CreateCourseResponse> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)
      const formData = new FormData()

      const {
        cover_imageFile,
        courseStructure,
        change_info_course,
        change_structure_course,
        ...data
      } = requestData

      const cleanNestedStructure = this.processStructureAndExtractFiles(
        courseStructure,
        formData
      )

      const jsonData = {
        ...data,
        courseStructure: cleanNestedStructure,
      }
      formData.append('data', JSON.stringify(jsonData))

      if (cover_imageFile) {
        formData.append('cover_image', cover_imageFile)
      }

      if (change_info_course) formData.append('change_info_course', 'true')
      if (change_structure_course)
        formData.append('change_structure_course', 'true')

      const response = await apiClient.patch<CreateCourseResponse>(
        `/course/change-course/${courseId}/`,
        formData,
        {
          headers: {
            'X-CSRFToken': csrfToken || '',
            'Content-Type': 'multipart/form-data',
          },
          withCredentials: true,
        }
      )

      return { message: response.data.message, status: response.status }
    } catch (error: unknown) {
      console.error(error)
      throw handleApiError(
        error,
        'Не вдалось оновити курс: ',
        this.t,
        'Невідома помилка при редагуванні курсу'
      )
    }
  }

  public processStructureAndExtractFiles(
    structure: any[] | undefined,
    formData: FormData
  ) {
    if (!structure) return []

    return structure.map(item => {
      if (item.type === 'module') {
        const currentModuleStructure = item.moduleStructure || []

        const cleanModuleStructure = currentModuleStructure.map(
          (moduleItem: any) => {
            if (moduleItem.type === 'module-test')
              return this.processTest(moduleItem, formData, `m${item.order}`)
            if (moduleItem.type === 'lesson')
              return this.processLesson(moduleItem, formData, `m${item.order}`)
            return moduleItem
          }
        )
        return { ...item, moduleStructure: cleanModuleStructure }
      }

      if (item.type === 'course-test')
        return this.processTest(item, formData, 'course')

      return item
    })
  }

  private processLesson(lesson: any, formData: FormData, prefix: string): any {
    const lessonPrefix = `${prefix}_l${lesson.order}`

    const cleanContentBlocks = lesson.contentBlocks?.map(
      (block: any, index: number) => {
        const fileKey = `lesson_file_${lessonPrefix}_b${index}`
        const cleanData = this.extractFileFromData(
          block.data,
          formData,
          fileKey
        )
        return { ...block, data: cleanData }
      }
    )

    const singleFileKey = `lesson_file_${lessonPrefix}_single`
    const cleanSingleData = this.extractFileFromData(
      lesson.singleContentData,
      formData,
      singleFileKey
    )

    const pad = (n: number) => String(n || 0).padStart(2, '0')
    const dur = lesson.duration
    const durationStr = dur
      ? `${pad(dur.days)}:${pad(dur.hours)}:${pad(dur.minutes)}`
      : '00:00:00'

    return {
      ...lesson,
      content_type: lesson.typeCategory || lesson.content_type,
      duration: durationStr,
      contentBlocks: cleanContentBlocks || [],
      singleContentData: cleanSingleData,
    }
  }

  private extractFileFromData(data: any, formData: FormData, key: string): any {
    if (
      data &&
      typeof data === 'object' &&
      'file' in data &&
      data.file instanceof File
    ) {
      formData.append(key, data.file)
      return { ...data, file: null, fileKey: key }
    }
    return data
  }

  private processTest<
    T extends {
      order: number
      questions?: any
      type: string
    },
  >(test: T, formData: FormData, prefix: string): T {
    let cleanQuestions = test.questions

    if (Array.isArray(test.questions)) {
      cleanQuestions = test.questions.map(q => {
        const backendQuestion = {
          ...q,
          correct_answers: q.correctAnswers || q.correct_answers || [],
        }

        delete backendQuestion.correctAnswers

        if (
          backendQuestion.imageFile &&
          backendQuestion.imageFile instanceof File
        ) {
          const fileKey = `question_image_${prefix}_t${test.order}_q${q.order}`
          formData.append(fileKey, backendQuestion.imageFile)
          const { imageFile, image, ...restOfQuestion } = backendQuestion
          return { ...restOfQuestion, imageFileKey: fileKey }
        }
        return backendQuestion
      })
    }

    return {
      ...test,
      type: test.type,
      questions: cleanQuestions,
    }
  }
}

export const createCourseService = new CreateCourseService()
