import { useEffect, useState } from 'react'
import { raciApi } from '../api/raci'
import type { RaciItem } from '../api/types'
import { EmptyState } from '../components/common/EmptyState'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { Table, Td, Th, Thead, Tr } from '../components/ui/Table'
import { useProjectContext } from '../lib/ProjectContext'

const FIELDS: (keyof RaciItem)[] = ['workstream', 'activity', 'responsible', 'accountable', 'consulted', 'informed']

export function RaciPage() {
  const { project } = useProjectContext()
  const [items, setItems] = useState<RaciItem[] | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  function load() {
    raciApi.list(project.id).then(setItems)
  }
  useEffect(load, [project.id])

  async function handleGenerate() {
    setBusy(true)
    setError(null)
    try {
      const result = await raciApi.generate(project.id)
      setItems(result)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Generation failed')
    } finally {
      setBusy(false)
    }
  }

  async function handleFieldChange(item: RaciItem, field: keyof RaciItem, value: string) {
    const updated = await raciApi.update(item.id, { [field]: value })
    setItems((prev) => prev?.map((i) => (i.id === updated.id ? updated : i)) ?? null)
  }

  async function handleDelete(id: number) {
    await raciApi.remove(id)
    setItems((prev) => prev?.filter((i) => i.id !== id) ?? null)
  }

  if (!items) return <LoadingSpinner />

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-500">
          Who's Responsible, Accountable, Consulted, and Informed for delivering this change.
        </p>
        <Button size="sm" disabled={busy} onClick={handleGenerate}>
          {busy ? 'Generating…' : items.length ? 'Regenerate' : 'Generate RACI Matrix'}
        </Button>
      </div>
      {error && <p className="text-sm text-heat-red">{error}</p>}

      {items.length === 0 ? (
        <EmptyState title="No RACI matrix yet" description="Run the impact analysis first, then generate a RACI matrix." />
      ) : (
        <Card>
          <Table>
            <Thead>
              <Tr>
                <Th>Workstream</Th>
                <Th>Activity</Th>
                <Th>Responsible</Th>
                <Th>Accountable</Th>
                <Th>Consulted</Th>
                <Th>Informed</Th>
                <Th />
              </Tr>
            </Thead>
            <tbody>
              {items.map((item) => (
                <Tr key={item.id}>
                  {FIELDS.map((field) => (
                    <Td key={field}>
                      <input
                        className="w-full min-w-[100px] rounded border border-transparent bg-transparent px-1 py-0.5 text-sm hover:border-navy-900/15 focus:border-brand focus:outline-none"
                        defaultValue={item[field] as string}
                        onBlur={(e) => e.target.value !== item[field] && handleFieldChange(item, field, e.target.value)}
                      />
                    </Td>
                  ))}
                  <Td>
                    <button onClick={() => handleDelete(item.id)} className="text-xs text-slate-400 hover:text-heat-red">
                      Remove
                    </button>
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
