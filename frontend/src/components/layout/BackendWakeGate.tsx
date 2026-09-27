import { Sparkles } from 'lucide-react'
import { type ReactNode, useEffect, useState } from 'react'
import { API_URL } from '../../api/client'

const SLOW_THRESHOLD_MS = 1200
const POLL_INTERVAL_MS = 3000
const HEALTH_TIMEOUT_MS = 10000

type Status = 'checking' | 'waking' | 'ready'

/** Render's free tier spins the backend down after inactivity, so the first
 * request after a while can take up to a minute. Rather than let that show
 * up as an unexplained hang on the portfolio page, ping /health up front
 * and explain what's happening if it's slow. Warm backends pass through
 * with a near-imperceptible delay. */
export function BackendWakeGate({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<Status>('checking')

  useEffect(() => {
    let cancelled = false
    let slowTimer: ReturnType<typeof setTimeout>

    async function pingOnce(): Promise<boolean> {
      const controller = new AbortController()
      const timeout = setTimeout(() => controller.abort(), HEALTH_TIMEOUT_MS)
      try {
        const res = await fetch(`${API_URL}/health`, { signal: controller.signal })
        return res.ok
      } catch {
        return false
      } finally {
        clearTimeout(timeout)
      }
    }

    async function run() {
      slowTimer = setTimeout(() => {
        if (!cancelled) setStatus('waking')
      }, SLOW_THRESHOLD_MS)

      let ok = await pingOnce()
      while (!ok && !cancelled) {
        await new Promise((r) => setTimeout(r, POLL_INTERVAL_MS))
        ok = await pingOnce()
      }
      clearTimeout(slowTimer)
      if (!cancelled) setStatus('ready')
    }

    run()
    return () => {
      cancelled = true
      clearTimeout(slowTimer)
    }
  }, [])

  if (status === 'ready') return <>{children}</>

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-[#f4f6fa] px-6 text-center">
      <div className="relative flex h-14 w-14 items-center justify-center">
        <span className="absolute inset-0 animate-spin rounded-full border-2 border-brand/15 border-t-brand" />
        <Sparkles size={20} className="text-brand" />
      </div>
      <p className="mt-5 text-base font-semibold text-navy-900">
        {status === 'waking' ? 'Waking up the server…' : 'Connecting…'}
      </p>
      {status === 'waking' && (
        <p className="mt-1.5 max-w-xs text-sm text-slate-500">
          The backend runs on free hosting that spins down after inactivity. This can take up to a minute on the
          first visit and only happens once.
        </p>
      )}
    </div>
  )
}
