import { useEffect } from 'react'
import { Link, useParams } from 'react-router-dom'
import Logo from '../components/Logo'
import Icon from '../components/ui/Icon'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import Avatar from '../components/ui/Avatar'
import ProgressBar from '../components/ui/ProgressBar'
import Heatmap from '../components/ui/Heatmap'
import { currentUser, projects, badges, skillGraph, reputation } from '../data/mock'

const TIER = { gold: '#FFC53D', silver: '#C9D1D9', bronze: '#D08A4E' }

export default function Portfolio() {
  const { username = currentUser.username } = useParams()

  useEffect(() => {
    document.title = `${username} — Portfolio ROOT 404`
  }, [username])

  const top = skillGraph.map((g) => ({
    name: g.group,
    color: g.color,
    value: Math.round(g.skills.reduce((a, s) => a + s.value, 0) / g.skills.length),
  }))

  return (
    <div className="min-h-screen bg-root-900">
      {/* Minimal public header */}
      <header className="sticky top-0 z-40 border-b border-line bg-root-950/90 backdrop-blur-xl">
        <div className="container-page flex h-[60px] items-center justify-between">
          <Logo size={30} />
          <div className="flex items-center gap-2">
            <Badge tone="ok" dot className="hidden sm:inline-flex">Profil vérifié</Badge>
            <Button to="/register" size="sm">Rejoindre ROOT 404</Button>
          </div>
        </div>
      </header>

      <div className="container-page max-w-[1000px] space-y-5 py-8">
        {/* Identity */}
        <section className="card relative overflow-hidden p-6 sm:p-8">
          <div aria-hidden className="absolute inset-0 bg-gradient-to-br from-brand-500/[0.1] to-transparent" />
          <div aria-hidden className="absolute inset-0 bg-grid opacity-30" />
          <div className="relative flex flex-col items-center gap-6 text-center sm:flex-row sm:text-left">
            <Avatar src={currentUser.avatar} name={currentUser.fullName} size="xl" ring />
            <div className="min-w-0 flex-1">
              <h1 className="text-[26px] font-extrabold tracking-tight text-white">{currentUser.fullName}</h1>
              <p className="mt-1 font-mono text-[13px] text-brand-500">root404.tn/u/{username}</p>
              <p className="mt-3 max-w-lg text-[13px] leading-relaxed text-ink-soft">{currentUser.bio}</p>
              <div className="mt-4 flex flex-wrap justify-center gap-2 sm:justify-start">
                <span className="chip"><Icon name="MapPin" size={11} /> {currentUser.campus}, Tunisie</span>
                <span className="chip"><Icon name="Flame" size={11} className="text-brand-500" /> {currentUser.coalition.name}</span>
                <span className="chip"><Icon name="CalendarDays" size={11} /> Depuis {currentUser.joined}</span>
              </div>
            </div>
            <div className="shrink-0 rounded-xl border border-brand-500/25 bg-brand-500/[0.07] px-7 py-5 text-center">
              <p className="text-[10px] font-bold uppercase tracking-widest text-ink-dim">Level</p>
              <p className="font-mono text-[34px] font-extrabold leading-none text-brand-500">
                {currentUser.level.toFixed(2)}
              </p>
              <p className="mt-1 text-[10.5px] text-ink-dim">/ 21.00</p>
            </div>
          </div>
        </section>

        {/* Key figures */}
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          {[
            { l: 'XP total', v: currentUser.xp.toLocaleString('fr-FR'), i: 'Zap' },
            { l: 'Projets validés', v: currentUser.projectsDone, i: 'CheckCircle2' },
            { l: 'Peer reviews', v: '47', i: 'Users' },
            { l: 'Streak record', v: `${currentUser.streak} j`, i: 'Flame' },
          ].map((s) => (
            <div key={s.l} className="card p-4 text-center">
              <Icon name={s.i} size={17} className="mx-auto text-brand-500" />
              <p className="mt-2 font-mono text-[19px] font-extrabold text-ink">{s.v}</p>
              <p className="mt-0.5 text-[10.5px] uppercase tracking-wider text-ink-dim">{s.l}</p>
            </div>
          ))}
        </div>

        {/* Skills */}
        <section className="card p-6">
          <h2 className="flex items-center gap-2 text-[15px] font-bold text-ink">
            <Icon name="Network" size={16} className="text-brand-500" /> Compétences vérifiées
          </h2>
          <p className="mt-1.5 text-[12px] text-ink-dim">
            Calculées à partir de soumissions réelles — jamais déclarées manuellement.
          </p>
          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            {top.map((s) => (
              <div key={s.name}>
                <div className="mb-1.5 flex items-center justify-between text-[12.5px]">
                  <span className="font-medium text-ink">{s.name}</span>
                  <span className="font-mono font-semibold" style={{ color: s.color }}>{s.value}%</span>
                </div>
                <ProgressBar value={s.value} color={s.color} height={7} />
              </div>
            ))}
          </div>
        </section>

        {/* Projects */}
        <section className="card p-6">
          <h2 className="flex items-center gap-2 text-[15px] font-bold text-ink">
            <Icon name="FolderKanban" size={16} className="text-brand-500" /> Projets réalisés
          </h2>
          <ul className="mt-5 grid gap-3 sm:grid-cols-2">
            {projects.filter((p) => p.status === 'done').map((p) => (
              <li key={p.id} className="flex items-center gap-3.5 rounded-lg border border-line bg-root-850 p-4">
                <span
                  className="grid h-10 w-10 shrink-0 place-items-center rounded-lg font-mono text-[12px] font-bold"
                  style={{ background: `${p.langColor}18`, color: p.langColor }}
                >
                  {p.name.slice(0, 2)}
                </span>
                <div className="min-w-0 flex-1">
                  <p className="truncate font-mono text-[13px] font-semibold text-ink">{p.name}</p>
                  <p className="truncate text-[11px] text-ink-dim">{p.level} · {p.lang}</p>
                </div>
                <span className="shrink-0 font-mono text-[13px] font-bold text-ok">{p.score}%</span>
              </li>
            ))}
          </ul>
        </section>

        {/* Badges + reputation */}
        <div className="grid gap-5 lg:grid-cols-[1.2fr_1fr]">
          <section className="card p-6">
            <h2 className="flex items-center gap-2 text-[15px] font-bold text-ink">
              <Icon name="Award" size={16} className="text-brand-500" /> Achievements
            </h2>
            <ul className="mt-5 grid grid-cols-2 gap-2.5 sm:grid-cols-4">
              {badges.map((b) => (
                <li key={b.name} className="flex flex-col items-center rounded-lg border border-line bg-root-850 p-3.5 text-center">
                  <Icon name={b.icon} size={19} style={{ color: TIER[b.tier] }} />
                  <p className="mt-2 text-[10.5px] font-medium leading-tight text-ink-soft">{b.name}</p>
                </li>
              ))}
            </ul>
          </section>

          <section className="card p-6">
            <h2 className="flex items-center gap-2 text-[15px] font-bold text-ink">
              <Icon name="ShieldCheck" size={16} className="text-ok" /> Réputation
            </h2>
            <ul className="mt-5 space-y-3.5">
              {reputation.map((r) => (
                <li key={r.label}>
                  <ProgressBar value={r.value} showLabel label={r.label} height={5} color="#2ECC71" />
                </li>
              ))}
            </ul>
          </section>
        </div>

        {/* Activity */}
        <section className="card p-6">
          <h2 className="flex items-center gap-2 text-[15px] font-bold text-ink">
            <Icon name="Activity" size={16} className="text-brand-500" /> Activité
          </h2>
          <Heatmap className="mt-5" />
        </section>

        {/* Contact */}
        <section className="card flex flex-col items-center gap-4 p-8 text-center sm:flex-row sm:justify-between sm:text-left">
          <div>
            <h2 className="text-[15px] font-bold text-ink">Ce profil est vérifié par ROOT 404</h2>
            <p className="mt-1.5 text-[12.5px] text-ink-dim">
              Chaque donnée provient de soumissions exécutées dans un sandbox contrôlé.
            </p>
          </div>
          <div className="flex shrink-0 gap-2">
            <Button variant="outline" size="sm" icon="Mail">Contacter</Button>
            <Button size="sm" icon="Share2">Partager</Button>
          </div>
        </section>

        <p className="pb-4 text-center text-[11.5px] text-ink-faint">
          Généré automatiquement par{' '}
          <Link to="/" className="text-brand-500 hover:underline">ROOT 404 — Elite Coder Platform</Link>
        </p>
      </div>
    </div>
  )
}
