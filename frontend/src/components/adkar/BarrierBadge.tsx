import { Badge } from '../ui/Badge'

export function BarrierBadge({ dimension }: { dimension: string | null }) {
  if (!dimension) return <Badge tone="green">No barrier</Badge>
  return <Badge tone="amber">Barrier: {dimension}</Badge>
}
