import { useEffect, useState } from 'react'
import { commsApi } from '../api/comms'
import type { ChecklistItem, CommsPlanItem, CommunicationPackage } from '../api/types'
import { ApprovalPanel } from '../components/approvals/ApprovalPanel'
import { EmptyState } from '../components/common/EmptyState'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { ExportButton } from '../components/export/ExportButtons'
import { Button } from '../components/ui/Button'
import { Card, CardBody, CardHeader, CardTitle } from '../components/ui/Card'
import { Table, Td, Th, Thead, Tr } from '../components/ui/Table'
import { useProjectContext } from '../lib/ProjectContext'

function ChecklistTable({ title, items, onToggle }: { title: string; items: ChecklistItem[]; onToggle: (item: ChecklistItem) => void }) {
  return (
    <div>
      <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">{title}</p>
      <Table>
        <Thead>
          <Tr>
            <Th>Done</Th>
            <Th>Item</Th>
            <Th>Owner</Th>
            <Th>Due</Th>
          </Tr>
        </Thead>
        <tbody>
          {items.map((it) => (
            <Tr key={it.id}>
              <Td>
                <input type="checkbox" checked={it.is_done} onChange={() => onToggle(it)} />
              </Td>
              <Td>{it.item}</Td>
              <Td>{it.owner}</Td>
              <Td>{it.due || '-'}</Td>
            </Tr>
          ))}
        </tbody>
      </Table>
    </div>
  )
}

export function CommsPlanPage() {
  const { project } = useProjectContext()
  const [plan, setPlan] = useState<CommsPlanItem[] | null>(null)
  const [pkg, setPkg] = useState<CommunicationPackage | null>(null)
  const [checklists, setChecklists] = useState<ChecklistItem[] | null>(null)
  const [busyPlan, setBusyPlan] = useState(false)
  const [busyPkg, setBusyPkg] = useState(false)
  const [error, setError] = useState<string | null>(null)

  function loadAll() {
    commsApi.listPlan(project.id).then(setPlan)
    commsApi
      .getPackage(project.id)
      .then(setPkg)
      .catch(() => setPkg(null))
    commsApi.listChecklist(project.id).then(setChecklists)
  }
  useEffect(loadAll, [project.id])

  async function handleGeneratePlan() {
    setBusyPlan(true)
    setError(null)
    try {
      setPlan(await commsApi.generatePlan(project.id))
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Generation failed')
    } finally {
      setBusyPlan(false)
    }
  }

  async function handleGeneratePackage() {
    setBusyPkg(true)
    setError(null)
    try {
      setPkg(await commsApi.generatePackage(project.id))
      commsApi.listChecklist(project.id).then(setChecklists)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Generation failed')
    } finally {
      setBusyPkg(false)
    }
  }

  async function toggleChecklistItem(item: ChecklistItem) {
    const updated = await commsApi.updateChecklistItem(item.id, { is_done: !item.is_done })
    setChecklists((prev) => prev?.map((i) => (i.id === updated.id ? updated : i)) ?? null)
  }

  if (!plan || !checklists) return <LoadingSpinner />

  return (
    <div className="space-y-6">
      {error && <p className="text-sm text-heat-red">{error}</p>}

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Communication Plan</CardTitle>
          <Button size="sm" disabled={busyPlan} onClick={handleGeneratePlan}>
            {busyPlan ? 'Generating…' : plan.length ? 'Regenerate' : 'Generate Plan'}
          </Button>
        </CardHeader>
        {plan.length === 0 ? (
          <CardBody>
            <EmptyState title="No communication plan yet" description="Run the impact analysis first, then generate a plan." />
          </CardBody>
        ) : (
          <Table>
            <Thead>
              <Tr>
                <Th>Audience</Th>
                <Th>Key Message</Th>
                <Th>Channel</Th>
                <Th>Owner</Th>
                <Th>Timing</Th>
              </Tr>
            </Thead>
            <tbody>
              {plan.map((item) => (
                <Tr key={item.id}>
                  <Td className="font-medium">{item.audience}</Td>
                  <Td className="max-w-sm">{item.key_message}</Td>
                  <Td>{item.channel}</Td>
                  <Td>{item.owner}</Td>
                  <Td>{item.timing}</Td>
                </Tr>
              ))}
            </tbody>
          </Table>
        )}
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Narrative Communications &amp; Checklists</CardTitle>
          <Button size="sm" disabled={busyPkg} onClick={handleGeneratePackage}>
            {busyPkg ? 'Generating…' : pkg ? 'Regenerate' : 'Generate Package'}
          </Button>
        </CardHeader>
        <CardBody className="space-y-6">
          {!pkg && (
            <EmptyState title="No communication package yet" description="Run the impact analysis first, then generate the package." />
          )}
          {pkg && (
            <>
              <div>
                <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">Employee Announcement</p>
                <p className="font-medium text-navy-900">{pkg.employee_subject}</p>
                <p className="mt-1 whitespace-pre-line text-sm text-navy-900/80">{pkg.employee_body}</p>
              </div>
              <div>
                <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">Manager Communication</p>
                <p className="font-medium text-navy-900">{pkg.manager_subject}</p>
                <p className="mt-1 whitespace-pre-line text-sm text-navy-900/80">{pkg.manager_body}</p>
                <ul className="mt-2 list-inside list-disc text-sm text-navy-900/80">
                  {pkg.manager_talking_points.map((t, i) => (
                    <li key={i}>{t}</li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">FAQ</p>
                <div className="space-y-2">
                  {pkg.faq.map((f, i) => (
                    <div key={i} className="text-sm">
                      <p className="font-medium text-navy-900">Q: {f.question}</p>
                      <p className="text-navy-900/80">A: {f.answer}</p>
                    </div>
                  ))}
                </div>
              </div>
              <div className="rounded-lg bg-navy-900/[0.03] p-4">
                <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">Change Readiness Summary</p>
                <p className="text-2xl font-semibold text-navy-900">{pkg.readiness_score}/100</p>
                <p className="mt-1 text-sm text-navy-900/80">{pkg.readiness_rationale}</p>
              </div>
              <ChecklistTable
                title="Training Checklist"
                items={checklists.filter((c) => c.checklist_type === 'training')}
                onToggle={toggleChecklistItem}
              />
              <ChecklistTable
                title="Implementation Checklist"
                items={checklists.filter((c) => c.checklist_type === 'implementation')}
                onToggle={toggleChecklistItem}
              />
              <ApprovalPanel projectId={project.id} artifactType="communication_package" artifactId={pkg.id} />
              <div className="flex flex-wrap gap-2 border-t border-navy-900/8 pt-4">
                <ExportButton projectId={project.id} kind="impact-onepager" />
                <ExportButton projectId={project.id} kind="comms-package" />
                <ExportButton projectId={project.id} kind="executive-summary" />
              </div>
            </>
          )}
        </CardBody>
      </Card>
    </div>
  )
}
