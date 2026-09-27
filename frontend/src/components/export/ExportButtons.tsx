import { Download } from 'lucide-react'
import { useState } from 'react'
import { exportsApi } from '../../api/exports'
import { Button } from '../ui/Button'

type ExportKind = 'impact-onepager' | 'comms-package' | 'executive-summary'

const LABELS: Record<ExportKind, string> = {
  'impact-onepager': 'Export Impact Assessment (.docx)',
  'comms-package': 'Export Communications (.docx)',
  'executive-summary': 'Export Executive Summary (.pptx)',
}

export function ExportButton({ projectId, kind }: { projectId: number; kind: ExportKind }) {
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleClick() {
    setBusy(true)
    setError(null)
    try {
      const fn =
        kind === 'impact-onepager'
          ? exportsApi.impactOnepager
          : kind === 'comms-package'
            ? exportsApi.commsPackage
            : exportsApi.executiveSummary
      const record = await fn(projectId)
      const url = exportsApi.downloadUrl(record.id)
      window.open(url, '_blank')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Export failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="inline-flex flex-col items-start gap-1">
      <Button size="sm" variant="outline" disabled={busy} onClick={handleClick}>
        <Download size={14} /> {busy ? 'Generating…' : LABELS[kind]}
      </Button>
      {error && <p className="text-xs text-heat-red">{error}</p>}
    </div>
  )
}
