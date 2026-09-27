import { useEffect, useState } from 'react'
import { raidApi } from '../api/raid'
import type { RaidItem } from '../api/types'
import { EmptyState } from '../components/common/EmptyState'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { SeverityBadge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { Table, Td, Th, Thead, Tr } from '../components/ui/Table'
import { useProjectContext } from '../lib/ProjectContext'

const STATUS_OPTIONS = ['Open', 'Mitigating', 'Monitoring', 'Closed']

export function RaidPage() {
  const { project } = useProjectContext()
  const [items, setItems] = useState<RaidItem[] | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  function load() {
    raidApi.list(project.id).then(setItems)
  }
  useEffect(load, [project.id])

  async function handleGenerate() {
    setBusy(true)
    setError(null)
    try {
      const result = await raidApi.generate(project.id)
      setItems(result)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Generation failed')
    } finally {
      setBusy(false)
    }
  }

  async function handleStatusChange(item: RaidItem, status: RaidItem['status']) {
    const updated = await raidApi.update(item.id, { status })
    setItems((prev) => prev?.map((i) => (i.id === updated.id ? updated : i)) ?? null)
  }

  if (!items) return <LoadingSpinner />

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-500">Risks, Assumptions, Issues, and Dependencies for this change.</p>
        <Button size="sm" disabled={busy} onClick={handleGenerate}>
          {busy ? 'Generating…' : items.length ? 'Regenerate' : 'Generate RAID Log'}
        </Button>
      </div>
      {error && <p className="text-sm text-heat-red">{error}</p>}

      {items.length === 0 ? (
        <EmptyState title="No RAID log yet" description="Run the impact analysis first, then generate a RAID log." />
      ) : (
        <Card>
          <Table>
            <Thead>
              <Tr>
                <Th>Category</Th>
                <Th>Description</Th>
                <Th>Severity</Th>
                <Th>Likelihood</Th>
                <Th>Owner</Th>
                <Th>Mitigation</Th>
                <Th>Status</Th>
              </Tr>
            </Thead>
            <tbody>
              {items.map((item) => (
                <Tr key={item.id}>
                  <Td>{item.category}</Td>
                  <Td className="max-w-xs">{item.description}</Td>
                  <Td>
                    <SeverityBadge severity={item.severity} />
                  </Td>
                  <Td>{item.likelihood}</Td>
                  <Td>{item.owner}</Td>
                  <Td className="max-w-xs">{item.mitigation}</Td>
                  <Td>
                    <select
                      className="rounded border border-navy-900/15 px-1.5 py-1 text-xs"
                      value={item.status}
                      onChange={(e) => handleStatusChange(item, e.target.value as RaidItem['status'])}
                    >
                      {STATUS_OPTIONS.map((s) => (
                        <option key={s} value={s}>
                          {s}
                        </option>
                      ))}
                    </select>
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
