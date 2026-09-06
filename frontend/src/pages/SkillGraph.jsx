import { useState } from 'react'
import usePageHeader from '../hooks/usePageHeader'
import Icon from '../components/ui/Icon'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import ProgressBar from '../components/ui/ProgressBar'
import { skillGraph } from '../data/mock'

/** Dependency-free radar chart. */
function Radar({ points, size = 300 }) {
  const cx = size / 2
  const cy = size / 2
  const r = size / 2 - 42
  const n = points.length

  const coords = (i, v) => {
    const a = (Math.PI * 2 * i) / n - Math.PI / 2
    return [cx + Math.cos(a) * r * (v / 100), cy + Math.sin(a) * r * (v / 100)]
  }

  const poly = points.map((p, i) => coords(i, p.value).join(',')).join(' ')

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="mx-auto max-w-full">
      {[20, 40, 60, 80, 100].map((ring) => (
        <polygon
          key={ring}
          points={points.map((_, i) => coords(i, ring).join(',')).join(' ')}
          fill="none"
          stroke="rgba(255,255,255,.06)"
          strokeWidth="1"
        />
      ))}
      {points.map((_, i) => {
        const [x, y] = coords(i, 100)
        return <line key={i} x1={cx} y1={cy} x2={x} y2={y} stroke="rgba(255,255,255,.06)" strokeWidth="1" />
      })}

      <polygon points={poly} fill="rgba(248,133,31,.18)" stroke="#F8851F" strokeWidth="2" strokeLinejoin="round" />

      {points.map((p, i) => {
        const [x, y] = coords(i, p.value)
        const [lx, ly] = coords(i, 122)
        return (
          <g key={p.name}>
            <circle cx={x} cy={y} r="3.5" fill="#F8851F" />
            <text
              x={lx}
              y={ly}
              textAnchor="middle"
              dominantBaseline="middle"
              className="fill-[#9AA7B4] text-[9px] font-medium"
              style={{ fontSize: 9.5 }}
            >
              {p.name}
            </text>
          </g>
        )
      })}
    </svg>
  )
}

export default function SkillGraph() {
  usePageHeader({ title: 'Skill Graph' })
  const [group, setGroup] = useState(skillGraph[0].group)
  const active = skillGraph.find((g) => g.group === group)

  const all = skillGraph.flatMap((g) => g.skills.map((s) => ({ ...s, group: g.group, color: g.color })))
  const gaps = [...all].sort((a, b) => a.value - b.value).slice(0, 5)
  const strengths = [...all].sort((a, b) => b.value - a.value).slice(0, 5)
  const avg = Math.round(all.reduce((a, s) => a + s.value, 0) / all.length)

  return (
    <div className="container-page space-y-5 py-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-[24px] font-extrabold tracking-tight text-white">Skill Graph</h1>
          <p className="mt-1.5 text-[13px] text-ink-dim">
            Indépendant du niveau — construit à partir de la Moulinette, des peer reviews et des challenges.
          </p>
        </div>
        <Badge tone="brand">Maîtrise moyenne {avg}%</Badge>
      </div>

      <div className="grid gap-5 xl:grid-cols-[1fr_360px]">
        <div className="space-y-5">
          {/* Radar */}
          <section className="card overflow-hidden">
            <header className="flex flex-wrap items-center justify-between gap-2 border-b border-line px-5 py-3.5">
              <h2 className="text-[13.5px] font-semibold text-ink">Vue radar</h2>
              <div className="flex flex-wrap gap-1.5">
                {skillGraph.map((g) => (
                  <button
                    key={g.group}
                    onClick={() => setGroup(g.group)}
                    className={`rounded-md px-2.5 py-1 text-[11.5px] font-semibold transition-colors ${
                      group === g.group ? 'bg-brand-500/15 text-brand-500' : 'text-ink-dim hover:text-ink'
                    }`}
                  >
                    {g.group}
                  </button>
                ))}
              </div>
            </header>
            <div className="p-5">
              <Radar points={active.skills} />
            </div>
          </section>

          {/* All groups */}
          <div className="grid gap-4 sm:grid-cols-2">
            {skillGraph.map((g) => (
              <section key={g.group} className="card p-5">
                <div className="flex items-center justify-between">
                  <h2 className="flex items-center gap-2 text-[13.5px] font-bold" style={{ color: g.color }}>
                    <span className="h-2 w-2 rounded-full" style={{ background: g.color }} />
                    {g.group}
                  </h2>
                  <span className="font-mono text-[12px] text-ink-dim">
                    {Math.round(g.skills.reduce((a, s) => a + s.value, 0) / g.skills.length)}%
                  </span>
                </div>
                <ul className="mt-4 space-y-3">
                  {g.skills.map((s) => (
                    <li key={s.name}>
                      <ProgressBar value={s.value} color={g.color} showLabel label={s.name} height={5} />
                    </li>
                  ))}
                </ul>
              </section>
            ))}
          </div>
        </div>

        {/* Rail */}
        <aside className="space-y-4">
          <section className="card p-5">
            <h2 className="flex items-center gap-2 text-[13px] font-bold text-ink">
              <Icon name="AlertTriangle" size={15} className="text-warn" /> Knowledge Gaps
            </h2>
            <p className="mt-1.5 text-[11.5px] leading-relaxed text-ink-dim">
              Le système bloque les projets qui dépendent d'une compétence sous les 40 %, et propose
              d'abord un micro-challenge.
            </p>
            <ul className="mt-4 space-y-3">
              {gaps.map((s) => (
                <li key={`${s.group}-${s.name}`}>
                  <div className="mb-1.5 flex items-center justify-between text-[11.5px]">
                    <span className="text-ink-soft">{s.name} <span className="text-ink-faint">· {s.group}</span></span>
                    <span className={`font-mono font-semibold ${s.value < 40 ? 'text-danger' : 'text-warn'}`}>{s.value}%</span>
                  </div>
                  <ProgressBar value={s.value} color={s.value < 40 ? '#E5484D' : '#F5B942'} height={4} />
                </li>
              ))}
            </ul>
            <Button size="sm" full className="mt-4" iconRight="ArrowRight">Lancer un micro-challenge</Button>
          </section>

          <section className="card p-5">
            <h2 className="flex items-center gap-2 text-[13px] font-bold text-ink">
              <Icon name="Award" size={15} className="text-ok" /> Points forts
            </h2>
            <ul className="mt-4 space-y-3">
              {strengths.map((s) => (
                <li key={`${s.group}-${s.name}`}>
                  <div className="mb-1.5 flex items-center justify-between text-[11.5px]">
                    <span className="text-ink-soft">{s.name} <span className="text-ink-faint">· {s.group}</span></span>
                    <span className="font-mono font-semibold text-ok">{s.value}%</span>
                  </div>
                  <ProgressBar value={s.value} color="#2ECC71" height={4} />
                </li>
              ))}
            </ul>
          </section>

          <section className="card p-5">
            <h2 className="flex items-center gap-2 text-[13px] font-bold text-ink">
              <Icon name="Compass" size={15} className="text-brand-500" /> Adaptive Path Engine
            </h2>
            <p className="mt-2 text-[12px] leading-relaxed text-ink-dim">
              Recommandation suivante basée sur ton profil : renforcer <span className="text-ink">Graphs</span> et{' '}
              <span className="text-ink">Complexity</span> avant d'attaquer <span className="font-mono text-ink">cub3d</span>.
            </p>
            <Button to="/projects" variant="outline" size="sm" full className="mt-4">
              Voir le parcours recommandé
            </Button>
          </section>
        </aside>
      </div>
    </div>
  )
}
