import usePageHeader from '../hooks/usePageHeader'
import Icon from '../components/ui/Icon'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import Avatar from '../components/ui/Avatar'
import ProgressBar from '../components/ui/ProgressBar'
import { coalitions, currentUser, leaderboard } from '../data/mock'

const WARS = [
  { id: 1, title: 'Coalition War #14 — Algorithmic Rush', ends: '12h 14m 08s', prize: '5 000 pts', teams: 4, live: true },
  { id: 2, title: 'Seasonal Event — CTF Nights', ends: '4 j 06h', prize: '3 200 pts', teams: 4, live: false },
]

export default function Coalitions() {
  usePageHeader({ title: 'Coalitions' })
  const mine = coalitions[0]
  const members = leaderboard.filter((l) => l.coalition === mine.name)

  return (
    <div className="container-page space-y-5 py-6">
      {/* My coalition banner */}
      <section className="card relative overflow-hidden">
        <div
          aria-hidden
          className="absolute inset-0"
          style={{ background: `radial-gradient(700px 220px at 15% 0%, ${mine.color}26, transparent)` }}
        />
        <div className="relative flex flex-col gap-6 p-6 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex items-center gap-5">
            <span
              className="grid h-20 w-20 shrink-0 place-items-center rounded-2xl border"
              style={{ background: `${mine.color}18`, borderColor: `${mine.color}45`, color: mine.color }}
            >
              <Icon name="Flame" size={38} strokeWidth={1.6} />
            </span>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <h1 className="text-[26px] font-extrabold tracking-tight text-white">{mine.name}</h1>
                <Badge tone="brand">Ta coalition</Badge>
              </div>
              <p className="mt-1.5 text-[13px] italic text-ink-dim">« {mine.motto} »</p>
              <div className="mt-3 flex flex-wrap gap-4 text-[12px] text-ink-soft">
                <span className="flex items-center gap-1.5"><Icon name="Users" size={13} className="text-ink-faint" /> {mine.members} membres</span>
                <span className="flex items-center gap-1.5"><Icon name="Trophy" size={13} className="text-ink-faint" /> {mine.wins} Wars gagnées</span>
                <span className="flex items-center gap-1.5"><Icon name="TrendingUp" size={13} className="text-ok" /> {mine.trend} cette semaine</span>
              </div>
            </div>
          </div>

          <div className="text-left lg:text-right">
            <p className="text-[10.5px] font-bold uppercase tracking-wider text-ink-dim">Points de coalition</p>
            <p className="font-mono text-[36px] font-extrabold leading-none" style={{ color: mine.color }}>
              {mine.points.toLocaleString('fr-FR')}
            </p>
            <p className="mt-1.5 text-[12px] text-ink-dim">Rang #{mine.rank} sur {coalitions.length}</p>
            <ProgressBar value={92} color={mine.color} height={5} className="mt-3 lg:w-56" />
            <p className="mt-1.5 text-[11px] text-ink-faint">345 pts avant la 1ʳᵉ place</p>
          </div>
        </div>
      </section>

      <div className="grid gap-5 xl:grid-cols-[1fr_360px]">
        {/* Ranking */}
        <section className="card overflow-hidden">
          <header className="flex items-center justify-between border-b border-line px-5 py-3.5">
            <h2 className="flex items-center gap-2 text-[13.5px] font-semibold text-ink">
              <Icon name="Flag" size={15} className="text-brand-500" /> Classement des coalitions
            </h2>
            <Badge tone="muted">Semaine 36</Badge>
          </header>
          <ul className="divide-y divide-line/70">
            {coalitions.map((c, i) => (
              <li
                key={c.id}
                className={`flex items-center gap-4 px-5 py-4 transition-colors ${
                  c.name === mine.name ? 'bg-brand-500/[0.06]' : 'hover:bg-white/[0.02]'
                }`}
              >
                <span className="w-6 font-mono text-[13px] font-bold text-ink-dim">{i + 1}</span>
                <span className="grid h-10 w-10 shrink-0 place-items-center rounded-lg" style={{ background: `${c.color}1A`, color: c.color }}>
                  <Icon name="Flag" size={17} />
                </span>
                <div className="min-w-0 flex-1">
                  <p className="text-[13.5px] font-semibold text-ink">{c.name}</p>
                  <ProgressBar value={(c.points / coalitions[0].points) * 100} color={c.color} height={4} className="mt-2 max-w-[240px]" />
                </div>
                <div className="text-right">
                  <p className="font-mono text-[14px] font-bold" style={{ color: c.color }}>{c.points.toLocaleString('fr-FR')}</p>
                  <p className="text-[10.5px] text-ok">{c.trend}</p>
                </div>
              </li>
            ))}
          </ul>
        </section>

        <div className="space-y-5">
          {/* Wars */}
          <section className="card overflow-hidden">
            <header className="flex items-center gap-2 border-b border-line px-5 py-3.5">
              <Icon name="Swords" size={15} className="text-brand-500" />
              <h2 className="text-[13.5px] font-semibold text-ink">Coalition Wars</h2>
            </header>
            <ul className="divide-y divide-line/70">
              {WARS.map((w) => (
                <li key={w.id} className="p-5">
                  <div className="flex items-start justify-between gap-3">
                    <p className="text-[13px] font-semibold text-ink">{w.title}</p>
                    {w.live && <Badge tone="danger" dot>Live</Badge>}
                  </div>
                  <div className="mt-3 grid grid-cols-3 gap-2 text-center">
                    {[
                      { l: 'Fin dans', v: w.ends },
                      { l: 'Prix', v: w.prize },
                      { l: 'Équipes', v: w.teams },
                    ].map((s) => (
                      <div key={s.l} className="rounded-lg border border-line bg-root-850 py-2.5">
                        <p className="text-[9.5px] uppercase tracking-wider text-ink-faint">{s.l}</p>
                        <p className="mt-1 font-mono text-[11.5px] font-bold text-ink">{s.v}</p>
                      </div>
                    ))}
                  </div>
                  <Button size="sm" full className="mt-3.5" variant={w.live ? 'primary' : 'outline'}>
                    {w.live ? 'Rejoindre la War' : 'S’inscrire'}
                  </Button>
                </li>
              ))}
            </ul>
          </section>

          {/* Top members */}
          <section className="card overflow-hidden">
            <header className="flex items-center gap-2 border-b border-line px-5 py-3.5">
              <Icon name="Users" size={15} className="text-brand-500" />
              <h2 className="text-[13.5px] font-semibold text-ink">Meilleurs contributeurs</h2>
            </header>
            <ul className="divide-y divide-line/70">
              {members.map((m, i) => (
                <li key={m.user} className={`flex items-center gap-3 px-5 py-3 ${m.user === currentUser.username ? 'bg-brand-500/[0.06]' : ''}`}>
                  <span className="w-4 font-mono text-[12px] text-ink-faint">{i + 1}</span>
                  <Avatar src={m.avatar} name={m.name} size="xs" />
                  <span className="min-w-0 flex-1 truncate text-[12.5px] text-ink-soft">@{m.user}</span>
                  <span className="font-mono text-[12px] font-bold text-brand-500">{m.xp}</span>
                </li>
              ))}
            </ul>
          </section>
        </div>
      </div>
    </div>
  )
}
