import { useEffect, useState } from 'react'
import { type AllCoursesResponse, getCourseService } from '@/features/courses'
import type { AllCourseRequest } from '@/features/courses/get.course.service.ts'

class CourseStore {
  private coursesData: AllCoursesResponse | null = null
  private loading = false
  private error = ''
  private listeners: Array<() => void> = []
  private loadPromise: Promise<void> | null = null
  private lastRequest: AllCourseRequest | null = null

  subscribe(listener: () => void) {
    this.listeners.push(listener)
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener)
    }
  }

  private notify() {
    this.listeners.forEach(listener => listener())
  }

  async loadCourses(request: AllCourseRequest) {
    const requestKey = JSON.stringify(request)
    if (
      this.loadPromise &&
      this.lastRequest &&
      JSON.stringify(this.lastRequest) === requestKey
    ) {
      return this.loadPromise
    }

    this.lastRequest = request
    this.loadPromise = this.doLoadCourses(request)

    try {
      await this.loadPromise
    } finally {
      this.loadPromise = null
    }
  }

  private async doLoadCourses(request: AllCourseRequest) {
    try {
      this.loading = true
      this.error = ''
      this.notify()

      const response = await getCourseService.getAllCourses(request)
      this.coursesData = response
    } catch (err: unknown) {
      if (err instanceof Error) {
        this.error = err.message
      } else {
        this.error = String(err)
      }
      this.coursesData = null
    } finally {
      this.loading = false
      this.notify()
    }
  }

  async refreshCourses(request: AllCourseRequest) {
    await this.loadCourses(request)
  }

  clearCourses() {
    this.coursesData = null
    this.loading = false
    this.error = ''
    this.notify()
  }

  getCoursesData() {
    return this.coursesData
  }

  isLoading() {
    return this.loading
  }

  getError() {
    return this.error
  }
}

const courseStore = new CourseStore()

export const useCoursesData = (request: AllCourseRequest) => {
  const [, forceUpdate] = useState({})

  useEffect(() => {
    const unsubscribe = courseStore.subscribe(() => forceUpdate({}))
    courseStore.loadCourses(request)
    return unsubscribe
  }, [JSON.stringify(request)])

  return {
    coursesData: courseStore.getCoursesData(),
    loading: courseStore.isLoading(),
    error: courseStore.getError(),
    refreshCourses: () => courseStore.refreshCourses(request),
    clearCourses: () => courseStore.clearCourses(),
  }
}
