import { ClassTranslator, ensureCsrfToken } from '@/shared/lib'
import { apiClient, handleApiError } from '@/shared/api'
import { type BlockData, type Lesson, type Question } from '@/shared/ui'

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

      const flatStructure = this.flattenStructure(cleanNestedStructure)

      const jsonData = {
        ...data,
        ...flatStructure,
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

      const flatStructure = this.flattenStructure(cleanNestedStructure)

      const jsonData = {
        ...data,
        ...flatStructure,
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
      throw handleApiError(
        error,
        'Не вдалось оновити курс: ',
        this.t,
        'Невідома помилка при редагуванні курсу'
      )
    }
  }

  private flattenStructure(cleanNestedStructure: any[]) {
    const backendData: any = { courseStructure: [] }

    if (!cleanNestedStructure) return backendData

    cleanNestedStructure.forEach(item => {
      if (item.type === 'module') {
        backendData.courseStructure.push({
          type: 'module',
          order: item.order,
          title: item.title,
          module_id: item.module_id,
        })

        const contentKey = `moduleStructure_order_${item.order}`

        backendData[contentKey] = item.moduleStructure.map((subItem: any) => {
          if (subItem.type === 'lesson') {
            const pad = (n: number) => String(n || 0).padStart(2, '0')
            const dur = subItem.duration
            const durationStr = dur
              ? `${pad(dur.days)}:${pad(dur.hours)}:${pad(dur.minutes)}`
              : '00:00:00'

            return {
              ...subItem,
              content_type: subItem.typeCategory,
              duration: durationStr,
              lesson_id: subItem.lesson_id,
            }
          }
          if (subItem.type === 'module-test' || subItem.type === 'test') {
            return {
              type: 'test',
              test_id: subItem.test_id,
              title: subItem.title,
              order: subItem.order,
              time_limit: subItem.time_limit,
            }
          }
          return subItem
        })
      } else if (item.type === 'course-test' || item.type === 'test') {
        backendData.courseStructure.push({
          type: 'test',
          test_id: item.test_id,
          title: item.title,
          order: item.order,
          time_limit: item.time_limit,
        })
      }
    })

    return backendData
  }

  private processStructureAndExtractFiles(
    structure: any[] | undefined,
    formData: FormData
  ) {
    if (!structure) return []

    return structure.map(item => {
      if (item.type === 'module') {
        const cleanModuleStructure = item.moduleStructure.map(
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

  private processLesson(
    lesson: Lesson,
    formData: FormData,
    prefix: string
  ): Lesson {
    const lessonPrefix = `${prefix}_l${lesson.order}`

    const cleanContentBlocks = lesson.contentBlocks?.map((block, index) => {
      const fileKey = `lesson_file_${lessonPrefix}_b${index}`
      const cleanData = this.extractFileFromData(block.data, formData, fileKey)
      return { ...block, data: cleanData }
    })

    const singleFileKey = `lesson_file_${lessonPrefix}_single`
    const cleanSingleData = this.extractFileFromData(
      lesson.singleContentData,
      formData,
      singleFileKey
    )

    return {
      ...lesson,
      contentBlocks: cleanContentBlocks || [],
      singleContentData: cleanSingleData,
    }
  }

  private extractFileFromData(
    data: BlockData,
    formData: FormData,
    key: string
  ): BlockData {
    if (
      data &&
      typeof data === 'object' &&
      'file' in data &&
      data.file instanceof File
    ) {
      formData.append(key, data.file)
      return { ...data, file: null, fileKey: key } as any
    }
    return data
  }

  private processTest<
    T extends {
      order: number
      questions: Question[]
    },
  >(test: T, formData: FormData, prefix: string): T {
    if (!test.questions) return test

    const cleanQuestions = test.questions.map(q => {
      if (q.imageFile && q.imageFile instanceof File) {
        const fileKey = `question_image_${prefix}_t${test.order}_q${q.order}`
        formData.append(fileKey, q.imageFile)
        const { imageFile, image, ...restOfQuestion } = q
        return { ...restOfQuestion, imageFileKey: fileKey }
      }
      return q
    })

    return { ...test, questions: cleanQuestions }
  }
}

export const createCourseService = new CreateCourseService()
