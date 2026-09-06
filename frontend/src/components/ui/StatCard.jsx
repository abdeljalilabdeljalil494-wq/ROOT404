import Icon from './Icon'

/**
 * Compact KPI tile — used on the dashboard grid and on the profile header.
 */
export default function StatCard({ icon, label, value, sub, delta, tone = 'brand', className = '' }) {
  const toneText = {
    brand: 'text-brand-500',
    ok: 'text-ok',
    info: 'text-info',
    warn: 'text-warn',
  }[tone]

  return (
    <div className={`card group p-4 transition-colors hover:border-line-strong ${className}`}>
      <div className="flex items-start justify-between gap-2">
        <span className="text-[11px] font-medium uppercase tracking-wide text-ink-dim">{label}</span>
        {icon && (
          <span className={`grid h-7 w-7 place-items-center rounded-md bg-white/[0.04] ${toneText}`}>
            <Icon name={icon} size={14} />
          </span>
        )}
      </div>
      <div className="mt-2.5 flex items-baseline gap-2">
        <span className="stat-num">{value}</span>
        {delta && <span className="text-[11px] font-semibold text-ok">{delta}</span>}
      </div>
      {sub && <p className="mt-1 text-[11px] text-ink-dim">{sub}</p>}
    </div>
  )
}
