import { useMemo, useState } from 'react'
import usePageHeader from '../hooks/usePageHeader'
import Icon from '../components/ui/Icon'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import Tabs from '../components/ui/Tabs'
import Avatar from '../components/ui/Avatar'
import ProgressBar from '../components/ui/ProgressBar'
import { leaderboard, coalitions } from '../data/mock'

const MEDALS = ['#FFC53D', '#C9D1D9', '#D08A4E']

function RankCell({ rank }) {
  if (rank <= 3) {
    return (
      <span className="flex items-center gap-1.5" style={{ color: MEDALS[rank - 1] }}>
        <Icon name="Medal" size={17} />
      </span>
    )
  }
  return <span className="font-mono text-[12.5px] text-ink-dim">{rank}</span>
}

function Podium() {
  const order = [leaderboard[1], leaderboard[0], leaderboard[2]]
  const heights = ['h-20', 'h-28', 'h-16']
  return (
    <div className="grid grid-cols-3 items-end gap-3 sm:gap-5">
      {order.map((u, i) => (
        <div key={u.user} className="flex flex-col items-center">
          <Avatar src={u.avatar} name={u.name} size={i === 1 ? 'lg' : 'md'} ring={i === 1} />
          <p className="mt-2.5 max-w-full truncate text-[12.5px] font-semibold text-ink">@{u.user}</p>
          <p className="font-mono text-[11px] text-brand-500">{u.level.toFixed(2)}</p>
          <div
            className={`mt-3 flex w-full ${heights[i]} flex-col items-center justify-start gap-1 rounded-t-lg border border-b-0 border-line pt-2.5`}
            style={{
              background: `linear-gradient(180deg, ${MEDALS[u.rank - 1]}1F, transparent)`,
            }}
          >
            <Icon name="Medal" size={18} style={{ color: MEDALS[u.rank - 1] }} />
            <span
              className="font-mono text-[20px] font-extrabold leading-none opacity-70"
              style={{ color: MEDALS[u.rank - 1] }}
            >
              {u.rank}
            </span>
          </div>
        </div>
      ))}
    </div>
  )
}

export default function Leaderboard() {
  usePageHeader({ title: 'Classement' })
  const [tab, setTab] = useState('global')
  const [q, setQ] = useState('')

  const rows = useMemo(
    () => leaderboard.filter((r) => `${r.user} ${r.name}`.toLowerCase().includes(q.toLowerCase())),
    [q],
  )

  return (
    <div className="container-page space-y-5 py-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-[24px] font-extrabold tracking-tight text-white">Classement</h1>
          <p className="mt-1.5 text-[13px] text-ink-dim">
            Mis à jour toutes les heures · Campus Tunis · Saison 3
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge tone="brand" dot>Ton rang : #4</Badge>
          <Button variant="outline" size="sm" icon="Download">Exporter</Button>
        </div>
      </div>

      {/* Podium */}
      <section className="card p-6">
        <Podium />
      </section>

      {/* Table */}
      <section className="card overflow-hidden">
        <Tabs
          active={tab}
          onChange={setTab}
          tabs={[
            { key: 'global', label: 'Global' },
            { key: 'coalitions', label: 'Coalitions' },
            { key: 'monthly', label: 'Mensuel' },
            { key: 'weekly', label: 'Hebdomadaire' },
          ]}
        />

        <div className="flex flex-wrap items-center gap-2.5 border-b border-line p-4">
          <label className="relative flex h-10 min-w-[200px] flex-1 items-center">
            <Icon name="Search" size={15} className="pointer-events-none absolute left-3 text-ink-faint" />
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Rechercher un codeur…"
              className="input h-full pl-9"
            />
          </label>
          <select className="select w-auto min-w-[140px]"><option>Tous les campus</option><option>Tunis</option><option>Sfax</option><option>Sousse</option></select>
          <select className="select w-auto min-w-[140px]"><option>Toutes coalitions</option>{coalitions.map((c) => <option key={c.id}>{c.name}</option>)}</select>
        </div>

        {tab === 'coalitions' ? (
          <ul className="divide-y divide-line/70">
            {coalitions.map((c, i) => (
              <li key={c.id} className="flex items-center gap-4 px-5 py-4 transition-colors hover:bg-white/[0.02]">
                <RankCell rank={i + 1} />
                <span
                  className="grid h-10 w-10 shrink-0 place-items-center rounded-lg"
                  style={{ background: `${c.color}1A`, color: c.color }}
                >
                  <Icon name="Flag" size={18} />
                </span>
                <div className="min-w-0 flex-1">
                  <p className="text-[13.5px] font-semibold text-ink">{c.name}</p>
                  <p className="truncate text-[11.5px] text-ink-dim">{c.motto}</p>
                </div>
                <div className="hidden text-right sm:block">
                  <p className="text-[11px] text-ink-faint">Membres</p>
                  <p className="font-mono text-[13px] text-ink-soft">{c.members}</p>
                </div>
                <div className="hidden text-right md:block">
                  <p className="text-[11px] text-ink-faint">Wars</p>
                  <p className="font-mono text-[13px] text-ink-soft">{c.wins}</p>
                </div>
                <div className="w-24 text-right">
                  <p className="font-mono text-[14px] font-bold" style={{ color: c.color }}>
                    {c.points.toLocaleString('fr-FR')}
                  </p>
                  <p className="text-[10.5px] text-ok">{c.trend}</p>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[680px]">
              <thead>
                <tr className="border-b border-line text-left text-[10.5px] font-bold uppercase tracking-wider text-ink-faint">
                  <th className="w-14 px-5 py-3">#</th>
                  <th className="px-2 py-3">Codeur</th>
                  <th className="px-3 py-3 text-right">Niveau</th>
                  <th className="px-3 py-3 text-right">XP</th>
                  <th className="hidden px-3 py-3 text-right sm:table-cell">Projets</th>
                  <th className="hidden px-3 py-3 text-right md:table-cell">Précision</th>
                  <th className="hidden px-5 py-3 lg:table-cell">Coalition</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((r) => (
                  <tr
                    key={r.user}
                    className={`border-b border-line/60 text-[13px] transition-colors last:border-0 ${
                      r.me
                        ? 'bg-brand-500/[0.09] font-semibold text-brand-400'
                        : 'text-ink-soft hover:bg-white/[0.02]'
                    }`}
                  >
                    <td className="px-5 py-3.5"><RankCell rank={r.rank} /></td>
                    <td className="px-2 py-3.5">
                      <div className="flex items-center gap-2.5">
                        <Avatar src={r.avatar} name={r.name} size="xs" ring={r.me} />
                        <div className="min-w-0">
                          <p className={`truncate text-[12.5px] ${r.me ? 'text-brand-400' : 'text-ink'} font-semibold`}>
                            @{r.user}
                          </p>
                          <p className="truncate text-[11px] text-ink-faint">{r.name}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-3 py-3.5 text-right font-mono">{r.level.toFixed(2)}</td>
                    <td className="px-3 py-3.5 text-right font-mono">{r.xp}</td>
                    <td className="hidden px-3 py-3.5 text-right font-mono sm:table-cell">{r.projects}</td>
                    <td className="hidden px-3 py-3.5 md:table-cell">
                      <div className="flex items-center justify-end gap-2">
                        <ProgressBar value={r.accuracy} height={4} className="w-14" />
                        <span className="font-mono text-[12px]">{r.accuracy}%</span>
                      </div>
                    </td>
                    <td className="hidden px-5 py-3.5 lg:table-cell">
                      <span className="chip">{r.coalition}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="flex items-center justify-center border-t border-line p-4">
          <Button variant="outline" size="sm" iconRight="ArrowRight">
            Voir le classement complet
          </Button>
        </div>
      </section>
    </div>
  )
}
