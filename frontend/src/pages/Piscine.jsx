import usePageHeader from '../hooks/usePageHeader'
import Icon from '../components/ui/Icon'
import Button from '../components/ui/Button'
import ProgressBar from '../components/ui/ProgressBar'
import { piscineDays, piscineStats } from '../data/mock'

const RULES = [
  { icon: 'CalendarDays', t: '4 semaines, 28 jours', d: 'Un exercice quotidien dont la difficulté monte en flèche, plus un Rush chaque week-end.' },
  { icon: 'Users', t: 'Correction obligatoire', d: 'Chaque exercice doit être corrigé par un pair avant d’être comptabilisé.' },
  { icon: 'Activity', t: 'Consistency Score', d: 'La régularité pèse autant que la réussite dans la décision finale d’admission.' },
  { icon: 'Trophy', t: 'Taux d’admission', d: 'Calculé sur la complétion, la qualité du code (Norme) et l’activité de correction.' },
]

export default function Piscine() {
  usePageHeader({ title: 'Piscine' })

  const done = piscineDays.filter((d) => d.status === 'done')
  const avg = Math.round(done.reduce((a, d) => a + d.score, 0) / done.length)

  return (
    <div className="container-page space-y-5 py-6">
      {/* Banner */}
      <section className="card relative overflow-hidden">
        <div aria-hidden className="absolute inset-0 bg-gradient-to-br from-info/[0.12] via-transparent to-brand-500/[0.09]" />
        <div aria-hidden className="absolute inset-0 bg-grid opacity-30" />
        <div className="relative flex flex-col gap-6 p-6 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div className="flex items-center gap-2.5">
              <span className="grid h-11 w-11 place-items-center rounded-xl bg-info/15 text-info">
                <Icon name="Waves" size={22} />
              </span>
              <div>
                <h1 className="text-[24px] font-extrabold tracking-tight text-white">Piscine — Session Sept. 2026</h1>
                <p className="text-[12.5px] text-ink-dim">Campus Tunis · 218 participants</p>
              </div>
            </div>
            <p className="mt-4 max-w-xl text-[13px] leading-relaxed text-ink-soft">
              Quatre semaines de code intensif. Aucun cours, aucun prof — seulement des sujets, des
              pairs et une Moulinette qui ne pardonne rien. Le seul filtre d'entrée de ROOT 404.
            </p>
          </div>

          <div className="shrink-0 rounded-xl border border-line bg-root-850/80 p-5 backdrop-blur-sm lg:w-64">
            <p className="text-[10.5px] font-bold uppercase tracking-wider text-ink-dim">Progression</p>
            <p className="mt-1 font-mono text-[30px] font-extrabold leading-none text-white">
              12<span className="text-[16px] text-ink-dim">/28</span>
            </p>
            <ProgressBar value={(12 / 28) * 100} height={6} className="mt-3" />
            <p className="mt-3 flex items-center justify-between text-[11.5px] text-ink-dim">
              <span>Moyenne</span>
              <span className="font-mono font-bold text-brand-500">{avg}/100</span>
            </p>
          </div>
        </div>
      </section>

      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {piscineStats.map((s) => (
          <div key={s.label} className="card flex items-center gap-3.5 p-4">
            <span className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-brand-500/10 text-brand-500">
              <Icon name={s.icon} size={18} />
            </span>
            <div>
              <p className="text-[11px] uppercase tracking-wider text-ink-dim">{s.label}</p>
              <p className="font-mono text-[18px] font-extrabold text-ink">{s.value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Calendar */}
      <section className="card overflow-hidden">
        <header className="flex flex-wrap items-center justify-between gap-3 border-b border-line px-5 py-3.5">
          <h2 className="flex items-center gap-2 text-[13.5px] font-semibold text-ink">
            <Icon name="CalendarDays" size={15} className="text-brand-500" /> Calendrier des 28 jours
          </h2>
          <div className="flex flex-wrap items-center gap-3 text-[11px] text-ink-dim">
            {[
              { c: 'bg-ok', l: 'Validé' },
              { c: 'bg-brand-500', l: 'Aujourd’hui' },
              { c: 'bg-root-750', l: 'À venir' },
            ].map((k) => (
              <span key={k.l} className="flex items-center gap-1.5">
                <span className={`h-2.5 w-2.5 rounded-sm ${k.c}`} /> {k.l}
              </span>
            ))}
          </div>
        </header>

        <div className="grid grid-cols-4 gap-2.5 p-5 sm:grid-cols-7">
          {piscineDays.map((d) => {
            const done = d.status === 'done'
            const today = d.status === 'today'
            return (
              <button
                key={d.day}
                className={`group relative flex aspect-square flex-col items-center justify-center rounded-lg border p-2 text-center transition-all ${
                  done
                    ? 'border-ok/25 bg-ok/[0.08] hover:border-ok/50'
                    : today
                      ? 'border-brand-500 bg-brand-500/12 shadow-glow'
                      : 'border-line bg-root-850 opacity-60 hover:opacity-100'
                }`}
              >
                {d.isRush && (
                  <span className="absolute right-1.5 top-1.5 text-warn" title="Rush week-end">
                    <Icon name="Zap" size={11} />
                  </span>
                )}
                <span className={`font-mono text-[15px] font-extrabold ${done ? 'text-ok' : today ? 'text-brand-500' : 'text-ink-faint'}`}>
                  {String(d.day).padStart(2, '0')}
                </span>
                <span className="mt-0.5 truncate text-[9.5px] text-ink-dim">{d.topic}</span>
                {done && <span className="mt-1 font-mono text-[10px] font-bold text-ok">{d.score}</span>}
                {!done && !today && <Icon name="Lock" size={10} className="mt-1 text-ink-faint" />}
              </button>
            )
          })}
        </div>

        <div className="border-t border-line p-5">
          <div className="flex flex-wrap items-center justify-between gap-4 rounded-lg border border-brand-500/25 bg-brand-500/[0.07] p-4">
            <div>
              <p className="flex items-center gap-2 text-[13px] font-bold text-brand-400">
                <Icon name="Zap" size={15} /> Day 12 — Structs & allocation dynamique
              </p>
              <p className="mt-1 text-[12px] text-ink-dim">
                8 exercices · disponible jusqu'à 23:42 · correction pair obligatoire
              </p>
            </div>
            <Button to="/workspace/piscine-day-12" iconRight="ArrowRight">Commencer</Button>
          </div>
        </div>
      </section>

      {/* Rules */}
      <section className="card p-6">
        <h2 className="text-[15px] font-bold text-ink">Comment fonctionne la Piscine</h2>
        <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {RULES.map((r) => (
            <div key={r.t} className="rounded-xl border border-line bg-root-850 p-4">
              <span className="grid h-9 w-9 place-items-center rounded-lg bg-brand-500/10 text-brand-500">
                <Icon name={r.icon} size={17} />
              </span>
              <h3 className="mt-3 text-[13px] font-bold text-ink">{r.t}</h3>
              <p className="mt-1.5 text-[12px] leading-relaxed text-ink-dim">{r.d}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
