import { Fragment } from 'react'
import type { HeatmapCell } from '../../api/types'
import { cn } from '../../lib/utils'

const HEAT_STYLES: Record<string, string> = {
  Red: 'bg-heat-red-bg border-heat-red/30 text-heat-red',
  Amber: 'bg-heat-amber-bg border-heat-amber/30 text-heat-amber',
  Green: 'bg-heat-green-bg border-heat-green/30 text-heat-green',
}

function band(score: number): 'Low' | 'Medium' | 'High' {
  if (score <= 33) return 'Low'
  if (score <= 66) return 'Medium'
  return 'High'
}

/** Impact (rows, high at top) x Readiness (columns, low at left) grid, each
 * cell listing the stakeholders that land there. Mirrors the classic
 * consulting stakeholder-management heat map. */
export function HeatmapGrid({ cells }: { cells: HeatmapCell[] }) {
  const impactBands: ('High' | 'Medium' | 'Low')[] = ['High', 'Medium', 'Low']
  const readinessBands: ('Low' | 'Medium' | 'High')[] = ['Low', 'Medium', 'High']

  const grouped = new Map<string, HeatmapCell[]>()
  for (const cell of cells) {
    const key = `${band(cell.impact_score)}|${band(cell.readiness_score)}`
    grouped.set(key, [...(grouped.get(key) ?? []), cell])
  }

  return (
    <div className="inline-grid grid-cols-[80px_repeat(3,1fr)] gap-2">
      <div />
      {readinessBands.map((b) => (
        <div key={b} className="px-2 text-center text-xs font-medium text-slate-500">
          {b} Readiness
        </div>
      ))}
      {impactBands.map((impactBand) => (
        <Fragment key={impactBand}>
          <div className="flex items-center justify-end pr-2 text-xs font-medium text-slate-500">
            {impactBand} Impact
          </div>
          {readinessBands.map((readinessBand) => {
            const key = `${impactBand}|${readinessBand}`
            const cellItems = grouped.get(key) ?? []
            const rating = cellItems[0]?.heat_rating
            return (
              <div
                key={key}
                className={cn(
                  'min-h-[92px] min-w-[150px] rounded-lg border p-2',
                  rating ? HEAT_STYLES[rating] : 'border-navy-900/8 bg-navy-900/[0.02] text-slate-400',
                )}
              >
                {cellItems.length === 0 ? (
                  <span className="text-xs">—</span>
                ) : (
                  <ul className="space-y-1">
                    {cellItems.map((c) => (
                      <li key={c.stakeholder_id} className="rounded bg-white/70 px-2 py-1 text-xs font-medium">
                        {c.stakeholder}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )
          })}
        </Fragment>
      ))}
    </div>
  )
}
