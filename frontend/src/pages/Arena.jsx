import { useEffect, useState } from 'react'
import usePageHeader from '../hooks/usePageHeader'
import Icon from '../components/ui/Icon'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import Avatar from '../components/ui/Avatar'
import ProgressBar from '../components/ui/ProgressBar'
import { arenaModes, arenaLive, leaderboard } from '../data/mock'

function Countdown({ from = 900 }) {
  const [s, setS] = useState(from)
  useEffect(() => {
    const id = setInterval(() => setS((v) => (v > 0 ? v - 1 : 0)), 1000)
    return () => clearInterval(id)
  }, [])
  const m = String(Math.floor(s / 60)).padStart(2, '0')
  const sec = String(s % 60).padStart(2, '0')
  return <span className="font-mono tabular-nums">{m}:{sec}</span>
}

export default function Arena() {
  usePageHeader({ title: 'ROOT Arena' })
  const [mode, setMode] = useState('1v1')

  return (
    <div className="container-page space-y-5 py-6">
      {/* Hero */}
      <section className="card relative overflow-hidden">
        <div aria-hidden className="absolute inset-0 bg-gradient-to-br from-danger/[0.12] via-transparent to-brand-500/[0.12]" />
        <div aria-hidden className="absolute inset-0 bg-grid opacity-30" />
        <div className="relative flex flex-col items-start gap-6 p-6 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div className="flex items-center gap-2.5">
              <span className="grid h-11 w-11 place-items-center rounded-xl bg-danger/15 text-danger">
                <Icon name="Swords" size={22} />
              </span>
              <h1 className="text-[26px] font-extrabold tracking-tight text-white">ROOT Arena</h1>
              <Badge tone="danger" dot>3 duels en direct</Badge>
            </div>
            <p className="mt-3 max-w-xl text-[13px] leading-relaxed text-ink-soft">
              Compétition pure, chronomètre en main. Classement séparé du cursus académique — ici,
              seule la vitesse et l'élégance de la solution comptent.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button icon="Zap">Trouver un adversaire</Button>
            <Button variant="outline" icon="Eye">Regarder un duel</Button>
          </div>
        </div>
      </section>

      {/* Modes */}
      <section>
        <h2 className="mb-3.5 text-[15px] font-bold text-ink">Modes de jeu</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
          {arenaModes.map((m) => {
            const on = mode === m.key
            return (
              <button
                key={m.key}
                onClick={() => setMode(m.key)}
                className={`card flex flex-col p-5 text-left transition-all hover:-translate-y-1 ${
                  on ? 'border-brand-500/50 shadow-glow' : 'hover:border-line-strong'
                }`}
              >
                <span className={`grid h-10 w-10 place-items-center rounded-lg ${on ? 'bg-brand-500 text-[#160A00]' : 'bg-brand-500/12 text-brand-500'}`}>
                  <Icon name={m.icon} size={19} />
                </span>
                <h3 className="mt-3.5 text-[13.5px] font-bold text-ink">{m.name}</h3>
                <p className="mt-1.5 flex-1 text-[11.5px] leading-relaxed text-ink-dim">{m.desc}</p>
                <div className="mt-4 flex items-center gap-3 border-t border-line pt-3 text-[11px] text-ink-dim">
                  <span className="flex items-center gap-1.5"><Icon name="Users" size={12} /> {m.players}</span>
                  <span className="flex items-center gap-1.5"><Icon name="Timer" size={12} /> {m.time}</span>
                </div>
              </button>
            )
          })}
        </div>
      </section>

      <div className="grid gap-5 xl:grid-cols-[1.3fr_1fr]">
        {/* Live battles */}
        <section className="card overflow-hidden">
          <header className="flex items-center justify-between border-b border-line px-5 py-3.5">
            <h2 className="flex items-center gap-2 text-[13.5px] font-semibold text-ink">
              <Icon name="Radio" size={15} className="text-danger" /> Duels en direct
            </h2>
            <Badge tone="danger" dot>Live</Badge>
          </header>
          <ul className="divide-y divide-line/70">
            {arenaLive.map((b) => (
              <li key={b.id} className="p-5">
                <div className="flex items-center justify-between gap-4">
                  <div className="flex min-w-0 flex-1 items-center gap-3">
                    <Avatar name={b.a} src={`https://i.pravatar.cc/64?img=${30 + b.id}`} size="sm" />
                    <span className="truncate text-[12.5px] font-semibold text-ink">@{b.a}</span>
                  </div>
                  <span className="shrink-0 font-mono text-[11px] font-bold text-brand-500">VS</span>
                  <div className="flex min-w-0 flex-1 items-center justify-end gap-3">
                    <span className="truncate text-[12.5px] font-semibold text-ink">@{b.b}</span>
                    <Avatar name={b.b} src={`https://i.pravatar.cc/64?img=${40 + b.id}`} size="sm" />
                  </div>
                </div>
                <div className="mt-3.5 flex flex-wrap items-center justify-between gap-3 rounded-lg border border-line bg-root-850 px-3.5 py-2.5">
                  <span className="font-mono text-[12px] text-ink-soft">{b.problem}</span>
                  <div className="flex items-center gap-4 text-[11.5px] text-ink-dim">
                    <span className="flex items-center gap-1.5"><Icon name="Eye" size={12} /> {b.viewers}</span>
                    <span className="flex items-center gap-1.5 text-danger">
                      <Icon name="Timer" size={12} /> <Countdown from={parseInt(b.time) * 60} />
                    </span>
                    <Button size="sm" variant="ghost" iconRight="ArrowRight">Voir</Button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </section>

        {/* Arena ranking */}
        <section className="card overflow-hidden">
          <header className="flex items-center justify-between border-b border-line px-5 py-3.5">
            <h2 className="flex items-center gap-2 text-[13.5px] font-semibold text-ink">
              <Icon name="Trophy" size={15} className="text-warn" /> Arena Leaderboard
            </h2>
            <Badge tone="muted">Saison 3</Badge>
          </header>
          <ul className="divide-y divide-line/70">
            {leaderboard.slice(0, 6).map((u, i) => (
              <li key={u.user} className={`flex items-center gap-3 px-5 py-3 ${u.me ? 'bg-brand-500/[0.07]' : ''}`}>
                <span className="w-5 font-mono text-[12px] font-bold text-ink-dim">{i + 1}</span>
                <Avatar src={u.avatar} name={u.name} size="xs" ring={u.me} />
                <span className="min-w-0 flex-1 truncate text-[12.5px] text-ink-soft">@{u.user}</span>
                <div className="hidden w-20 sm:block">
                  <ProgressBar value={u.accuracy} height={4} />
                </div>
                <span className="w-14 text-right font-mono text-[12.5px] font-bold text-brand-500">
                  {(2400 - i * 137).toLocaleString('fr-FR')}
                </span>
              </li>
            ))}
          </ul>
          <div className="border-t border-line p-4">
            <Button variant="outline" size="sm" full iconRight="ArrowRight">Classement Arena complet</Button>
          </div>
        </section>
      </div>
    </div>
  )
}
