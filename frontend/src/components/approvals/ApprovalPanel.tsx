import { useState } from 'react'
import { approvalsApi } from '../../api/approvals'
import type { Approval } from '../../api/types'
import { Badge } from '../ui/Badge'
import { Button } from '../ui/Button'
import { Card, CardBody } from '../ui/Card'

const STATUS_TONE: Record<string, 'green' | 'red' | 'neutral'> = {
  approved: 'green',
  rejected: 'red',
  pending: 'neutral',
}

export function ApprovalPanel({
  projectId,
  artifactType,
  artifactId,
  latest,
  onDecision,
}: {
  projectId: number
  artifactType: string
  artifactId: number
  latest?: Approval
  onDecision?: (approval: Approval) => void
}) {
  const [reviewer, setReviewer] = useState('')
  const [comments, setComments] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function decide(status: 'approved' | 'rejected') {
    if (!reviewer.trim()) {
      setError('Enter a reviewer name first.')
      return
    }
    setBusy(true)
    setError(null)
    try {
      const approval = await approvalsApi.create(projectId, {
        artifact_type: artifactType,
        artifact_id: artifactId,
        reviewer_name: reviewer,
        status,
        comments,
      })
      onDecision?.(approval)
      setComments('')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to submit decision')
    } finally {
      setBusy(false)
    }
  }

  return (
    <Card>
      <CardBody className="space-y-3">
        <div className="flex items-center justify-between">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Human review</p>
          {latest && (
            <Badge tone={STATUS_TONE[latest.status] ?? 'neutral'}>
              {latest.status} by {latest.reviewer_name}
            </Badge>
          )}
        </div>
        {latest?.comments && <p className="text-xs text-slate-500">"{latest.comments}"</p>}
        <div className="flex flex-wrap items-center gap-2">
          <input
            className="w-40 rounded-md border border-navy-900/15 px-2.5 py-1.5 text-sm"
            placeholder="Reviewer name"
            value={reviewer}
            onChange={(e) => setReviewer(e.target.value)}
          />
          <input
            className="min-w-[180px] flex-1 rounded-md border border-navy-900/15 px-2.5 py-1.5 text-sm"
            placeholder="Comments (optional)"
            value={comments}
            onChange={(e) => setComments(e.target.value)}
          />
          <Button size="sm" variant="primary" disabled={busy} onClick={() => decide('approved')}>
            Approve
          </Button>
          <Button size="sm" variant="danger" disabled={busy} onClick={() => decide('rejected')}>
            Reject
          </Button>
        </div>
        {error && <p className="text-xs text-heat-red">{error}</p>}
      </CardBody>
    </Card>
  )
}
