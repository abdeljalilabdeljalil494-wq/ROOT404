import usePageHeader from '../hooks/usePageHeader'
import Icon from '../components/ui/Icon'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import ProgressBar from '../components/ui/ProgressBar'
import BarChart from '../components/ui/BarChart'
import Heatmap from '../components/ui/Heatmap'
import { analytics, weeklyActivity, currentUser } from '../data/mock'

function Metric({ label, value, suffix = '%', color = '#F8851F', hint }) {
  return (
    <div className="card p-5">
      <p className="text-[11px] font-semibold uppercase tracking-wider text-ink-dim">{label}</p>
      <p className="mt-2 font-mono text-[30px] font-extrabold leading-none" style={{ color }}>
        {value}
        <span className="text-[15px] text-ink-dim">{suffix}</span>
      </p>
      <ProgressBar value={value} color={color} height={6} className="mt-3.5" />
      {hint && <p className="mt-2.5 text-[11.5px] text-ink-dim">{hint}</p>}
    </div>
  )
}

export default function Analytics() {
  usePageHeader({ title: 'Analytics 360°' })

  const maxTime = Math.max(...analytics.timeToSolve.flatMap((t) => [t.you, t.avg]))

  return (
    <div className="container-page space-y-5 py-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-[24px] font-extrabold tracking-tight text-white">Student Analytics 360°</h1>
          <p className="mt-1.5 text-[13px] text-ink-dim">
            Event tracking + learning metrics · rapport hebdomadaire envoyé chaque lundi
          </p>
        </div>
        <div className="flex gap-2">
          <select className="select w-auto"><option>30 derniers jours</option><option>90 jours</option><option>Depuis le début</option></select>
          <Button variant="outline" size="sm" icon="Download">Rapport PDF</Button>
        </div>
      </div>

      {/* Top metrics */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Metric label="Learning Velocity" value={analytics.velocity} hint="+6 pts vs. le mois dernier" />
        <Metric label="Consistency" value={analytics.consistency} color="#2ECC71" hint={`${currentUser.streak} jours de streak actif`} />
        <Metric label="Précision Moulinette" value={currentUser.accuracy} color="#3B9EFF" hint="Moyenne du campus : 76 %" />
        <Metric label="Integrity Score" value={currentUser.integrity} color="#B37BFF" hint="Dépendance IA : faible" />
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.3fr_1fr]">
        {/* Time to solve */}
        <section className="card p-5">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h2 className="flex items-center gap-2 text-[13.5px] font-semibold text-ink">
              <Icon name="Timer" size={15} className="text-brand-500" /> Time-to-Solve par domaine
            </h2>
            <div className="flex items-center gap-3 text-[11px] text-ink-dim">
              <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-sm bg-brand-500" /> Toi</span>
              <span className="flex items-center gap-1.5"><span className="h-2 w-2 rounded-sm bg-white/20" /> Moyenne</span>
            </div>
          </div>

          <ul className="mt-5 space-y-4">
            {analytics.timeToSolve.map((t) => (
              <li key={t.label}>
                <div className="mb-2 flex items-center justify-between text-[12px]">
                  <span className="text-ink-soft">{t.label}</span>
                  <span className="font-mono text-ink-dim">
                    <span className={t.you > t.avg ? 'text-danger' : 'text-ok'}>{t.you} j</span> / {t.avg} j
                  </span>
                </div>
                <div className="space-y-1">
                  <div className="h-2.5 w-full overflow-hidden rounded-full bg-white/[0.05]">
                    <div
                      className="h-full rounded-full bg-brand-500 transition-[width] duration-700"
                      style={{ width: `${(t.you / maxTime) * 100}%` }}
                    />
                  </div>
                  <div className="h-1.5 w-full overflow-hidden rounded-full bg-white/[0.03]">
                    <div className="h-full rounded-full bg-white/20" style={{ width: `${(t.avg / maxTime) * 100}%` }} />
                  </div>
                </div>
              </li>
            ))}
          </ul>

          <div className="mt-5 rounded-lg border border-brand-500/25 bg-brand-500/[0.07] p-4">
            <p className="flex gap-2.5 text-[12.5px] leading-relaxed text-ink-soft">
              <Icon name="Sparkles" size={15} className="mt-0.5 shrink-0 text-brand-500" />
              <span><span className="font-semibold text-ink">Lecture IA — </span>{analytics.insight}</span>
            </p>
          </div>
        </section>

        <div className="space-y-5">
          <section className="card p-5">
            <h2 className="flex items-center gap-2 text-[13.5px] font-semibold text-ink">
              <Icon name="Gauge" size={15} className="text-brand-500" /> Tolérance à la difficulté
            </h2>
            <ul className="mt-4 space-y-3.5">
              {analytics.tolerance.map((t) => (
                <li key={t.label}>
                  <ProgressBar
                    value={t.value}
                    showLabel
                    label={t.label}
                    height={7}
                    color={t.value > 80 ? '#2ECC71' : t.value > 50 ? '#F8851F' : '#E5484D'}
                  />
                </li>
              ))}
            </ul>
          </section>

          <section className="card p-5">
            <div className="flex items-center justify-between">
              <h2 className="flex items-center gap-2 text-[13.5px] font-semibold text-ink">
                <Icon name="CalendarCheck" size={15} className="text-brand-500" /> Completion Forecast
              </h2>
              <Badge tone="ok">Dans les temps</Badge>
            </div>
            <p className="mt-4 font-mono text-[22px] font-extrabold text-white">{analytics.forecast}</p>
            <p className="mt-1.5 text-[12px] text-ink-dim">
              Estimation de fin du cursus au rythme actuel ({analytics.velocity} % de vélocité).
            </p>
            <div className="mt-4 space-y-2.5 border-t border-line pt-4 text-[11.5px]">
              {[
                { l: 'Black Hole', v: `${currentUser.blackHole.daysLeft} jours restants`, t: 'text-ok' },
                { l: 'Rythme requis', v: '1,4 projet / mois', t: 'text-ink-soft' },
                { l: 'Rythme actuel', v: '1,9 projet / mois', t: 'text-ok' },
              ].map((r) => (
                <div key={r.l} className="flex items-center justify-between">
                  <span className="text-ink-dim">{r.l}</span>
                  <span className={`font-medium ${r.t}`}>{r.v}</span>
                </div>
              ))}
            </div>
          </section>
        </div>
      </div>

      <div className="grid gap-5 xl:grid-cols-[1fr_1fr]">
        <section className="card p-5">
          <h2 className="flex items-center gap-2 text-[13.5px] font-semibold text-ink">
            <Icon name="BarChart3" size={15} className="text-brand-500" /> Heures de code par jour
          </h2>
          <div className="mt-5"><BarChart data={weeklyActivity} height={160} /></div>
        </section>

        <section className="card p-5">
          <h2 className="flex items-center gap-2 text-[13.5px] font-semibold text-ink">
            <Icon name="Activity" size={15} className="text-brand-500" /> Activity Heatmap
          </h2>
          <Heatmap className="mt-5" />
        </section>
      </div>

      {/* Anti-burnout */}
      <section className="card overflow-hidden">
        <header className="flex items-center gap-2 border-b border-line bg-warn/[0.06] px-5 py-3.5">
          <Icon name="Flame" size={15} className="text-warn" />
          <h2 className="text-[13.5px] font-semibold text-ink">Streak & Anti-Burnout Engine</h2>
          <Badge tone="warn" className="ml-auto">Charge élevée détectée</Badge>
        </header>
        <div className="grid gap-5 p-5 lg:grid-cols-[1fr_320px]">
          <div>
            <p className="text-[13px] leading-relaxed text-ink-soft">
              Tu as codé <span className="font-semibold text-ink">17 h 24 min</span> cette semaine, dont
              <span className="font-semibold text-ink"> 6 h 12 min</span> après minuit. Le moteur détecte un
              schéma de fatigue : ton temps de résolution a augmenté de 22 % sur les trois dernières sessions.
            </p>
            <div className="mt-4 grid gap-2.5 sm:grid-cols-3">
              {[
                { l: 'Sessions > 4 h', v: '5', t: 'text-warn' },
                { l: 'Nuits blanches', v: '2', t: 'text-danger' },
                { l: 'Jours de repos', v: '0', t: 'text-danger' },
              ].map((s) => (
                <div key={s.l} className="rounded-lg border border-line bg-root-850 p-3.5 text-center">
                  <p className={`font-mono text-[20px] font-extrabold ${s.t}`}>{s.v}</p>
                  <p className="mt-1 text-[10.5px] text-ink-dim">{s.l}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-lg border border-brand-500/25 bg-brand-500/[0.07] p-4">
            <p className="text-[11px] font-bold uppercase tracking-wider text-brand-400">
              Plan allégé recommandé
            </p>
            <ul className="mt-3 space-y-2.5 text-[12.5px] text-ink-soft">
              {[
                { t: '20 min', d: 'Pointer Challenge' },
                { t: '10 min', d: 'Peer review courte' },
                { t: '—', d: 'Puis repos jusqu’à demain' },
              ].map((r) => (
                <li key={r.d} className="flex items-center gap-3">
                  <span className="w-14 shrink-0 font-mono text-[11px] text-brand-500">{r.t}</span>
                  <span>{r.d}</span>
                </li>
              ))}
            </ul>
            <Button size="sm" full className="mt-4">Appliquer ce plan</Button>
          </div>
        </div>
      </section>
    </div>
  )
}
