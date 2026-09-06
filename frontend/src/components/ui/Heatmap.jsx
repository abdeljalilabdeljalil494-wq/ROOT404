import { heatmap } from '../../data/mock'

const SHADES = ['#0F151C', '#1E3A24', '#2A6B36', '#35A34A', '#42D95F']
const MONTHS = ['Sep', 'Oct', 'Nov', 'Déc', 'Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août']
const DAYS = ['Lun', '', 'Mer', '', 'Ven', '', '']

/**
 * GitHub-style contribution heatmap — 53 weeks × 7 days.
 */
export default function Heatmap({ data = heatmap, className = '' }) {
  const weeks = Array.from({ length: 53 }, (_, w) => data.slice(w * 7, w * 7 + 7))
  const total = data.filter((v) => v > 0).length

  return (
    <div className={className}>
      <div className="no-scrollbar overflow-x-auto pb-1">
        <div className="inline-block min-w-full">
          {/* Month labels */}
          <div className="mb-1.5 flex gap-[3px] pl-8">
            {MONTHS.map((m) => (
              <span key={m} className="w-[calc(4.42*13px)] shrink-0 text-[9.5px] text-ink-faint">
                {m}
              </span>
            ))}
          </div>

          <div className="flex gap-[3px]">
            {/* Weekday labels */}
            <div className="mr-1 flex w-7 shrink-0 flex-col gap-[3px]">
              {DAYS.map((d, i) => (
                <span key={i} className="h-[10px] text-[9px] leading-[10px] text-ink-faint">{d}</span>
              ))}
            </div>

            {weeks.map((week, wi) => (
              <div key={wi} className="flex flex-col gap-[3px]">
                {week.map((v, di) => (
                  <span
                    key={di}
                    title={`${v * 3} contributions`}
                    className="h-[10px] w-[10px] rounded-[2px] transition-transform hover:scale-125"
                    style={{ background: SHADES[v] }}
                  />
                ))}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-3 flex flex-wrap items-center justify-between gap-3 text-[11px] text-ink-dim">
        <span>
          <span className="font-semibold text-ink">{total}</span> jours actifs cette année
        </span>
        <span className="flex items-center gap-1.5">
          Moins
          {SHADES.map((s) => (
            <span key={s} className="h-[10px] w-[10px] rounded-[2px]" style={{ background: s }} />
          ))}
          Plus
        </span>
      </div>
    </div>
  )
}
