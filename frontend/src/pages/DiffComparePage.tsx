import { useState } from 'react'
import { diffApi } from '../api/diff'
import type { DocumentDiffAnalysis } from '../api/types'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { Card, CardBody, CardHeader, CardTitle } from '../components/ui/Card'
import { useProjectContext } from '../lib/ProjectContext'

export function DiffComparePage() {
  const { project } = useProjectContext()
  const [question, setQuestion] = useState('What changed between the old and new processes?')
  const [result, setResult] = useState<DocumentDiffAnalysis | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleCompare() {
    setBusy(true)
    setError(null)
    try {
      setResult(await diffApi.compare(project.id, question))
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Comparison failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Compare Old vs. New Process Documentation</CardTitle>
        </CardHeader>
        <CardBody className="space-y-3">
          <p className="text-sm text-slate-500">
            Retrieves relevant excerpts from uploaded documents (TF-IDF) and asks the model for a structured,
            cited comparison. Every citation is verified against the retrieved source text.
          </p>
          <div className="flex gap-2">
            <input
              className="flex-1 rounded-md border border-navy-900/15 px-3 py-2 text-sm"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
            />
            <Button disabled={busy} onClick={handleCompare}>
              {busy ? 'Comparing…' : 'Compare'}
            </Button>
          </div>
          {error && <p className="text-sm text-heat-red">{error}</p>}
        </CardBody>
      </Card>

      {result && (
        <Card>
          <CardHeader>
            <CardTitle>Summary</CardTitle>
          </CardHeader>
          <CardBody className="space-y-5">
            <p className="text-sm text-navy-900/90">{result.summary}</p>
            <div className="space-y-4">
              {result.findings.map((f) => (
                <div key={f.id} className="rounded-lg border border-navy-900/8 p-4">
                  <p className="mb-2 font-medium text-navy-900">{f.topic}</p>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">Old State</p>
                      <p className="text-navy-900/80">{f.old_state}</p>
                    </div>
                    <div>
                      <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500">New State</p>
                      <p className="text-navy-900/80">{f.new_state}</p>
                    </div>
                  </div>
                  <div className="mt-3 space-y-1.5">
                    {f.citations.map((c) => (
                      <div key={c.id} className="flex items-start gap-2 text-xs">
                        <Badge tone={c.verified ? 'green' : 'red'}>{c.verified ? 'Verified' : 'Unverified'}</Badge>
                        <span className="text-slate-500">
                          "{c.excerpt}", <span className="font-medium">{c.source}</span>
                          {!c.verified && c.verification_note && ` (${c.verification_note})`}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>
      )}
    </div>
  )
}
