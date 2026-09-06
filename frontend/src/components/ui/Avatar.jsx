const SIZES = { xs: 'h-6 w-6', sm: 'h-8 w-8', md: 'h-10 w-10', lg: 'h-14 w-14', xl: 'h-20 w-20' }
const DOT = { xs: 'h-1.5 w-1.5', sm: 'h-2 w-2', md: 'h-2.5 w-2.5', lg: 'h-3 w-3', xl: 'h-4 w-4' }
const STATUS = { online: 'bg-ok', idle: 'bg-warn', offline: 'bg-ink-faint', busy: 'bg-danger' }

export default function Avatar({ src, name = '', size = 'md', status, ring = false, className = '' }) {
  const initials = name
    .split(/[\s_.-]+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0]?.toUpperCase())
    .join('')

  return (
    <span className={`relative inline-flex shrink-0 ${className}`}>
      <span
        className={`${SIZES[size]} grid place-items-center overflow-hidden rounded-full bg-root-750 text-[11px]
                    font-bold text-ink-soft ${ring ? 'ring-2 ring-brand-500/70 ring-offset-2 ring-offset-root-900' : 'ring-1 ring-white/10'}`}
      >
        {src ? (
          <img src={src} alt={name} loading="lazy" className="h-full w-full object-cover" />
        ) : (
          initials || '?'
        )}
      </span>
      {status && (
        <span
          className={`absolute -bottom-0 -right-0 rounded-full border-2 border-root-900 ${DOT[size]} ${STATUS[status] || STATUS.offline}`}
        />
      )}
    </span>
  )
}
