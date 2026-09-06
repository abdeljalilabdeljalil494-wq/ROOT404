import { useEffect } from 'react'
import Icon from '../components/ui/Icon'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import Avatar from '../components/ui/Avatar'
import SectionHeading from '../components/ui/SectionHeading'
import { coalitions, leaderboard, rooms, roomTypes } from '../data/mock'

const EVENTS = [
  { d: '12', m: 'Sept.', t: 'Coalition War #15 — Algorithmic Rush', l: 'En ligne · 48 h', tag: 'Compétition', tone: 'danger' },
  { d: '19', m: 'Sept.', t: 'Meetup Tunis — Systèmes & bas niveau', l: 'Lac 2, Tunis · 18h30', tag: 'Meetup', tone: 'brand' },
  { d: '27', m: 'Sept.', t: 'Partner Fair — 12 entreprises présentes', l: 'Campus Tunis · 10h', tag: 'Emploi', tone: 'info' },
  { d: '04', m: 'Oct.', t: 'Ouverture Piscine — Session automne', l: 'Trois campus · 08h', tag: 'Piscine', tone: 'ok' },
]

const CHANNELS = [
  { n: 'général', d: 'Le salon principal, tout y passe.', m: '12.4k' },
  { n: 'aide-c', d: 'Segfaults, pointeurs et compassion.', m: '8.1k' },
  { n: 'peer-review', d: 'Trouver un correcteur en urgence.', m: '5.7k' },
  { n: 'offres-emploi', d: 'Stages et postes des partenaires.', m: '2.3k' },
]

export default function Community() {
  useEffect(() => { document.title = 'Communauté — ROOT 404' }, [])

  return (
    <>
      <section className="relative overflow-hidden border-b border-line bg-root-950 py-20">
        <div aria-hidden className="absolute inset-0 bg-dots opacity-50" />
        <div className="container-page relative text-center">
          <SectionHeading
            eyebrow="Communauté"
            title="Personne ne code"
            highlight="seul ici"
            text="12 487 codeurs, 42 coalitions, trois campus et un Discord qui ne dort jamais. La communauté est le vrai moteur de la plateforme."
            className="mx-auto"
          />
          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <Button size="lg" icon="MessageCircle">Rejoindre le Discord</Button>
            <Button to="/rooms" variant="outline" size="lg" icon="Video">Voir les rooms actives</Button>
          </div>
        </div>
      </section>

      {/* Coalitions */}
      <section className="border-b border-line bg-root-900 py-20">
        <div className="container-page">
          <SectionHeading align="left" eyebrow="Coalitions" title="Choisis ton" highlight="camp" text="Chaque étudiant rejoint une coalition. Les points de tous les membres s'additionnent dans un classement hebdomadaire séparé." />
          <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {coalitions.map((c) => (
              <article key={c.id} className="card relative overflow-hidden p-6 text-center transition-transform hover:-translate-y-1">
                <div aria-hidden className="absolute inset-x-0 top-0 h-1" style={{ background: c.color }} />
                <span className="mx-auto grid h-14 w-14 place-items-center rounded-xl" style={{ background: `${c.color}18`, color: c.color }}>
                  <Icon name="Flag" size={26} />
                </span>
                <h3 className="mt-4 text-[15px] font-bold text-white">{c.name}</h3>
                <p className="mt-1.5 text-[11.5px] italic text-ink-dim">« {c.motto} »</p>
                <p className="mt-4 font-mono text-[22px] font-extrabold" style={{ color: c.color }}>
                  {c.points.toLocaleString('fr-FR')}
                </p>
                <p className="text-[11px] text-ink-dim">{c.members} membres · {c.wins} Wars</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* Events */}
      <section className="border-b border-line bg-root-950 py-20">
        <div className="container-page grid gap-10 lg:grid-cols-[1.2fr_1fr]">
          <div>
            <SectionHeading align="left" eyebrow="Agenda" title="Prochains" highlight="événements" />
            <ul className="mt-8 space-y-3">
              {EVENTS.map((e) => (
                <li key={e.t} className="card flex items-center gap-4 p-4 transition-colors hover:border-line-strong">
                  <div className="grid h-14 w-14 shrink-0 place-items-center rounded-lg border border-line bg-root-850">
                    <span className="font-mono text-[17px] font-extrabold leading-none text-brand-500">{e.d}</span>
                    <span className="text-[9.5px] uppercase tracking-wider text-ink-dim">{e.m}</span>
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-[13.5px] font-semibold text-ink">{e.t}</p>
                    <p className="mt-0.5 text-[11.5px] text-ink-dim">{e.l}</p>
                  </div>
                  <Badge tone={e.tone}>{e.tag}</Badge>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <SectionHeading align="left" eyebrow="Discord" title="Les salons" highlight="les plus actifs" />
            <ul className="mt-8 space-y-2.5">
              {CHANNELS.map((c) => (
                <li key={c.n} className="card flex items-center gap-3.5 p-4">
                  <span className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-brand-500/10 font-mono text-[15px] font-bold text-brand-500">#</span>
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-mono text-[13px] font-semibold text-ink">{c.n}</p>
                    <p className="truncate text-[11.5px] text-ink-dim">{c.d}</p>
                  </div>
                  <span className="shrink-0 text-[11.5px] text-ink-faint">{c.m}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      {/* Live rooms */}
      <section className="border-b border-line bg-root-900 py-20">
        <div className="container-page">
          <SectionHeading eyebrow="En direct" title="Ce qui se passe" highlight="maintenant" />
          <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {rooms.filter((r) => r.live).slice(0, 3).map((r) => {
              const t = roomTypes.find((x) => x.key === r.type)
              return (
                <article key={r.id} className="card p-5">
                  <div className="flex items-center justify-between">
                    <span className="grid h-9 w-9 place-items-center rounded-lg" style={{ background: `${t.color}18`, color: t.color }}>
                      <Icon name={t.icon} size={17} />
                    </span>
                    <Badge tone="danger" dot>Live</Badge>
                  </div>
                  <h3 className="mt-3.5 text-[14px] font-bold text-white">{r.name}</h3>
                  <p className="mt-1 font-mono text-[11.5px] text-ink-dim">{r.project}</p>
                  <div className="mt-4 flex items-center justify-between border-t border-line pt-3.5">
                    <span className="text-[11.5px] text-ink-dim">{r.members} participants</span>
                    <Button to="/rooms" size="sm" variant="ghost" iconRight="ArrowRight">Voir</Button>
                  </div>
                </article>
              )
            })}
          </div>
        </div>
      </section>

      {/* Top helpers */}
      <section className="bg-root-950 py-20">
        <div className="container-page">
          <SectionHeading eyebrow="Merci à eux" title="Les codeurs qui" highlight="aident le plus" />
          <ul className="mx-auto mt-12 grid max-w-3xl gap-3">
            {leaderboard.slice(0, 5).map((u, i) => (
              <li key={u.user} className="card flex items-center gap-4 p-4">
                <span className="w-6 font-mono text-[15px] font-extrabold text-ink-faint">{i + 1}</span>
                <Avatar src={u.avatar} name={u.name} size="md" />
                <div className="min-w-0 flex-1">
                  <p className="truncate text-[13.5px] font-semibold text-ink">@{u.user}</p>
                  <p className="truncate text-[11.5px] text-ink-dim">{u.coalition} · Niveau {u.level.toFixed(2)}</p>
                </div>
                <div className="text-right">
                  <p className="font-mono text-[14px] font-bold text-brand-500">{(94 - i * 9)}</p>
                  <p className="text-[10.5px] text-ink-faint">corrections</p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </section>
    </>
  )
}
