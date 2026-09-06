/**
 * Underlined tab strip matching the mockups (Leaderboard, Projects, Profile).
 */
export default function Tabs({ tabs, active, onChange, className = '', size = 'md' }) {
  const pad = size === 'sm' ? 'px-3 py-2 text-[12px]' : 'px-4 py-3 text-[13px]'
  return (
    <div className={`no-scrollbar flex overflow-x-auto border-b border-line ${className}`} role="tablist">
      {tabs.map((t) => {
        const key = t.key ?? t
        const label = t.label ?? t
        const on = active === key
        return (
          <button
            key={key}
            role="tab"
            aria-selected={on}
            onClick={() => onChange(key)}
            className={`relative shrink-0 font-semibold transition-colors ${pad} ${
              on ? 'text-brand-500' : 'text-ink-dim hover:text-ink'
            }`}
          >
            <span className="inline-flex items-center gap-2">
              {label}
              {t.count != null && (
                <span
                  className={`rounded px-1.5 py-0.5 text-[10px] font-bold ${
                    on ? 'bg-brand-500/15 text-brand-400' : 'bg-white/[0.06] text-ink-dim'
                  }`}
                >
                  {t.count}
                </span>
              )}
            </span>
            {on && <span className="absolute inset-x-0 -bottom-px h-0.5 rounded-full bg-brand-500" />}
          </button>
        )
      })}
    </div>
  )
}
