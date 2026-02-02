import { ClassTranslator, ensureCsrfToken } from '@/shared/lib'
import { apiClient } from '@/shared/api'
import axios from 'axios'

export interface TestHistoryResponse {
  history: any[]
  config: {
    can_attempt: boolean
    show_correct_answers: boolean
    attempts_used: number
    max_attempts: number | 'unlimited'
    remaining_attempts: number | 'unlimited'
  }
}

export interface TestAnswerPayload {
  order: number
  selected_options: string[]
}

export interface SubmitTestRequest {
  testId: string
  test_type: 'course_test' | 'module_test' | 'public'
  answers: TestAnswerPayload[]
}

export interface QuestionResult {
  order: number
  is_correct: boolean
  points_awarded: number
  max_points: number
  selected_choices: string[]
  explanation?: string | null
  correct_choices?: string[]
}

export interface TestResultData {
  id: string
  score: number
  max_score: number
  passed: boolean
  percent: number
  questions_result: QuestionResult[]
}

export interface SubmitTestResponse {
  message: string
  result: TestResultData
}

class TestAttemptService {
  private t = ClassTranslator.translate

  async getTestHistory(
    testId: string,
    test_type: string
  ): Promise<TestHistoryResponse> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      const response = await apiClient.get<TestHistoryResponse>(
        `/test/get-history-test-attempts/${testId}/`,
        {
          params: { test_type: test_type },
          headers: {
            'X-CSRFToken': csrfToken || '',
          },
          withCredentials: true,
        }
      )

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
          this.t('Не вдалось отримати історію тестувань. ') + serverMessage
        )
      }
      throw new Error(this.t('Невідома помилка при отриманні історії тестів.'))
    }
  }

  async submitAttempt({
    testId,
    test_type,
    answers,
  }: SubmitTestRequest): Promise<SubmitTestResponse> {
    try {
      const csrfToken = await ensureCsrfToken(this.t)

      const response = await apiClient.post<SubmitTestResponse>(
        `/test/start-test-attempt/${testId}/`,
        {
          test_type,
          answers,
        },
        {
          headers: {
            'X-CSRFToken': csrfToken || '',
          },
          withCredentials: true,
        }
      )

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
          this.t('Не вдалось відправити відповіді. ') + serverMessage
        )
      }
      throw new Error(this.t('Невідома помилка при проходженні тесту.'))
    }
  }
}

export const testAttemptService = new TestAttemptService()
