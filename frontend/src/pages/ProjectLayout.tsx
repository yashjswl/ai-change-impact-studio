import { Check, MoreVertical, Pencil, Trash2, X } from 'lucide-react'
import { useCallback, useEffect, useRef, useState } from 'react'
import { Link, Outlet, useNavigate, useParams } from 'react-router-dom'
import { projectsApi } from '../api/projects'
import type { Project } from '../api/types'
import { ConfirmDialog } from '../components/ui/ConfirmDialog'
import { LoadingSpinner } from '../components/common/LoadingSpinner'
import { Tabs } from '../components/ui/Tabs'
import { ProjectContext } from '../lib/ProjectContext'

export function ProjectLayout() {
  const { projectId } = useParams<{ projectId: string }>()
  const id = Number(projectId)
  const navigate = useNavigate()
  const [project, setProject] = useState<Project | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [menuOpen, setMenuOpen] = useState(false)
  const [renaming, setRenaming] = useState(false)
  const [draftName, setDraftName] = useState('')
  const [busy, setBusy] = useState(false)
  const [confirmingDelete, setConfirmingDelete] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  const load = useCallback(() => {
    projectsApi
      .get(id)
      .then(setProject)
      .catch((e) => setError(e.message))
  }, [id])

  useEffect(() => {
    load()
  }, [load])

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) setMenuOpen(false)
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  function startRename() {
    setDraftName(project?.name ?? '')
    setRenaming(true)
    setMenuOpen(false)
  }

  async function saveRename() {
    if (!project || !draftName.trim() || draftName === project.name) {
      setRenaming(false)
      return
    }
    setBusy(true)
    try {
      const updated = await projectsApi.update(project.id, { name: draftName.trim() })
      setProject(updated)
      setRenaming(false)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Rename failed')
    } finally {
      setBusy(false)
    }
  }

  async function confirmDelete() {
    if (!project) return
    setBusy(true)
    try {
      await projectsApi.remove(project.id)
      navigate('/')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Delete failed')
      setBusy(false)
      setConfirmingDelete(false)
    }
  }

  if (error) return <p className="text-sm text-heat-red">{error}</p>
  if (!project) return <LoadingSpinner label="Loading initiative…" />

  const base = `/projects/${id}`

  return (
    <ProjectContext.Provider value={{ project, refresh: load }}>
      <div className="space-y-5">
        <div>
          <Link to="/" className="text-xs text-slate-500 hover:text-navy-900">
            ← Portfolio
          </Link>
          <div className="mt-1 flex items-center gap-2">
            {renaming ? (
              <>
                <input
                  autoFocus
                  className="rounded-md border border-navy-900/15 px-2 py-1 text-xl font-semibold text-navy-900 focus:outline-none focus:ring-2 focus:ring-brand/30"
                  value={draftName}
                  disabled={busy}
                  onChange={(e) => setDraftName(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') saveRename()
                    if (e.key === 'Escape') setRenaming(false)
                  }}
                />
                <button onClick={saveRename} disabled={busy} className="text-heat-green hover:opacity-80" aria-label="Save name">
                  <Check size={18} />
                </button>
                <button onClick={() => setRenaming(false)} disabled={busy} className="text-slate-400 hover:text-navy-900" aria-label="Cancel">
                  <X size={18} />
                </button>
              </>
            ) : (
              <>
                <h1 className="text-xl font-semibold text-navy-900">{project.name}</h1>
                <div className="relative" ref={menuRef}>
                  <button
                    onClick={() => setMenuOpen((o) => !o)}
                    className="rounded-md p-1 text-slate-400 hover:bg-navy-900/5 hover:text-navy-900"
                    aria-label="Initiative options"
                  >
                    <MoreVertical size={16} />
                  </button>
                  {menuOpen && (
                    <div className="absolute left-0 top-full z-20 mt-1 w-40 overflow-hidden rounded-md border border-navy-900/10 bg-white py-1 shadow-lg">
                      <button
                        onClick={startRename}
                        className="flex w-full items-center gap-2 px-3 py-1.5 text-left text-sm text-navy-900 hover:bg-navy-900/5"
                      >
                        <Pencil size={14} /> Rename
                      </button>
                      <button
                        onClick={() => {
                          setMenuOpen(false)
                          setConfirmingDelete(true)
                        }}
                        className="flex w-full items-center gap-2 px-3 py-1.5 text-left text-sm text-heat-red hover:bg-heat-red-bg"
                      >
                        <Trash2 size={14} /> Delete
                      </button>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
          <p className="text-sm text-slate-500">{project.change_type} initiative</p>
        </div>
        <Tabs
          items={[
            { label: 'Overview', to: base, end: true },
            { label: 'Documents', to: `${base}/documents` },
            { label: 'Impact & ADKAR', to: `${base}/impact` },
            { label: 'Heat Map', to: `${base}/heatmap` },
            { label: 'RACI', to: `${base}/raci` },
            { label: 'RAID Log', to: `${base}/raid` },
            { label: 'Communications', to: `${base}/comms` },
            { label: 'Training', to: `${base}/training` },
            { label: 'Compare Docs', to: `${base}/diff` },
            { label: 'Audit Trail', to: `${base}/audit` },
          ]}
        />
        <Outlet />
      </div>
      <ConfirmDialog
        open={confirmingDelete}
        title={`Delete "${project.name}"?`}
        description="This permanently removes all its documents, analysis, RACI, RAID, communications, and history. This cannot be undone."
        confirmLabel="Delete Initiative"
        busy={busy}
        onConfirm={confirmDelete}
        onCancel={() => setConfirmingDelete(false)}
      />
    </ProjectContext.Provider>
  )
}
