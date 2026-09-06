const TONES = {
  brand: 'bg-brand-500/12 text-brand-400 ring-1 ring-inset ring-brand-500/25',
  ok: 'bg-ok/12 text-ok ring-1 ring-inset ring-ok/25',
  danger: 'bg-danger/12 text-danger ring-1 ring-inset ring-danger/25',
  warn: 'bg-warn/12 text-warn ring-1 ring-inset ring-warn/25',
  info: 'bg-info/12 text-info ring-1 ring-inset ring-info/25',
  muted: 'bg-white/[0.05] text-ink-dim ring-1 ring-inset ring-white/10',
  solid: 'bg-brand-500 text-[#160A00]',
}

export default function Badge({ children, tone = 'muted', className = '', dot = false }) {
  return (
    <span
      className={`badge ${TONES[tone] || TONES.muted} ${className}`}
    >
      {dot && <span className="h-1.5 w-1.5 rounded-full bg-current" />}
      {children}
    </span>
  )
}
