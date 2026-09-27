import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { heatmapApi } from '../api/heatmap'
import type { HeatmapCell } from '../api/types'
import { EmptyState } from '../components/common/EmptyState'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { HeatmapGrid } from '../components/heatmap/HeatmapGrid'
import { HeatBadge } from '../components/ui/Badge'
import { Card, CardBody, CardHeader, CardTitle } from '../components/ui/Card'
import { Table, Td, Th, Thead, Tr } from '../components/ui/Table'
import { useProjectContext } from '../lib/ProjectContext'

export function HeatmapPage() {
  const { project } = useProjectContext()
  const [cells, setCells] = useState<HeatmapCell[] | null>(null)

  useEffect(() => {
    heatmapApi.get(project.id).then(setCells)
  }, [project.id])

  if (!cells) return <LoadingSpinner />

  if (cells.length === 0) {
    return (
      <EmptyState
        title="No heat map yet"
        description="Run the impact analysis first to generate ADKAR-scored stakeholder data."
        action={
          <Link to={`/projects/${project.id}/impact`} className="text-sm text-brand hover:underline">
            Go to Impact Assessment →
          </Link>
        }
      />
    )
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Stakeholder Impact vs. Readiness Heat Map</CardTitle>
        </CardHeader>
        <CardBody>
          <HeatmapGrid cells={cells} />
        </CardBody>
      </Card>

      <Card>
        <Table>
          <Thead>
            <Tr>
              <Th>Stakeholder</Th>
              <Th>Impact Score</Th>
              <Th>Readiness Score</Th>
              <Th>Barrier</Th>
              <Th>Rating</Th>
            </Tr>
          </Thead>
          <tbody>
            {cells.map((c) => (
              <Tr key={c.stakeholder_id}>
                <Td className="font-medium">{c.stakeholder}</Td>
                <Td>{c.impact_score.toFixed(0)}</Td>
                <Td>{c.readiness_score.toFixed(0)}</Td>
                <Td>{c.barrier_dimension || '—'}</Td>
                <Td>
                  <HeatBadge rating={c.heat_rating} />
                </Td>
              </Tr>
            ))}
          </tbody>
        </Table>
      </Card>
    </div>
  )
}
