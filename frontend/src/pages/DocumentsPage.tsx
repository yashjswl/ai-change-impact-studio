import { Trash2, Upload } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { documentsApi } from '../api/documents'
import type { DocumentItem } from '../api/types'
import { EmptyState } from '../components/common/EmptyState'
import { Button } from '../components/ui/Button'
import { Card, CardBody, CardHeader, CardTitle } from '../components/ui/Card'
import { Table, Td, Th, Thead, Tr } from '../components/ui/Table'
import { useProjectContext } from '../lib/ProjectContext'
import { formatDate } from '../lib/utils'

const DOC_TYPES = [
  { value: 'old_process', label: 'Old Process' },
  { value: 'new_process', label: 'New Process' },
  { value: 'policy', label: 'Policy' },
  { value: 'implementation_plan', label: 'Implementation Plan' },
  { value: 'other', label: 'Other' },
]

export function DocumentsPage() {
  const { project } = useProjectContext()
  const [docs, setDocs] = useState<DocumentItem[] | null>(null)
  const [docType, setDocType] = useState('old_process')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const fileRef = useRef<HTMLInputElement>(null)

  function load() {
    documentsApi.list(project.id).then(setDocs).catch((e) => setError(e.message))
  }

  useEffect(load, [project.id])

  async function handleUpload() {
    const file = fileRef.current?.files?.[0]
    if (!file) return
    setBusy(true)
    setError(null)
    try {
      await documentsApi.upload(project.id, file, docType)
      if (fileRef.current) fileRef.current.value = ''
      load()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Upload failed')
    } finally {
      setBusy(false)
    }
  }

  async function handleLoadSamples() {
    setBusy(true)
    setError(null)
    try {
      await documentsApi.loadSamples(project.id)
      load()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load sample docs')
    } finally {
      setBusy(false)
    }
  }

  async function handleDelete(docId: number) {
    await documentsApi.remove(project.id, docId)
    load()
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Upload Documents</CardTitle>
        </CardHeader>
        <CardBody className="space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <select
              className="rounded-md border border-navy-900/15 px-2.5 py-1.5 text-sm"
              value={docType}
              onChange={(e) => setDocType(e.target.value)}
            >
              {DOC_TYPES.map((t) => (
                <option key={t.value} value={t.value}>
                  {t.label}
                </option>
              ))}
            </select>
            <input ref={fileRef} type="file" accept=".txt,.md,.pdf" className="text-sm" />
            <Button size="sm" disabled={busy} onClick={handleUpload}>
              <Upload size={14} /> Upload
            </Button>
            <span className="text-xs text-slate-400">or</span>
            <Button size="sm" variant="outline" disabled={busy} onClick={handleLoadSamples}>
              Load Sample Docs
            </Button>
          </div>
          {error && <p className="text-sm text-heat-red">{error}</p>}
        </CardBody>
      </Card>

      {docs && docs.length === 0 && (
        <EmptyState
          title="No documents yet"
          description="Upload old/new process docs, policies, and an implementation plan, or load the sample onboarding-automation dataset."
        />
      )}

      {docs && docs.length > 0 && (
        <Card>
          <Table>
            <Thead>
              <Tr>
                <Th>Filename</Th>
                <Th>Type</Th>
                <Th>Size</Th>
                <Th>Uploaded</Th>
                <Th />
              </Tr>
            </Thead>
            <tbody>
              {docs.map((d) => (
                <Tr key={d.id}>
                  <Td className="font-medium">{d.filename}</Td>
                  <Td>{d.doc_type}</Td>
                  <Td>{d.char_count.toLocaleString()} chars</Td>
                  <Td>{formatDate(d.uploaded_at)}</Td>
                  <Td>
                    <button onClick={() => handleDelete(d.id)} className="text-slate-400 hover:text-heat-red">
                      <Trash2 size={14} />
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
