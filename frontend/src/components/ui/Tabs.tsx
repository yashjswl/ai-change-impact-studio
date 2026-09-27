import { NavLink } from 'react-router-dom'
import { cn } from '../../lib/utils'

export interface TabItem {
  label: string
  to: string
  end?: boolean
}

export function Tabs({ items }: { items: TabItem[] }) {
  return (
    <nav className="flex gap-1 overflow-x-auto border-b border-navy-900/8">
      {items.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.end}
          className={({ isActive }) =>
            cn(
              'whitespace-nowrap border-b-2 px-3 py-2.5 text-sm font-medium transition-colors',
              isActive
                ? 'border-brand text-brand'
                : 'border-transparent text-slate-500 hover:text-navy-900',
            )
          }
        >
          {item.label}
        </NavLink>
      ))}
    </nav>
  )
}
