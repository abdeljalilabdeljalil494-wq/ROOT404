import { useEffect, useState } from 'react'
import Icon from '../components/ui/Icon'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import SectionHeading from '../components/ui/SectionHeading'
import ProgressBar from '../components/ui/ProgressBar'
import { pathways, projects, howItWorks } from '../data/mock'

export default function Parcours() {
  useEffect(() => { document.title = 'Parcours — ROOT 404' }, [])
  const [active, setActive] = useState(pathways[0].name)
  const path = pathways.find((p) => p.name === active)

  return (
    <>
      <section className="relative overflow-hidden border-b border-line bg-root-950 py-20">
        <div aria-hidden className="absolute inset-0 bg-grid opacity-40" />
        <div className="container-page relative">
          <SectionHeading
            align="left"
            eyebrow="Parcours"
            title="Un cursus qui s'adapte"
            highlight="à toi"
            text="Le tronc commun pose les fondations, puis l'Adaptive Path Engine réordonne les projets selon ton Skill Graph, tes lacunes et ton rythme réel."
          />
        </div>
      </section>

      {/* Selector */}
      <section className="border-b border-line bg-root-900 py-16">
        <div className="container-page grid gap-8 lg:grid-cols-[300px_1fr]">
          <nav className="space-y-2">
            {pathways.map((p) => {
              const on = active === p.name
              return (
                <button
                  key={p.name}
                  onClick={() => setActive(p.name)}
                  className={`flex w-full items-center gap-3 rounded-xl border p-3.5 text-left transition-all ${
                    on ? 'border-brand-500/45 bg-brand-500/[0.08]' : 'border-line hover:border-line-strong'
                  }`}
                >
                  <span className="grid h-9 w-9 shrink-0 place-items-center rounded-lg" style={{ background: `${p.color}18`, color: p.color }}>
                    <Icon name={p.icon} size={17} />
                  </span>
                  <span className="min-w-0 flex-1">
                    <span className={`block truncate text-[13px] font-semibold ${on ? 'text-brand-500' : 'text-ink'}`}>{p.name}</span>
                    <span className="block font-mono text-[10.5px] text-ink-dim">{p.level}</span>
                  </span>
                  {on && <Icon name="ChevronRight" size={15} className="shrink-0 text-brand-500" />}
                </button>
              )
            })}
          </nav>

          <div className="card p-6 sm:p-8">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div className="flex items-start gap-4">
                <span className="grid h-14 w-14 shrink-0 place-items-center rounded-xl" style={{ background: `${path.color}18`, color: path.color }}>
                  <Icon name={path.icon} size={26} />
                </span>
                <div>
                  <h2 className="text-[22px] font-extrabold tracking-tight text-white">{path.name}</h2>
                  <p className="mt-1 font-mono text-[12px] font-semibold" style={{ color: path.color }}>{path.level}</p>
                </div>
              </div>
              <Button to="/register" iconRight="ArrowRight">Commencer</Button>
            </div>

            <p className="mt-5 text-[13.5px] leading-relaxed text-ink-soft">{path.desc}</p>

            <div className="mt-6 grid grid-cols-3 gap-3">
              {[
                { l: 'Projets', v: path.projects, i: 'FolderKanban' },
                { l: 'Durée', v: `${path.weeks} sem.`, i: 'Clock' },
                { l: 'Format', v: 'Solo & groupe', i: 'Users' },
              ].map((s) => (
                <div key={s.l} className="rounded-lg border border-line bg-root-850 p-4 text-center">
                  <Icon name={s.i} size={16} className="mx-auto text-ink-dim" />
                  <p className="mt-2 text-[15px] font-bold text-ink">{s.v}</p>
                  <p className="text-[11px] text-ink-dim">{s.l}</p>
                </div>
              ))}
            </div>

            <h3 className="mt-8 text-[14px] font-bold text-ink">Projets emblématiques</h3>
            <ul className="mt-4 space-y-2.5">
              {projects.slice(0, 5).map((p, i) => (
                <li key={p.id} className="flex items-center gap-3.5 rounded-lg border border-line bg-root-850 p-3.5">
                  <span className="grid h-7 w-7 shrink-0 place-items-center rounded-md bg-white/[0.05] font-mono text-[11px] font-bold text-ink-dim">
                    {String(i + 1).padStart(2, '0')}
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-mono text-[13px] font-semibold text-ink">{p.name}</p>
                    <p className="truncate text-[11.5px] text-ink-dim">{p.desc}</p>
                  </div>
                  <Badge tone="brand" className="shrink-0">{p.level}</Badge>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      {/* Level scale */}
      <section className="border-b border-line bg-root-950 py-20">
        <div className="container-page">
          <SectionHeading eyebrow="Progression" title="Une échelle continue," highlight="de 0.00 à 21.00" text="Pas de notes, pas de semestres. Chaque projet réussi ajoute un pourcentage de niveau pondéré par sa difficulté et ta note de correction." />
          <div className="mt-12 space-y-5">
            {[
              { r: '0.00 → 2.00', t: 'Piscine & fondations', d: 'Shell, logique, premiers programmes en C.', v: 100 },
              { r: '2.00 → 7.00', t: 'Programmation système', d: 'Pointeurs, mémoire, processus, get_next_line, printf.', v: 64 },
              { r: '7.00 → 12.00', t: 'Projets complexes', d: 'minishell, philosophers, cub3d, réseau et graphique.', v: 0 },
              { r: '12.00 → 17.00', t: 'Spécialisation', d: 'Web, DevOps, sécurité, IA — au choix.', v: 0 },
              { r: '17.00 → 21.00', t: 'Mentorat & professionnel', d: 'Encadrer les autres, Hiring Challenges, portfolio vérifié.', v: 0 },
            ].map((s) => (
              <div key={s.r} className="card p-5">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <span className="font-mono text-[12px] font-bold text-brand-500">{s.r}</span>
                    <h3 className="mt-1 text-[14.5px] font-bold text-white">{s.t}</h3>
                    <p className="mt-1 text-[12.5px] text-ink-dim">{s.d}</p>
                  </div>
                  <span className={`badge ${s.v === 100 ? 'bg-ok/12 text-ok' : s.v > 0 ? 'bg-brand-500/12 text-brand-500' : 'bg-white/[0.05] text-ink-dim'}`}>
                    {s.v === 100 ? 'Terminé' : s.v > 0 ? 'En cours' : 'À venir'}
                  </span>
                </div>
                <ProgressBar value={s.v} height={5} className="mt-4" />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Lifecycle */}
      <section className="bg-root-900 py-20">
        <div className="container-page">
          <SectionHeading eyebrow="Project Lifecycle" title="Le même cycle" highlight="pour chaque projet" />
          <ol className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {howItWorks.map((s) => (
              <li key={s.step} className="card flex gap-4 p-5">
                <span className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-brand-500/10 text-brand-500">
                  <Icon name={s.icon} size={19} />
                </span>
                <div>
                  <span className="font-mono text-[11px] font-bold text-ink-faint">{s.step}</span>
                  <h3 className="text-[13.5px] font-bold text-white">{s.title}</h3>
                  <p className="mt-1.5 text-[12px] leading-relaxed text-ink-dim">{s.text}</p>
                </div>
              </li>
            ))}
          </ol>
        </div>
      </section>
    </>
  )
}
