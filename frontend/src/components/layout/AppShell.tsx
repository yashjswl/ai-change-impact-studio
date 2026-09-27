import { Plus, Sparkles } from 'lucide-react'
import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { GithubIcon, LinkedinIcon } from '../ui/BrandIcons'
import { Button } from '../ui/Button'

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col bg-[#f4f6fa]">
      <header className="sticky top-0 z-10 border-b border-white/10 bg-gradient-to-r from-orange-950 via-orange-800 to-orange-700 text-white shadow-sm">
        <div className="mx-auto flex max-w-[88rem] items-center justify-between gap-4 px-6 py-3.5">
          <Link to="/" className="flex items-center gap-3">
            <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-white/10 ring-1 ring-white/15">
              <Sparkles size={18} className="text-white" />
            </span>
            <span>
              <span className="block text-base font-semibold leading-tight tracking-tight">Change Impact Studio</span>
              <span className="block text-[13px] leading-tight text-white/50">Organizational Change Management</span>
            </span>
          </Link>
          <Link to="/projects/new">
            <Button size="md" variant="secondary" className="bg-white/10 hover:bg-white/15">
              <Plus size={16} /> New Initiative
            </Button>
          </Link>
        </div>
      </header>
      <main className="mx-auto w-full max-w-7xl flex-1 px-6 py-8">{children}</main>
      <footer className="border-t border-navy-900/8 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-6 py-4 text-xs text-slate-500">
          <span>&copy; 2026 Yashasvi Jaiswal</span>
          <div className="flex items-center gap-3">
            <a
              href="https://github.com/yashjswl"
              target="_blank"
              rel="noreferrer"
              aria-label="GitHub"
              className="text-slate-400 transition-colors hover:text-navy-900"
            >
              <GithubIcon size={16} />
            </a>
            <a
              href="https://www.linkedin.com/in/yashjswl/"
              target="_blank"
              rel="noreferrer"
              aria-label="LinkedIn"
              className="text-slate-400 transition-colors hover:text-brand"
            >
              <LinkedinIcon size={16} />
            </a>
          </div>
        </div>
      </footer>
    </div>
  )
}
