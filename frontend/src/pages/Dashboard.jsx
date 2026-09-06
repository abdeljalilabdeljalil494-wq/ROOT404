import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import usePageHeader from '../hooks/usePageHeader'
import useAuthUser from '../hooks/useAuthUser'
import Icon from '../components/ui/Icon'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import Avatar from '../components/ui/Avatar'
import StatCard from '../components/ui/StatCard'
import ProgressBar from '../components/ui/ProgressBar'
import BarChart from '../components/ui/BarChart'
import { dashboardService, projectService } from '../services/api'
import {
  dashboardStats as mockStats,
  recentActivity as mockActivity,
  weeklyActivity as mockWeekly,
  dailyMission,
  upcomingSlots,
  projects as mockProjects,
} from '../data/mock'

const TONE_TEXT = { ok: 'text-ok', danger: 'text-danger', brand: 'text-brand-500', muted: 'text-ink-dim' }
const TONE_DOT = { ok: 'bg-ok', danger: 'bg-danger', brand: 'bg-brand-500', muted: 'bg-ink-faint' }

function Panel({ title, action, children, className = '', icon }) {
  return (
    <section className={`card flex flex-col ${className}`}>
      <header className="flex items-center justify-between gap-3 border-b border-line px-5 py-3.5">
        <h2 className="flex items-center gap-2 text-[13.5px] font-semibold text-ink">
          {icon && <Icon name={icon} size={15} className="text-brand-500" />}
          {title}
        </h2>
        {action}
      </header>
      <div className="flex-1">{children}</div>
    </section>
  )
}

export default function Dashboard() {
  usePageHeader({ title: 'Tableau de bord' })
  const currentUser = useAuthUser()

  // Real data from the FastAPI backend (falls back to mock when offline).
  const [stats, setStats] = useState(mockStats)
  const [activity, setActivity] = useState(mockActivity)
  const [weekly, setWeekly] = useState(mockWeekly)
  const [projects, setProjects] = useState(mockProjects)

  useEffect(() => {
    let alive = true
    Promise.all([
      dashboardService.stats(),
      dashboardService.activity(),
      dashboardService.weekly(),
      projectService.list(),
    ])
      .then(([s, a, w, p]) => {
        if (!alive) return
        if (s?.length) setStats(s)
        if (a?.length) setActivity(a)
        if (w?.length) setWeekly(w)
        if (p?.length) setProjects(p)
      })
      .catch(() => {}) // unauthenticated / offline → keep the mock data below
    return () => {
      alive = false
    }
  }, [])

  const inProgress = projects.filter((p) => p.status === 'progress' || p.status === 'available').slice(0, 3)

  return (
    <div className="container-page space-y-5 py-6">
      {/* ---------- Welcome + level ---------- */}
      <div className="grid gap-5 lg:grid-cols-[1fr_320px]">
        <div className="flex flex-col justify-center">
          <h1 className="text-[26px] font-extrabold tracking-tight text-white sm:text-[30px]">
            Tableau de bord
          </h1>
          <p className="mt-2 text-[15px] font-semibold text-ink">
            Bienvenue, {currentUser.displayName} <span aria-hidden>👋</span>
          </p>
          <p className="mt-1 text-[13px] text-ink-dim">
            Continue là où tu t'es arrêté — il te reste{' '}
            <span className="font-semibold text-brand-500">{currentUser.xpToNext.toLocaleString('fr-FR')} XP</span>{' '}
            avant le niveau 7.00.
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            <Button to="/workspace/minishell" size="sm" icon="Play">Reprendre minishell</Button>
            <Button to="/projects" size="sm" variant="outline" icon="FolderKanban">Mes projets</Button>
            <Button to="/mentor" size="sm" variant="ghost" icon="Sparkles">Assistant IA</Button>
          </div>
        </div>

        {/* Level card */}
        <div className="card relative overflow-hidden p-5">
          <div
            aria-hidden
            className="absolute -right-10 -top-10 h-32 w-32 rounded-full bg-brand-500/15 blur-3xl"
          />
          <div className="relative">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-ink-dim">
                Niveau actuel
              </span>
              <Badge tone="brand">{currentUser.campus}</Badge>
            </div>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="font-mono text-[38px] font-extrabold leading-none text-white">
                {currentUser.level.toFixed(2)}
              </span>
              <span className="text-[12px] text-ink-dim">/ 21.00</span>
            </div>
            <ProgressBar value={currentUser.levelProgress} height={8} className="mt-4" />
            <div className="mt-2.5 flex items-center justify-between text-[11.5px]">
              <span className="text-ink-dim">Prochain niveau : 7.00</span>
              <span className="font-semibold text-brand-500">{currentUser.levelProgress}%</span>
            </div>
          </div>
        </div>
      </div>

      {/* ---------- KPI row ---------- */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {stats.map(({ key, ...s }) => (
          <StatCard key={key} {...s} />
        ))}
      </div>

      {/* ---------- Activity + charts ---------- */}
      <div className="grid gap-5 xl:grid-cols-[1.35fr_1fr]">
        <Panel
          title="Ton activité récente"
          icon="Activity"
          action={
            <Link to="/profile" className="text-[12px] font-medium text-brand-500 hover:underline">
              Tout voir
            </Link>
          }
        >
          <ul className="divide-y divide-line/70">
            {activity.map((a) => (
              <li
                key={a.id}
                className="flex items-center gap-3.5 px-5 py-3.5 transition-colors hover:bg-white/[0.02]"
              >
                <span
                  className={`grid h-9 w-9 shrink-0 place-items-center rounded-full ${
                    a.tone === 'ok' ? 'bg-ok/15 text-ok' : a.tone === 'danger' ? 'bg-danger/15 text-danger' : 'bg-brand-500/15 text-brand-500'
                  }`}
                >
                  <Icon
                    name={a.tone === 'ok' ? 'Check' : a.tone === 'danger' ? 'X' : 'Loader'}
                    size={16}
                  />
                </span>
                <div className="min-w-0 flex-1">
                  <p className="truncate font-mono text-[13px] font-semibold text-ink">{a.project}</p>
                  <p className="truncate text-[11.5px] text-ink-dim">{a.kind}</p>
                </div>
                <div className="flex shrink-0 items-center gap-3">
                  <span className={`text-[13px] font-bold ${TONE_TEXT[a.tone]}`}>{a.score}</span>
                  <span className={`h-2 w-2 rounded-full ${TONE_DOT[a.tone]}`} />
                </div>
                <span className="hidden w-20 shrink-0 text-right text-[11px] text-ink-faint sm:block">
                  {a.time}
                </span>
              </li>
            ))}
          </ul>
        </Panel>

        <div className="space-y-5">
          <Panel title="Activité hebdomadaire" icon="BarChart3" action={<Badge tone="ok">+18%</Badge>}>
            <div className="p-5">
              <BarChart data={weekly} height={140} />
              <p className="mt-4 border-t border-line pt-3 text-[11.5px] text-ink-dim">
                <span className="font-semibold text-ink">17 h 24 min</span> de code cette semaine —
                meilleur jour : mercredi.
              </p>
            </div>
          </Panel>

          {/* Daily mission */}
          <section className="card overflow-hidden">
            <div className="flex items-center gap-2 border-b border-line bg-brand-500/[0.07] px-5 py-3">
              <Icon name="Zap" size={15} className="text-brand-500" />
              <h2 className="text-[13px] font-bold uppercase tracking-wide text-brand-400">
                Daily Mission
              </h2>
              <Badge tone="brand" className="ml-auto">+{dailyMission.reward} XP</Badge>
            </div>
            <div className="p-5">
              <p className="font-mono text-[14px] font-semibold text-ink">{dailyMission.title}</p>
              <p className="mt-1 text-[11.5px] text-ink-dim">{dailyMission.skill}</p>
              <div className="mt-4 flex items-center justify-between">
                <div className="flex items-center gap-1" aria-label={`Difficulté ${dailyMission.difficulty}/5`}>
                  {Array.from({ length: 5 }).map((_, i) => (
                    <Icon
                      key={i}
                      name="Star"
                      size={13}
                      className={i < dailyMission.difficulty ? 'fill-brand-500 text-brand-500' : 'text-ink-faint'}
                    />
                  ))}
                </div>
                <span className="flex items-center gap-1.5 text-[11.5px] text-ink-dim">
                  <Icon name="Clock" size={12} /> {dailyMission.time}
                </span>
              </div>
              <Button size="sm" full className="mt-4" iconRight="ArrowRight">Lancer la mission</Button>
            </div>
          </section>
        </div>
      </div>

      {/* ---------- Continue + slots ---------- */}
      <div className="grid gap-5 xl:grid-cols-[1.35fr_1fr]">
        <Panel
          title="Continuer à coder"
          icon="Code2"
          action={
            <Link to="/projects" className="text-[12px] font-medium text-brand-500 hover:underline">
              Tous les projets
            </Link>
          }
        >
          <div className="grid gap-3 p-5 sm:grid-cols-3">
            {inProgress.map((p) => (
              <Link
                key={p.id}
                to={`/projects/${p.slug}`}
                className="group rounded-lg border border-line bg-root-850 p-4 transition-all hover:-translate-y-0.5 hover:border-brand-500/35"
              >
                <div className="flex items-center justify-between">
                  <span
                    className="rounded px-1.5 py-0.5 text-[10px] font-bold"
                    style={{ background: `${p.langColor}1A`, color: p.langColor }}
                  >
                    {p.lang}
                  </span>
                  <Icon
                    name="ArrowUpRight"
                    size={14}
                    className="text-ink-faint transition-colors group-hover:text-brand-500"
                  />
                </div>
                <p className="mt-3 font-mono text-[13px] font-semibold text-ink">{p.name}</p>
                <p className="mt-0.5 text-[11px] text-ink-dim">{p.level}</p>
                <ProgressBar value={p.progress ?? 0} height={4} className="mt-3" />
                <p className="mt-1.5 text-[10.5px] text-ink-faint">
                  {p.progress != null ? `${p.progress}% complété` : 'Pas encore commencé'}
                </p>
              </Link>
            ))}
          </div>
        </Panel>

        <Panel
          title="Slots de correction"
          icon="CalendarClock"
          action={<Link to="/peer-review" className="text-[12px] font-medium text-brand-500 hover:underline">Gérer</Link>}
        >
          <ul className="divide-y divide-line/70">
            {upcomingSlots.map((s) => (
              <li key={s.id} className="flex items-center gap-3 px-5 py-4">
                <Avatar name={s.peer} size="sm" status="online" />
                <div className="min-w-0 flex-1">
                  <p className="truncate text-[12.5px] font-semibold text-ink">@{s.peer}</p>
                  <p className="truncate font-mono text-[11px] text-ink-dim">{s.project}</p>
                </div>
                <div className="text-right">
                  <Badge tone={s.role === 'Correcteur' ? 'brand' : 'info'}>{s.role}</Badge>
                  <p className="mt-1 text-[10.5px] text-ink-faint">{s.time}</p>
                </div>
              </li>
            ))}
          </ul>
          <div className="border-t border-line p-5">
            <Button variant="outline" size="sm" full icon="Plus">Réserver un slot</Button>
          </div>
        </Panel>
      </div>
    </div>
  )
}
