import { useEffect, useState } from 'react'
import { auditApi } from '../api/audit'
import type { AuditLogEntry } from '../api/types'
import { EmptyState } from '../components/common/EmptyState'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { Badge } from '../components/ui/Badge'
import { Card } from '../components/ui/Card'
import { Table, Td, Th, Thead, Tr } from '../components/ui/Table'
import { useProjectContext } from '../lib/ProjectContext'

const ACTION_TONE: Record<string, 'green' | 'red' | 'brand' | 'neutral'> = {
  approved: 'green',
  rejected: 'red',
  generated: 'brand',
  created: 'brand',
  updated: 'neutral',
  deleted: 'red',
  exported: 'brand',
}

export function AuditPage() {
  const { project } = useProjectContext()
  const [entries, setEntries] = useState<AuditLogEntry[] | null>(null)

  useEffect(() => {
    auditApi.list(project.id).then(setEntries)
  }, [project.id])

  if (!entries) return <LoadingSpinner />
  if (entries.length === 0) return <EmptyState title="No activity yet" description="Actions taken on this initiative will appear here." />

  return (
    <Card>
      <Table>
        <Thead>
          <Tr>
            <Th>When</Th>
            <Th>Action</Th>
            <Th>Entity</Th>
            <Th>Actor</Th>
            <Th>Detail</Th>
          </Tr>
        </Thead>
        <tbody>
          {entries.map((e) => (
            <Tr key={e.id}>
              <Td className="whitespace-nowrap text-xs text-slate-500">{new Date(e.created_at).toLocaleString()}</Td>
              <Td>
                <Badge tone={ACTION_TONE[e.action] ?? 'neutral'}>{e.action}</Badge>
              </Td>
              <Td>{e.entity_type}</Td>
              <Td>{e.actor}</Td>
              <Td className="max-w-xs truncate text-xs text-slate-500">
                {Object.keys(e.detail).length > 0 ? JSON.stringify(e.detail) : '-'}
              </Td>
            </Tr>
          ))}
        </tbody>
      </Table>
    </Card>
  )
}
