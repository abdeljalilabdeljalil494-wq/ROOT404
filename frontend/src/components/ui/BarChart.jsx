/**
 * Dependency-free vertical bar chart (weekly activity card on the dashboard).
 */
export default function BarChart({ data, height = 130, color = '#F8851F', suffix = '' }) {
  const max = Math.max(...data.map((d) => d.value), 1)
  return (
    <div className="flex w-full items-end gap-2" style={{ height }}>
      {data.map((d, i) => {
        const h = Math.max(4, (d.value / max) * 100)
        return (
          <div key={d.day ?? i} className="group flex h-full flex-1 flex-col items-center justify-end gap-2">
            <span className="text-[10px] font-semibold text-ink opacity-0 transition-opacity group-hover:opacity-100">
              {d.value}
              {suffix}
            </span>
            <div className="flex w-full flex-1 items-end">
              <div
                className="w-full rounded-t-[3px] transition-all duration-500 ease-out group-hover:brightness-125"
                style={{
                  height: `${h}%`,
                  background: `linear-gradient(180deg, ${color}, ${color}55)`,
                }}
              />
            </div>
            <span className="text-[10px] font-medium text-ink-dim">{d.day ?? d.label}</span>
          </div>
        )
      })}
    </div>
  )
}
