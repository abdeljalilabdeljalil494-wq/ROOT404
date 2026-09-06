/**
 * Circular level gauge (0.00 → 21.00) used on the profile & portfolio headers.
 */
export default function LevelRing({ level = 0, progress = 0, size = 120, stroke = 8 }) {
  const r = (size - stroke) / 2
  const c = 2 * Math.PI * r
  const offset = c - (progress / 100) * c

  return (
    <div className="relative grid place-items-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="rgba(255,255,255,.07)" strokeWidth={stroke} />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="url(#lvl-grad)"
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={offset}
          className="transition-[stroke-dashoffset] duration-1000 ease-out"
        />
        <defs>
          <linearGradient id="lvl-grad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#FFAD57" />
            <stop offset="100%" stopColor="#F8851F" />
          </linearGradient>
        </defs>
      </svg>
      <div className="absolute inset-0 grid place-content-center text-center">
        <span className="text-[10px] font-semibold uppercase tracking-widest text-ink-dim">Niveau</span>
        <span className="text-2xl font-extrabold leading-tight text-white">{level.toFixed(2)}</span>
        <span className="text-[10px] font-medium text-brand-500">{progress}%</span>
      </div>
    </div>
  )
}
