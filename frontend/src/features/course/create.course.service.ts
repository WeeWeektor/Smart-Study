import { ClassTranslator, ensureCsrfToken } from '@/shared/lib'
import { apiClient } from '@/shared/api'
import axios from 'axios'
import {
  type BlockData,
  type CourseStructure,
  type Lesson,
  type Question,
} from '@/shared/ui'

export interface CreateCourseResponse {
  message: string
  status: number
}

interface CreateCourseRequestData {
  title: string
  description: string
  category: string
  is_published: boolean
  level: string
  course_language: string
  time_to_complete: string
  cover_imageFile?: File | null
  courseStructure?: CourseStructure['courseStructure']
}

class CreateCourseService {
  private t = ClassTranslator.translate

  async createCourse(
    requestData: CreateCourseRequestData
  ): Promise<CreateCourseResponse> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      const formData = new FormData()
      const { cover_imageFile, courseStructure, ...data } = requestData

      const cleanCourseStructure = this.processStructureAndExtractFiles(
        courseStructure,
        formData
      )

      const jsonData = {
        ...data,
        courseStructure: cleanCourseStructure,
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

      return {
        message: response.data.message,
        status: response.status,
      }
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

        throw new Error(this.t('Не вдалось зберегти курс: ') + serverMessage)
      }
      throw new Error(this.t('Невідома помилка при створенні курсу'))
    }
  }

  private processStructureAndExtractFiles(
    structure: CreateCourseRequestData['courseStructure'],
    formData: FormData
  ) {
    if (!structure) {
      return []
    }

    return structure.map(item => {
      if (item.type === 'module') {
        const cleanModuleStructure = item.moduleStructure.map(moduleItem => {
          if (moduleItem.type === 'module-test') {
            return this.processTest(moduleItem, formData, `m${item.order}`)
          }
          if (moduleItem.type === 'lesson') {
            return this.processLesson(moduleItem, formData, `m${item.order}`)
          }
          return moduleItem
        })
        return { ...item, moduleStructure: cleanModuleStructure }
      }

      if (item.type === 'course-test') {
        return this.processTest(item, formData, 'course')
      }

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

      return {
        ...block,
        data: cleanData,
      }
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

      return {
        ...data,
        file: null,
        fileKey: key,
      } as any
    }

    return data
  }

  private processTest<T extends { order: number; questions: Question[] }>(
    test: T,
    formData: FormData,
    prefix: string
  ): T {
    const cleanQuestions = test.questions.map(q => {
      if (q.imageFile && q.imageFile instanceof File) {
        const fileKey = `question_image_${prefix}_t${test.order}_q${q.order}`

        formData.append(fileKey, q.imageFile)

        const { imageFile, image, ...restOfQuestion } = q
        return {
          ...restOfQuestion,
          imageFileKey: fileKey,
        }
      }
      return q
    })

    return { ...test, questions: cleanQuestions }
  }
}

export const createCourseService = new CreateCourseService()
