import { ChevronDown, ChevronUp } from 'lucide-react'
import { Label } from '@/shared/ui'
import { useI18n } from '@/shared/lib'
import { useCallback, useEffect, useRef } from 'react'
import { cn } from '@/shared/lib/utils' // твоє утилітарне cn

interface Duration {
  days: number
  hours: number
  minutes: number
}

interface CourseDurationPickerProps {
  value: Duration
  onChange: (val: Duration) => void
  maxDays: number
  inputtedText?: string
}

const StepperInput = ({
  label,
  val,
  min,
  max,
  onChange,
}: {
  label: string
  val: number
  min: number
  max: number
  onChange: (newVal: number) => void
}) => {
  const intervalRef = useRef<number | null>(null)
  const currentRef = useRef<number>(val)

  useEffect(() => {
    currentRef.current = val
  }, [val])

  const inc = useCallback(() => {
    const next = Math.min(max, currentRef.current + 1)
    onChange(next)
    currentRef.current = next
  }, [max, onChange])

  const dec = useCallback(() => {
    const next = Math.max(min, currentRef.current - 1)
    onChange(next)
    currentRef.current = next
  }, [min, onChange])

  const startHold = useCallback((action: () => void) => {
    if (intervalRef.current != null) return
    action()
    intervalRef.current = window.setInterval(action, 150)
  }, [])

  const stopHold = useCallback(() => {
    if (intervalRef.current != null) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
  }, [])

  useEffect(() => {
    window.addEventListener('pointerup', stopHold)
    window.addEventListener('pointercancel', stopHold)
    window.addEventListener('touchend', stopHold)
    return () => {
      window.removeEventListener('pointerup', stopHold)
      window.removeEventListener('pointercancel', stopHold)
      window.removeEventListener('touchend', stopHold)
    }
  }, [stopHold])

  return (
    <div className="flex flex-col items-center select-none">
      <button
        type="button"
        onPointerDown={e => {
          e.preventDefault()
          startHold(inc)
        }}
        onPointerUp={stopHold}
        onPointerCancel={stopHold}
        className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
      >
        <ChevronUp className="w-4 h-4" />
      </button>

      <input
        type="number"
        value={val}
        min={min}
        max={max}
        onChange={e => {
          let newVal = Number(e.target.value)
          if (isNaN(newVal)) newVal = min
          newVal = Math.max(min, Math.min(max, newVal))
          onChange(newVal)
          currentRef.current = newVal
        }}
        onKeyDown={e => {
          if (e.key === 'ArrowUp') {
            e.preventDefault()
            inc()
          } else if (e.key === 'ArrowDown') {
            e.preventDefault()
            dec()
          }
        }}
        className={cn(
          'flex h-10 w-16 text-center rounded-md border border-input bg-background px-3 py-2 text-base text-gray-900 dark:text-gray-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 appearance-none [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none [-moz-appearance:textfield]'
        )}
      />

      <button
        type="button"
        onPointerDown={e => {
          e.preventDefault()
          startHold(dec)
        }}
        onPointerUp={stopHold}
        onPointerCancel={stopHold}
        className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
      >
        <ChevronDown className="w-4 h-4" />
      </button>

      <span className="text-sm text-gray-700 dark:text-gray-300">{label}</span>
    </div>
  )
}

const CourseDurationPicker = ({
  value,
  onChange,
  maxDays,
  inputtedText,
}: CourseDurationPickerProps) => {
  const { t } = useI18n()

  return (
    <div className="space-y-2">
      <div className="items-center grid grid-cols-1 md:grid-cols-2">
        <Label className="text-gray-800 dark:text-gray-200 flex-shrink-0 flex justify-end px-6">
          {inputtedText
            ? inputtedText
            : t(
                'Встановіть орієнтовний час необхідний для проходження всього курсу *'
              )}
        </Label>
        <div className="flex gap-6">
          <StepperInput
            label={t('дн.')}
            val={value.days}
            min={0}
            max={maxDays}
            onChange={v => onChange({ ...value, days: v })}
          />
          <StepperInput
            label={t('год.')}
            val={value.hours}
            min={0}
            max={23}
            onChange={v => onChange({ ...value, hours: v })}
          />
          <StepperInput
            label={t('хв.')}
            val={value.minutes}
            min={0}
            max={59}
            onChange={v => onChange({ ...value, minutes: v })}
          />
        </div>
      </div>
    </div>
  )
}

export default CourseDurationPicker
