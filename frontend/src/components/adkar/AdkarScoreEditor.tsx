import { cn } from '../../lib/utils'

const DIMENSIONS: { key: 'adkar_awareness' | 'adkar_desire' | 'adkar_knowledge' | 'adkar_ability' | 'adkar_reinforcement'; label: string }[] = [
  { key: 'adkar_awareness', label: 'Awareness' },
  { key: 'adkar_desire', label: 'Desire' },
  { key: 'adkar_knowledge', label: 'Knowledge' },
  { key: 'adkar_ability', label: 'Ability' },
  { key: 'adkar_reinforcement', label: 'Reinforcement' },
]

interface AdkarValues {
  adkar_awareness: number
  adkar_desire: number
  adkar_knowledge: number
  adkar_ability: number
  adkar_reinforcement: number
}

export function AdkarScoreEditor({
  values,
  onChange,
  disabled,
}: {
  values: AdkarValues
  onChange: (key: keyof AdkarValues, value: number) => void
  disabled?: boolean
}) {
  return (
    <div className="grid grid-cols-5 gap-3">
      {DIMENSIONS.map((d) => {
        const value = values[d.key]
        return (
          <div key={d.key} className="flex flex-col items-center gap-1">
            <span className="text-[11px] font-medium text-slate-500">{d.label}</span>
            <div className="flex gap-0.5">
              {[1, 2, 3, 4, 5].map((n) => (
                <button
                  key={n}
                  type="button"
                  disabled={disabled}
                  onClick={() => onChange(d.key, n)}
                  className={cn(
                    'h-5 w-3.5 rounded-sm transition-colors',
                    n <= value ? (value <= 3 ? 'bg-heat-amber' : 'bg-heat-green') : 'bg-navy-900/10',
                    !disabled && 'hover:opacity-80',
                  )}
                  aria-label={`${d.label} ${n}`}
                />
              ))}
            </div>
            <span className="text-xs font-semibold text-navy-900">{value}/5</span>
          </div>
        )
      })}
    </div>
  )
}
