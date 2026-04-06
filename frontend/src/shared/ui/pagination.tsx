import React from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { Button } from '@/shared/ui'

const DOTS = '...'

const range = (start: number, end: number): number[] => {
  const length = end - start + 1
  return Array.from({ length }, (_, idx) => idx + start)
}

interface UsePaginationProps {
  totalPages: number
  siblingCount?: number
  currentPage: number
}

const usePagination = ({
  totalPages,
  siblingCount = 1,
  currentPage,
}: UsePaginationProps): (number | typeof DOTS)[] => {
  return React.useMemo(() => {
    const totalPageNumbers = siblingCount + 5

    if (totalPageNumbers >= totalPages) {
      return range(1, totalPages)
    }

    const leftSiblingIndex = Math.max(currentPage - siblingCount, 1)
    const rightSiblingIndex = Math.min(currentPage + siblingCount, totalPages)

    const shouldShowLeftDots = leftSiblingIndex > 2
    const shouldShowRightDots = rightSiblingIndex < totalPages - 2

    const firstPageIndex = 1
    const lastPageIndex = totalPages

    if (!shouldShowLeftDots && shouldShowRightDots) {
      const leftItemCount = 3 + 2 * siblingCount
      const leftRange = range(1, leftItemCount)

      return [...leftRange, DOTS, totalPages]
    }

    if (shouldShowLeftDots && !shouldShowRightDots) {
      const rightItemCount = 3 + 2 * siblingCount
      const rightRange = range(totalPages - rightItemCount + 1, totalPages)

      return [firstPageIndex, DOTS, ...rightRange]
    }

    if (shouldShowLeftDots && shouldShowRightDots) {
      const middleRange = range(leftSiblingIndex, rightSiblingIndex)
      return [firstPageIndex, DOTS, ...middleRange, DOTS, lastPageIndex]
    }

    return []
  }, [totalPages, siblingCount, currentPage])
}

interface PaginationProps {
  page: number
  totalPages: number
  onPageChange: (page: number) => void
  siblingCount?: number
}

export const Pagination: React.FC<PaginationProps> = ({
  page,
  totalPages,
  onPageChange,
  siblingCount = 1,
}) => {
  const paginationRange = usePagination({
    currentPage: page,
    totalPages,
    siblingCount,
  })

  if (page === 0 || !paginationRange || paginationRange.length < 2) {
    return null
  }

  const onNext = () => {
    if (page < totalPages) {
      onPageChange(page + 1)
    }
  }

  const onPrevious = () => {
    if (page > 1) {
      onPageChange(page - 1)
    }
  }

  const lastPage = paginationRange[paginationRange.length - 1]

  return (
    <div className="flex items-center justify-center gap-2 mt-8">
      <Button
        variant="outline"
        size="icon"
        onClick={onPrevious}
        disabled={page === 1}
        className="w-10 h-10"
      >
        <ChevronLeft className="w-5 h-5" />
      </Button>

      {paginationRange.map((pageNumber, index) => {
        if (pageNumber === DOTS) {
          return (
            <div
              key={`dots-${index}`}
              className="w-10 h-10 flex items-center justify-center text-muted-foreground"
            >
              &#8230;
            </div>
          )
        }

        return (
          <Button
            key={pageNumber}
            variant={pageNumber === page ? 'secondary' : 'outline'}
            size="icon"
            onClick={() => onPageChange(pageNumber)}
            className="w-10 h-10"
          >
            {pageNumber}
          </Button>
        )
      })}

      <Button
        variant="outline"
        size="icon"
        onClick={onNext}
        disabled={page === lastPage}
        className="w-10 h-10"
      >
        <ChevronRight className="w-5 h-5" />
      </Button>
    </div>
  )
}
