import type { HTMLAttributes } from 'react'
import { cn } from '../../lib/utils'

type Tone = 'neutral' | 'red' | 'amber' | 'green' | 'brand'

const toneClasses: Record<Tone, string> = {
  neutral: 'bg-slate-500/10 text-slate-500',
  red: 'bg-heat-red-bg text-heat-red',
  amber: 'bg-heat-amber-bg text-heat-amber',
  green: 'bg-heat-green-bg text-heat-green',
  brand: 'bg-brand/10 text-brand',
}

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: Tone
}

export function Badge({ tone = 'neutral', className, ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
        toneClasses[tone],
        className,
      )}
      {...props}
    />
  )
}

const HEAT_TONE: Record<string, Tone> = { Red: 'red', Amber: 'amber', Green: 'green' }
const SEVERITY_TONE: Record<string, Tone> = {
  Critical: 'red',
  High: 'red',
  Medium: 'amber',
  Low: 'green',
}

export function HeatBadge({ rating }: { rating: string }) {
  return <Badge tone={HEAT_TONE[rating] ?? 'neutral'}>{rating}</Badge>
}

export function SeverityBadge({ severity }: { severity: string }) {
  return <Badge tone={SEVERITY_TONE[severity] ?? 'neutral'}>{severity}</Badge>
}
