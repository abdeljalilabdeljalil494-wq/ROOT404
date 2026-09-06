/**
 * Thin progress track used across dashboard, projects and skill graph.
 */
export default function ProgressBar({
  value = 0,
  color = '#F8851F',
  height = 6,
  className = '',
  showLabel = false,
  label,
  trackClass = 'bg-white/[0.07]',
}) {
  const v = Math.max(0, Math.min(100, value))
  return (
    <div className={className}>
      {showLabel && (
        <div className="mb-1.5 flex items-center justify-between text-[11px]">
          <span className="text-ink-soft">{label}</span>
          <span className="font-mono font-semibold text-ink">{v}%</span>
        </div>
      )}
      <div
        className={`w-full overflow-hidden rounded-full ${trackClass}`}
        style={{ height }}
        role="progressbar"
        aria-valuenow={v}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        <div
          className="h-full rounded-full transition-[width] duration-700 ease-out"
          style={{
            width: `${v}%`,
            background: `linear-gradient(90deg, ${color}CC, ${color})`,
            boxShadow: `0 0 12px -2px ${color}99`,
          }}
        />
      </div>
    </div>
  )
}
