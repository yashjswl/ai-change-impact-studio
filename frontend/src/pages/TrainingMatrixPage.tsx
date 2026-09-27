import { useEffect, useState } from 'react'
import { trainingApi } from '../api/training'
import type { TrainingItem } from '../api/types'
import { EmptyState } from '../components/common/EmptyState'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { Table, Td, Th, Thead, Tr } from '../components/ui/Table'
import { useProjectContext } from '../lib/ProjectContext'

const PRIORITY_TONE: Record<string, 'red' | 'amber' | 'green'> = { High: 'red', Medium: 'amber', Low: 'green' }

export function TrainingMatrixPage() {
  const { project } = useProjectContext()
  const [items, setItems] = useState<TrainingItem[] | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  function load() {
    trainingApi.list(project.id).then(setItems)
  }
  useEffect(load, [project.id])

  async function handleGenerate() {
    setBusy(true)
    setError(null)
    try {
      setItems(await trainingApi.generate(project.id))
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Generation failed')
    } finally {
      setBusy(false)
    }
  }

  if (!items) return <LoadingSpinner />

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-500">Capability gaps by role and the training actions to close them.</p>
        <Button size="sm" disabled={busy} onClick={handleGenerate}>
          {busy ? 'Generating…' : items.length ? 'Regenerate' : 'Generate Training Matrix'}
        </Button>
      </div>
      {error && <p className="text-sm text-heat-red">{error}</p>}

      {items.length === 0 ? (
        <EmptyState title="No training matrix yet" description="Run the impact analysis first, then generate a training needs matrix." />
      ) : (
        <Card>
          <Table>
            <Thead>
              <Tr>
                <Th>Role</Th>
                <Th>Current Capability</Th>
                <Th>Required Capability</Th>
                <Th>Gap</Th>
                <Th>Training Action</Th>
                <Th>Owner</Th>
                <Th>Due</Th>
                <Th>Priority</Th>
              </Tr>
            </Thead>
            <tbody>
              {items.map((item) => (
                <Tr key={item.id}>
                  <Td className="font-medium">{item.role}</Td>
                  <Td className="max-w-[160px]">{item.current_capability}</Td>
                  <Td className="max-w-[160px]">{item.required_capability}</Td>
                  <Td className="max-w-[160px]">{item.gap}</Td>
                  <Td className="max-w-[200px]">{item.training_action}</Td>
                  <Td>{item.owner}</Td>
                  <Td>{item.due_date || '-'}</Td>
                  <Td>
                    <Badge tone={PRIORITY_TONE[item.priority] ?? 'neutral'}>{item.priority}</Badge>
                  </Td>
                </Tr>
              ))}
            </tbody>
          </Table>
        </Card>
      )}
    </div>
  )
}
