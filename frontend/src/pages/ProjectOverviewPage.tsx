import { AlertTriangle, FileText, Gauge, Users } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { projectsApi } from '../api/projects'
import type { ProjectDashboard } from '../api/types'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { StatCard } from '../components/common/StatCard'
import { Card, CardBody, CardHeader, CardTitle } from '../components/ui/Card'
import { useProjectContext } from '../lib/ProjectContext'

export function ProjectOverviewPage() {
  const { project } = useProjectContext()
  const [dashboard, setDashboard] = useState<ProjectDashboard | null>(null)

  useEffect(() => {
    projectsApi.dashboard(project.id).then(setDashboard)
  }, [project.id])

  if (!dashboard) return <LoadingSpinner />

  return (
    <div className="space-y-6">
      <p className="text-sm text-slate-500">{project.description || 'No description provided.'}</p>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <StatCard
          label="Readiness Score"
          value={dashboard.readiness_score !== null ? `${dashboard.readiness_score}/100` : '—'}
          icon={<Gauge size={20} />}
        />
        <StatCard label="Stakeholders" value={dashboard.stakeholder_count} icon={<Users size={20} />} />
        <StatCard
          label="Heat Map"
          value={`${dashboard.red_count}R / ${dashboard.amber_count}A / ${dashboard.green_count}G`}
        />
        <StatCard label="Open RAID Items" value={dashboard.open_raid_count} icon={<AlertTriangle size={20} />} />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Top Risks</CardTitle>
          </CardHeader>
          <CardBody>
            {dashboard.top_risks.length === 0 ? (
              <p className="text-sm text-slate-400">No high/critical risks logged yet.</p>
            ) : (
              <ul className="space-y-2 text-sm text-navy-900/90">
                {dashboard.top_risks.map((r, i) => (
                  <li key={i} className="flex gap-2">
                    <span className="text-heat-red">●</span> {r}
                  </li>
                ))}
              </ul>
            )}
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Get Started</CardTitle>
          </CardHeader>
          <CardBody className="space-y-2 text-sm">
            <p className="flex items-center gap-2 text-slate-500">
              <FileText size={14} /> {dashboard.document_count} documents loaded
            </p>
            {dashboard.document_count === 0 && (
              <Link to={`/projects/${project.id}/documents`} className="text-brand hover:underline">
                Upload or load sample documents →
              </Link>
            )}
            {dashboard.stakeholder_count === 0 && (
              <Link to={`/projects/${project.id}/impact`} className="block text-brand hover:underline">
                Run the change impact analysis →
              </Link>
            )}
            {dashboard.stakeholder_count > 0 && (
              <Link to={`/projects/${project.id}/heatmap`} className="block text-brand hover:underline">
                View the stakeholder heat map →
              </Link>
            )}
          </CardBody>
        </Card>
      </div>
    </div>
  )
}
