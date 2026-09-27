import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { projectsApi } from '../api/projects'
import { Button } from '../components/ui/Button'
import { Card, CardBody, CardHeader, CardTitle } from '../components/ui/Card'

const CHANGE_TYPES = ['Process', 'Systems', 'Organizational', 'Policy']

export function NewProjectPage() {
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [changeType, setChangeType] = useState('Process')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!name.trim()) {
      setError('Name is required.')
      return
    }
    setBusy(true)
    setError(null)
    try {
      const project = await projectsApi.create({ name, description, change_type: changeType })
      navigate(`/projects/${project.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create project')
      setBusy(false)
    }
  }

  return (
    <div className="mx-auto max-w-xl">
      <Card>
        <CardHeader>
          <CardTitle>New Change Initiative</CardTitle>
        </CardHeader>
        <CardBody>
          <form className="space-y-4" onSubmit={handleSubmit}>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-500">Name</label>
              <input
                className="w-full rounded-md border border-navy-900/15 px-3 py-2 text-sm"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Employee Onboarding Automation"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-500">Description</label>
              <textarea
                className="w-full rounded-md border border-navy-900/15 px-3 py-2 text-sm"
                rows={3}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Short context for this change initiative"
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-500">Change Type</label>
              <select
                className="w-full rounded-md border border-navy-900/15 px-3 py-2 text-sm"
                value={changeType}
                onChange={(e) => setChangeType(e.target.value)}
              >
                {CHANGE_TYPES.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>
            {error && <p className="text-sm text-heat-red">{error}</p>}
            <Button type="submit" disabled={busy} className="w-full">
              {busy ? 'Creating…' : 'Create Initiative'}
            </Button>
          </form>
        </CardBody>
      </Card>
    </div>
  )
}
