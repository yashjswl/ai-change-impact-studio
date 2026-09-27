import { useEffect, useState } from 'react'
import { impactApi } from '../api/impact'
import type { ChangeImpactAnalysis, StakeholderImpact } from '../api/types'
import { AdkarScoreEditor } from '../components/adkar/AdkarScoreEditor'
import { BarrierBadge } from '../components/adkar/BarrierBadge'
import { ApprovalPanel } from '../components/approvals/ApprovalPanel'
import { EmptyState } from '../components/common/EmptyState'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { HeatBadge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Card, CardBody, CardHeader, CardTitle } from '../components/ui/Card'
import { useProjectContext } from '../lib/ProjectContext'

function StakeholderCard({
  projectId,
  stakeholder,
  onUpdate,
}: {
  projectId: number
  stakeholder: StakeholderImpact
  onUpdate: (updated: StakeholderImpact) => void
}) {
  const [saving, setSaving] = useState(false)

  async function handleAdkarChange(key: string, value: number) {
    setSaving(true)
    try {
      const updated = await impactApi.updateStakeholder(projectId, stakeholder.id, { [key]: value })
      onUpdate(updated)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>{stakeholder.stakeholder}</CardTitle>
        <div className="flex items-center gap-2">
          <HeatBadge rating={stakeholder.heat_rating} />
          <BarrierBadge dimension={stakeholder.adkar_barrier_dimension} />
        </div>
      </CardHeader>
      <CardBody className="space-y-4">
        <p className="text-sm text-navy-900/90">{stakeholder.what_changes}</p>

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">What's impacted</p>
            <ul className="list-inside list-disc space-y-0.5 text-navy-900/80">
              {stakeholder.what_is_impacted.map((x, i) => (
                <li key={i}>{x}</li>
              ))}
            </ul>
          </div>
          <div>
            <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">What they need to learn</p>
            <ul className="list-inside list-disc space-y-0.5 text-navy-900/80">
              {stakeholder.what_to_learn.map((x, i) => (
                <li key={i}>{x}</li>
              ))}
            </ul>
          </div>
          <div>
            <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">Resistance / risk</p>
            <ul className="list-inside list-disc space-y-0.5 text-navy-900/80">
              {stakeholder.resistance_risk.map((x, i) => (
                <li key={i}>{x}</li>
              ))}
            </ul>
          </div>
          <div>
            <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">Action required</p>
            <ul className="list-inside list-disc space-y-0.5 text-navy-900/80">
              {stakeholder.action_required.map((x, i) => (
                <li key={i}>{x}</li>
              ))}
            </ul>
          </div>
        </div>

        <div className="border-t border-navy-900/8 pt-3">
          <div className="mb-2 flex items-center justify-between">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">ADKAR Readiness (editable)</p>
            <span className="text-xs text-slate-400">
              Impact {stakeholder.impact_severity}/5 · Readiness {stakeholder.readiness_score}/100
              {saving && ' · saving…'}
            </span>
          </div>
          <AdkarScoreEditor
            values={stakeholder}
            onChange={(key, value) => handleAdkarChange(key, value)}
          />
          <p className="mt-2 text-xs italic text-slate-400">{stakeholder.adkar_rationale}</p>
        </div>
      </CardBody>
    </Card>
  )
}

export function ImpactAssessmentPage() {
  const { project } = useProjectContext()
  const [analysis, setAnalysis] = useState<ChangeImpactAnalysis | null>(null)
  const [loaded, setLoaded] = useState(false)
  const [description, setDescription] = useState('')
  const [groundInDocs, setGroundInDocs] = useState(true)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    impactApi
      .get(project.id)
      .then(setAnalysis)
      .catch(() => {})
      .finally(() => setLoaded(true))
  }, [project.id])

  async function handleGenerate() {
    if (!description.trim()) {
      setError('Enter a change description first.')
      return
    }
    setBusy(true)
    setError(null)
    try {
      const result = await impactApi.generate(project.id, description, groundInDocs)
      setAnalysis(result)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Analysis failed')
    } finally {
      setBusy(false)
    }
  }

  function updateStakeholderInState(updated: StakeholderImpact) {
    setAnalysis((prev) =>
      prev
        ? { ...prev, stakeholder_impacts: prev.stakeholder_impacts.map((s) => (s.id === updated.id ? updated : s)) }
        : prev,
    )
  }

  if (!loaded) return <LoadingSpinner />

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Change Impact Analysis</CardTitle>
        </CardHeader>
        <CardBody className="space-y-3">
          <textarea
            className="w-full rounded-md border border-navy-900/15 px-3 py-2 text-sm"
            rows={3}
            placeholder="Describe the business process change…"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
          <div className="flex items-center justify-between">
            <label className="flex items-center gap-2 text-sm text-slate-500">
              <input type="checkbox" checked={groundInDocs} onChange={(e) => setGroundInDocs(e.target.checked)} />
              Ground analysis in uploaded documents (RAG)
            </label>
            <Button disabled={busy} onClick={handleGenerate}>
              {busy ? 'Analyzing…' : analysis ? 'Re-run Analysis' : 'Analyze Impact'}
            </Button>
          </div>
          {error && <p className="text-sm text-heat-red">{error}</p>}
        </CardBody>
      </Card>

      {!analysis && (
        <EmptyState
          title="No impact analysis yet"
          description="Describe the change above and click Analyze Impact to produce a full ADKAR-scored stakeholder assessment."
        />
      )}

      {analysis && (
        <>
          <Card>
            <CardHeader>
              <CardTitle>{analysis.change_title}</CardTitle>
            </CardHeader>
            <CardBody className="space-y-4">
              <p className="text-sm text-navy-900/90">{analysis.change_summary}</p>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">Overall risks</p>
                  <ul className="list-inside list-disc space-y-0.5 text-navy-900/80">
                    {analysis.overall_risks.map((r, i) => (
                      <li key={i}>{r}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">Success factors</p>
                  <ul className="list-inside list-disc space-y-0.5 text-navy-900/80">
                    {analysis.success_factors.map((r, i) => (
                      <li key={i}>{r}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </CardBody>
          </Card>

          <ApprovalPanel projectId={project.id} artifactType="impact_analysis" artifactId={analysis.id} />

          <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
            {analysis.stakeholder_impacts.map((s) => (
              <StakeholderCard key={s.id} projectId={project.id} stakeholder={s} onUpdate={updateStakeholderInState} />
            ))}
          </div>
        </>
      )}
    </div>
  )
}
