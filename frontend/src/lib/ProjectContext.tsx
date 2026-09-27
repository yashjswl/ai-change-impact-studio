import { createContext, useContext } from 'react'
import type { Project } from '../api/types'

export interface ProjectContextValue {
  project: Project
  refresh: () => void
}

export const ProjectContext = createContext<ProjectContextValue | null>(null)

export function useProjectContext(): ProjectContextValue {
  const ctx = useContext(ProjectContext)
  if (!ctx) throw new Error('useProjectContext must be used within a ProjectLayout')
  return ctx
}
