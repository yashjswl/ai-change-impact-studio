import { Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from './components/layout/AppShell'
import { AuditPage } from './pages/AuditPage'
import { CommsPlanPage } from './pages/CommsPlanPage'
import { DiffComparePage } from './pages/DiffComparePage'
import { DocumentsPage } from './pages/DocumentsPage'
import { HeatmapPage } from './pages/HeatmapPage'
import { ImpactAssessmentPage } from './pages/ImpactAssessmentPage'
import { NewProjectPage } from './pages/NewProjectPage'
import { PortfolioDashboardPage } from './pages/PortfolioDashboardPage'
import { ProjectLayout } from './pages/ProjectLayout'
import { ProjectOverviewPage } from './pages/ProjectOverviewPage'
import { RaciPage } from './pages/RaciPage'
import { RaidPage } from './pages/RaidPage'
import { TrainingMatrixPage } from './pages/TrainingMatrixPage'

export default function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<PortfolioDashboardPage />} />
        <Route path="/projects/new" element={<NewProjectPage />} />
        <Route path="/projects/:projectId" element={<ProjectLayout />}>
          <Route index element={<ProjectOverviewPage />} />
          <Route path="documents" element={<DocumentsPage />} />
          <Route path="impact" element={<ImpactAssessmentPage />} />
          <Route path="heatmap" element={<HeatmapPage />} />
          <Route path="raci" element={<RaciPage />} />
          <Route path="raid" element={<RaidPage />} />
          <Route path="comms" element={<CommsPlanPage />} />
          <Route path="training" element={<TrainingMatrixPage />} />
          <Route path="diff" element={<DiffComparePage />} />
          <Route path="audit" element={<AuditPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AppShell>
  )
}
