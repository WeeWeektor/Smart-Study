import { parseDurationFromISO } from '@/shared/lib'

const areDurationsEqual = (val1: any, val2: any) => {
  const d1 = typeof val1 === 'string' ? parseDurationFromISO(val1) : val1
  const d2 = typeof val2 === 'string' ? parseDurationFromISO(val2) : val2

  if (!d1 && !d2) return true
  if (!d1 || !d2) return false

  return (
    Number(d1.days || 0) === Number(d2.days || 0) &&
    Number(d1.hours || 0) === Number(d2.hours || 0) &&
    Number(d1.minutes || 0) === Number(d2.minutes || 0)
  )
}

const areContentBlocksEqual = (blocks1: any[], blocks2: any[]) => {
  const simplify = (blocks: any[]) => {
    return (blocks || []).map(block => {
      const { id, url, previewUrl, fileKey, ...pureData } = block

      if (pureData.data && typeof pureData.data === 'object') {
        const { previewUrl: _, fileKey: __, ...actualData } = pureData.data
        pureData.data = actualData
      }

      return pureData
    })
  }

  return JSON.stringify(simplify(blocks1)) === JSON.stringify(simplify(blocks2))
}

export const getElementDiff = (current: any, original: any) => {
  if (!original) return { ...current, action: 'create' }

  const diff: any = {}
  let hasChanges = false

  const scalarFields = [
    'title',
    'description',
    'typeCategory',
    'comment',
    'order',
    'time_limit',
    'count_attempts',
    'pass_score',
    'random_questions',
    'show_correct_answers',
  ]

  scalarFields.forEach(field => {
    if (current[field] !== undefined) {
      const curVal = JSON.stringify(current[field])
      const origVal = JSON.stringify(original[field])

      if (curVal !== origVal) {
        diff[field] = current[field]
        hasChanges = true
      }
    }
  })

  if (!areDurationsEqual(current.duration, original.duration)) {
    diff.duration = current.duration
    hasChanges = true
  }

  const currentBlocks = current.contentBlocks || []
  const originalBlocks = original.contentBlocks || []

  if (!areContentBlocksEqual(currentBlocks, originalBlocks)) {
    diff.contentBlocks = current.contentBlocks
    diff.singleContentData = current.singleContentData
    hasChanges = true
  }

  if (current.questions) {
    const curQ = JSON.stringify(current.questions)
    const origQ = JSON.stringify(original.questions || [])
    if (curQ !== origQ) {
      diff.questions = current.questions
      hasChanges = true
    }
  }

  if (!hasChanges) return null

  return {
    lesson_id: current.lesson_id,
    test_id: current.test_id,
    module_id: current.module_id,
    type: current.type,
    action: 'update',
    ...diff,
  }
}

export const getCourseStructureDiff = (
  currentStructure: any[],
  originalStructure: any[]
) => {
  const result: any[] = []

  currentStructure.forEach(currItem => {
    const origItem = originalStructure.find(
      o =>
        (currItem.module_id && o.module_id === currItem.module_id) ||
        (currItem.test_id && o.test_id === currItem.test_id)
    )

    if (currItem.type === 'module') {
      const moduleDiff = getElementDiff(currItem, origItem)
      const childChanges: any[] = []

      const currentChildren = currItem.moduleStructure || []
      const originalChildren = origItem?.moduleStructure || []

      currentChildren.forEach((currChild: any) => {
        const origChild = originalChildren.find(
          (o: any) =>
            (currChild.lesson_id && o.lesson_id === currChild.lesson_id) ||
            (currChild.test_id && o.test_id === currChild.test_id)
        )
        const childDiff = getElementDiff(currChild, origChild)
        if (childDiff) childChanges.push(childDiff)
      })

      originalChildren.forEach((origChild: any) => {
        const stillExists = currentChildren.find(
          (c: any) =>
            (origChild.lesson_id && c.lesson_id === origChild.lesson_id) ||
            (origChild.test_id && c.test_id === origChild.test_id)
        )
        if (!stillExists) {
          childChanges.push({
            lesson_id: origChild.lesson_id,
            test_id: origChild.test_id,
            type: origChild.type,
            action: 'delete',
          })
        }
      })

      if (moduleDiff || childChanges.length > 0) {
        result.push({
          ...(moduleDiff || {}),
          module_id: currItem.module_id,
          type: 'module',
          moduleStructure: childChanges,
          action: moduleDiff ? moduleDiff.action : 'update',
        })
      }
    } else {
      const testDiff = getElementDiff(currItem, origItem)
      if (testDiff) result.push(testDiff)
    }
  })

  originalStructure.forEach(origItem => {
    const stillExists = currentStructure.find(
      c =>
        (origItem.module_id && c.module_id === origItem.module_id) ||
        (origItem.test_id && c.test_id === origItem.test_id)
    )
    if (!stillExists) {
      result.push({
        module_id: origItem.module_id,
        test_id: origItem.test_id,
        type: origItem.type,
        action: 'delete',
      })
    }
  })

  return result
}
