import { AlertTriangle, ArrowRight, FileText, Gauge, Layers, Plus } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { projectsApi } from '../api/projects'
import type { ProjectDashboard } from '../api/types'
import { EmptyState } from '../components/common/EmptyState'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { StatCard } from '../components/common/StatCard'
import { Button } from '../components/ui/Button'
import { Card, CardBody } from '../components/ui/Card'
import { cn, formatDate } from '../lib/utils'

const DOMINANT_STYLES: Record<'Red' | 'Amber' | 'Green' | 'None', string> = {
  Red: 'before:bg-heat-red',
  Amber: 'before:bg-heat-amber',
  Green: 'before:bg-heat-green',
  None: 'before:bg-navy-900/10',
}

function dominantHeat(d: ProjectDashboard): 'Red' | 'Amber' | 'Green' | 'None' {
  if (d.red_count > 0) return 'Red'
  if (d.amber_count > 0) return 'Amber'
  if (d.green_count > 0) return 'Green'
  return 'None'
}

export function PortfolioDashboardPage() {
  const [items, setItems] = useState<ProjectDashboard[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    projectsApi
      .portfolio()
      .then(setItems)
      .catch((e) => setError(e.message))
  }, [])

  const scored = items?.filter((d) => d.readiness_score !== null) ?? []
  const avgReadiness = scored.length
    ? Math.round(scored.reduce((sum, d) => sum + (d.readiness_score ?? 0), 0) / scored.length)
    : null
  const totalRed = items?.reduce((sum, d) => sum + d.red_count, 0) ?? 0
  const totalOpenRaid = items?.reduce((sum, d) => sum + d.open_raid_count, 0) ?? 0

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-navy-900">Change Portfolio</h1>
        <p className="mt-1 text-sm text-slate-500">
          Every change initiative at a glance, readiness, stakeholder risk, and heat map status.
        </p>
      </div>

      {error && <p className="text-sm text-heat-red">{error}</p>}
      {!items && !error && <LoadingSpinner label="Loading portfolio…" />}

      {items && items.length > 0 && (
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <StatCard label="Active Initiatives" value={items.length} icon={<Layers size={18} />} />
          <StatCard
            label="Avg. Readiness"
            value={avgReadiness !== null ? `${avgReadiness}/100` : '—'}
            icon={<Gauge size={18} />}
          />
          <StatCard
            label="Stakeholders at Risk"
            value={totalRed}
            hint="Rated Red across portfolio"
            icon={<AlertTriangle size={18} className="text-heat-red" />}
          />
          <StatCard label="Open RAID Items" value={totalOpenRaid} icon={<FileText size={18} />} />
        </div>
      )}

      {items && items.length === 0 && (
        <EmptyState
          title="No change initiatives yet"
          description="Create your first change initiative to start a stakeholder impact assessment."
          action={
            <Link to="/projects/new">
              <Button>
                <Plus size={16} /> Create Initiative
              </Button>
            </Link>
          }
        />
      )}

      {items && items.length > 0 && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {items.map((d) => (
            <Link key={d.project.id} to={`/projects/${d.project.id}`} className="group">
              <Card
                className={cn(
                  "relative h-full overflow-hidden pl-1 transition-all before:absolute before:inset-y-0 before:left-0 before:w-1 before:content-['']",
                  'group-hover:-translate-y-0.5 group-hover:shadow-lg group-hover:shadow-navy-900/5',
                  DOMINANT_STYLES[dominantHeat(d)],
                )}
              >
                <CardBody className="space-y-3.5">
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <p className="truncate font-semibold text-navy-900 group-hover:text-brand">{d.project.name}</p>
                      <p className="mt-0.5 text-xs text-slate-500">
                        {d.project.change_type} initiative · {formatDate(d.project.created_at)}
                      </p>
                    </div>
                    {d.readiness_score !== null && (
                      <div className="flex shrink-0 flex-col items-center rounded-lg bg-navy-900/[0.03] px-2.5 py-1.5">
                        <span className="text-sm font-bold leading-none text-navy-900">{d.readiness_score}</span>
                        <span className="mt-0.5 text-[10px] font-medium uppercase tracking-wide text-slate-400">
                          / 100
                        </span>
                      </div>
                    )}
                  </div>

                  <p className="line-clamp-2 text-sm text-slate-500">{d.project.description || 'No description provided.'}</p>

                  <div className="flex flex-wrap gap-1.5">
                    {d.stakeholder_count === 0 ? (
                      <span className="text-xs text-slate-400">No impact analysis yet</span>
                    ) : (
                      <>
                        {d.red_count > 0 && (
                          <span className="rounded-full bg-heat-red-bg px-2 py-0.5 text-xs font-medium text-heat-red">
                            {d.red_count} Red
                          </span>
                        )}
                        {d.amber_count > 0 && (
                          <span className="rounded-full bg-heat-amber-bg px-2 py-0.5 text-xs font-medium text-heat-amber">
                            {d.amber_count} Amber
                          </span>
                        )}
                        {d.green_count > 0 && (
                          <span className="rounded-full bg-heat-green-bg px-2 py-0.5 text-xs font-medium text-heat-green">
                            {d.green_count} Green
                          </span>
                        )}
                      </>
                    )}
                  </div>

                  <div className="flex items-center justify-between border-t border-navy-900/8 pt-3 text-xs text-slate-500">
                    <span className="flex items-center gap-3">
                      <span>{d.document_count} docs</span>
                      <span>{d.open_raid_count} open RAID</span>
                    </span>
                    <span className="flex items-center gap-1 font-medium text-brand opacity-0 transition-opacity group-hover:opacity-100">
                      Open <ArrowRight size={12} />
                    </span>
                  </div>
                </CardBody>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
