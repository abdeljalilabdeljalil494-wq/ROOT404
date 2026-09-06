import { useState } from 'react'
import usePageHeader from '../hooks/usePageHeader'
import Icon from '../components/ui/Icon'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import Tabs from '../components/ui/Tabs'
import Avatar from '../components/ui/Avatar'
import ProgressBar from '../components/ui/ProgressBar'
import EmptyState from '../components/ui/EmptyState'
import { currentUser } from '../data/mock'

const REQUESTS = [
  { id: 1, peer: 'nour_dev', avatar: 'https://i.pravatar.cc/64?img=32', level: 5.88, project: 'minishell', when: 'Aujourd’hui 16:30', role: 'Tu es corrigé', match: 94, lang: 'FR / AR' },
  { id: 2, peer: 'skhalifa', avatar: 'https://i.pravatar.cc/64?img=26', level: 6.02, project: 'ft_printf', when: 'Demain 10:00', role: 'Tu corriges', match: 88, lang: 'FR' },
]

const AVAILABLE = [
  { id: 3, peer: 'mehdi42', avatar: 'https://i.pravatar.cc/64?img=33', level: 9.94, project: 'philosophers', when: 'Aujourd’hui 18:00', match: 91, lang: 'FR / EN', rep: 93 },
  { id: 4, peer: 'ines_dev', avatar: 'https://i.pravatar.cc/64?img=47', level: 6.36, project: 'minishell', when: 'Demain 09:30', match: 86, lang: 'AR / FR', rep: 88 },
  { id: 5, peer: 'oussama_c', avatar: 'https://i.pravatar.cc/64?img=53', level: 5.41, project: 'get_next_line', when: 'Demain 14:00', match: 74, lang: 'FR', rep: 79 },
  { id: 6, peer: 'chaimacoder', avatar: 'https://i.pravatar.cc/64?img=45', level: 10.87, project: 'cub3d', when: 'Jeudi 11:00', match: 82, lang: 'EN / FR', rep: 96 },
]

const HISTORY = [
  { id: 7, peer: 'BlackHoleSurvivor', avatar: 'https://i.pravatar.cc/64?img=12', project: 'netpractice', date: '24 août 2026', score: 100, given: true },
  { id: 8, peer: 'ines_dev', avatar: 'https://i.pravatar.cc/64?img=47', project: 'ft_printf', date: '19 août 2026', score: 115, given: false },
  { id: 9, peer: 'mehdi42', avatar: 'https://i.pravatar.cc/64?img=33', project: 'get_next_line', date: '11 août 2026', score: 100, given: true },
]

function MatchRing({ value }) {
  const tone = value >= 90 ? '#2ECC71' : value >= 80 ? '#F8851F' : '#F5B942'
  return (
    <div className="flex flex-col items-center">
      <span className="font-mono text-[15px] font-extrabold" style={{ color: tone }}>{value}%</span>
      <span className="text-[9.5px] uppercase tracking-wider text-ink-faint">match</span>
    </div>
  )
}

export default function PeerReview() {
  usePageHeader({ title: 'Peer Review' })
  const [tab, setTab] = useState('upcoming')

  return (
    <div className="container-page space-y-5 py-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-[24px] font-extrabold tracking-tight text-white">Peer Review</h1>
          <p className="mt-1.5 text-[13px] text-ink-dim">
            Smart Matchmaking · niveau, disponibilité, langue et réputation pris en compte
          </p>
        </div>
        <Button icon="CalendarPlus">Ouvrir un créneau</Button>
      </div>

      {/* KPI */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {[
          { l: 'Correction Points', v: currentUser.correctionPoints.toLocaleString('fr-FR'), i: 'Coins', t: 'text-brand-500' },
          { l: 'Corrections données', v: '47', i: 'ClipboardCheck', t: 'text-ok' },
          { l: 'Corrections reçues', v: '38', i: 'Inbox', t: 'text-info' },
          { l: 'Reputation Score', v: `${currentUser.reputation}/100`, i: 'Star', t: 'text-warn' },
        ].map((s) => (
          <div key={s.l} className="card flex items-center gap-3.5 p-4">
            <span className={`grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-white/[0.04] ${s.t}`}>
              <Icon name={s.i} size={18} />
            </span>
            <div>
              <p className="text-[11px] uppercase tracking-wider text-ink-dim">{s.l}</p>
              <p className="font-mono text-[18px] font-extrabold text-ink">{s.v}</p>
            </div>
          </div>
        ))}
      </div>

      <section className="card overflow-hidden">
        <Tabs
          active={tab}
          onChange={setTab}
          tabs={[
            { key: 'upcoming', label: 'Mes slots', count: REQUESTS.length },
            { key: 'available', label: 'Slots disponibles', count: AVAILABLE.length },
            { key: 'history', label: 'Historique', count: HISTORY.length },
          ]}
        />

        {tab === 'upcoming' && (
          <ul className="divide-y divide-line/70">
            {REQUESTS.map((r) => (
              <li key={r.id} className="flex flex-wrap items-center gap-4 px-5 py-4">
                <Avatar src={r.avatar} name={r.peer} size="md" status="online" />
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <p className="text-[13.5px] font-semibold text-ink">@{r.peer}</p>
                    <Badge tone="muted">Niv. {r.level.toFixed(2)}</Badge>
                    <Badge tone={r.role === 'Tu corriges' ? 'brand' : 'info'}>{r.role}</Badge>
                  </div>
                  <p className="mt-1 flex flex-wrap items-center gap-x-4 gap-y-1 text-[11.5px] text-ink-dim">
                    <span className="font-mono text-ink-soft">{r.project}</span>
                    <span className="flex items-center gap-1.5"><Icon name="CalendarClock" size={12} /> {r.when}</span>
                    <span className="flex items-center gap-1.5"><Icon name="Languages" size={12} /> {r.lang}</span>
                  </p>
                </div>
                <MatchRing value={r.match} />
                <div className="flex gap-2">
                  <Button to="/rooms/r1" size="sm" icon="Video">Rejoindre</Button>
                  <Button size="sm" variant="ghost" icon="X" className="px-2.5" aria-label="Annuler" />
                </div>
              </li>
            ))}
          </ul>
        )}

        {tab === 'available' && (
          <ul className="divide-y divide-line/70">
            {AVAILABLE.map((r) => (
              <li key={r.id} className="flex flex-wrap items-center gap-4 px-5 py-4 transition-colors hover:bg-white/[0.02]">
                <Avatar src={r.avatar} name={r.peer} size="md" />
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <p className="text-[13.5px] font-semibold text-ink">@{r.peer}</p>
                    <Badge tone="muted">Niv. {r.level.toFixed(2)}</Badge>
                    {r.rep >= 90 && <Badge tone="ok"><Icon name="ShieldCheck" size={10} /> Trusted</Badge>}
                  </div>
                  <p className="mt-1 flex flex-wrap items-center gap-x-4 gap-y-1 text-[11.5px] text-ink-dim">
                    <span className="font-mono text-ink-soft">{r.project}</span>
                    <span className="flex items-center gap-1.5"><Icon name="CalendarClock" size={12} /> {r.when}</span>
                    <span className="flex items-center gap-1.5"><Icon name="Languages" size={12} /> {r.lang}</span>
                  </p>
                  <div className="mt-2 flex items-center gap-2">
                    <span className="text-[10.5px] text-ink-faint">Réputation</span>
                    <ProgressBar value={r.rep} height={4} className="w-24" />
                    <span className="font-mono text-[10.5px] text-ink-soft">{r.rep}</span>
                  </div>
                </div>
                <MatchRing value={r.match} />
                <Button size="sm" variant="outline" iconRight="ArrowRight">Réserver</Button>
              </li>
            ))}
          </ul>
        )}

        {tab === 'history' &&
          (HISTORY.length ? (
            <ul className="divide-y divide-line/70">
              {HISTORY.map((h) => (
                <li key={h.id} className="flex items-center gap-4 px-5 py-4">
                  <Avatar src={h.avatar} name={h.peer} size="sm" />
                  <div className="min-w-0 flex-1">
                    <p className="text-[13px] font-semibold text-ink">@{h.peer}</p>
                    <p className="font-mono text-[11.5px] text-ink-dim">{h.project}</p>
                  </div>
                  <Badge tone={h.given ? 'brand' : 'info'}>{h.given ? 'Donnée' : 'Reçue'}</Badge>
                  <span className="hidden w-28 text-right text-[11.5px] text-ink-faint sm:block">{h.date}</span>
                  <span className={`w-12 text-right font-mono text-[15px] font-extrabold ${h.score >= 100 ? 'text-ok' : 'text-warn'}`}>
                    {h.score}
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState icon="History" title="Aucune correction" text="Ton historique apparaîtra ici." />
          ))}
      </section>
    </div>
  )
}
