import { useState } from 'react'
import { Link } from 'react-router-dom'
import usePageHeader from '../hooks/usePageHeader'
import Icon from '../components/ui/Icon'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import Tabs from '../components/ui/Tabs'
import Avatar from '../components/ui/Avatar'
import ProgressBar from '../components/ui/ProgressBar'
import Heatmap from '../components/ui/Heatmap'
import LevelRing from '../components/ui/LevelRing'
import { currentUser, projects, badges, skillGraph, reputation, integrityScore, analytics } from '../data/mock'

const TIER = {
  gold: { bg: 'from-[#FFC53D]/20', text: 'text-[#FFC53D]', ring: 'ring-[#FFC53D]/30' },
  silver: { bg: 'from-[#C9D1D9]/15', text: 'text-[#C9D1D9]', ring: 'ring-[#C9D1D9]/25' },
  bronze: { bg: 'from-[#D08A4E]/15', text: 'text-[#D08A4E]', ring: 'ring-[#D08A4E]/25' },
}

export default function Profile() {
  usePageHeader({ title: 'Profil' })
  const [tab, setTab] = useState('overview')

  const stats = [
    { label: 'Niveau', value: currentUser.level.toFixed(2), icon: 'TrendingUp' },
    { label: 'XP', value: currentUser.xp.toLocaleString('fr-FR'), icon: 'Zap' },
    { label: 'Projets', value: currentUser.projectsDone, icon: 'CheckCircle2' },
    { label: 'Correction Points', value: currentUser.correctionPoints.toLocaleString('fr-FR'), icon: 'Users' },
    { label: 'Valeur de compte', value: currentUser.accountValue.toLocaleString('fr-FR'), icon: 'Coins' },
  ]

  return (
    <div className="container-page space-y-5 py-6">
      {/* ---------- Header ---------- */}
      <section className="card overflow-hidden">
        <div className="relative h-28 bg-gradient-to-r from-brand-500/25 via-root-850 to-root-900">
          <div aria-hidden className="absolute inset-0 bg-grid opacity-50" />
        </div>

        <div className="px-5 pb-5 sm:px-6">
          <div className="-mt-12 flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
            <div className="flex items-end gap-4">
              <Avatar src={currentUser.avatar} name={currentUser.fullName} size="xl" ring />
              <div className="pb-1">
                <div className="flex flex-wrap items-center gap-2">
                  <h1 className="text-[22px] font-extrabold tracking-tight text-white">
                    {currentUser.fullName}
                  </h1>
                  <Badge tone="ok" dot>En ligne</Badge>
                </div>
                <p className="mt-1 text-[13px] text-ink-dim">
                  @{currentUser.username} · {currentUser.title}
                </p>
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button to="/portfolio" variant="outline" size="sm" icon="Globe">Portfolio public</Button>
              <Button to="/settings" size="sm" icon="Pencil">Modifier</Button>
            </div>
          </div>

          <p className="mt-4 max-w-2xl text-[13px] leading-relaxed text-ink-soft">{currentUser.bio}</p>

          <div className="mt-4 flex flex-wrap gap-x-5 gap-y-2 text-[12px] text-ink-dim">
            <span className="flex items-center gap-1.5"><Icon name="MapPin" size={13} /> Campus {currentUser.campus}</span>
            <span className="flex items-center gap-1.5"><Icon name="Flame" size={13} className="text-brand-500" /> {currentUser.coalition.name}</span>
            <span className="flex items-center gap-1.5"><Icon name="CalendarDays" size={13} /> Membre depuis {currentUser.joined}</span>
            <span className="flex items-center gap-1.5"><Icon name="Github" size={13} /> {currentUser.socials.github}</span>
            <a href="#" className="flex items-center gap-1.5 text-brand-500 hover:underline">
              <Icon name="Link2" size={13} /> {currentUser.socials.site}
            </a>
          </div>

          {/* Stat strip */}
          <div className="mt-5 grid grid-cols-2 gap-px overflow-hidden rounded-xl border border-line bg-line sm:grid-cols-3 lg:grid-cols-5">
            {stats.map((s) => (
              <div key={s.label} className="bg-root-850 px-4 py-3.5">
                <p className="flex items-center gap-1.5 text-[10.5px] uppercase tracking-wider text-ink-faint">
                  <Icon name={s.icon} size={11} /> {s.label}
                </p>
                <p className="mt-1.5 font-mono text-[18px] font-extrabold text-ink">{s.value}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ---------- Tabs ---------- */}
      <section className="card overflow-hidden">
        <Tabs
          active={tab}
          onChange={setTab}
          tabs={[
            { key: 'overview', label: 'Aperçu' },
            { key: 'projects', label: 'Projets', count: projects.filter((p) => p.status === 'done').length },
            { key: 'skills', label: 'Compétences' },
            { key: 'badges', label: 'Badges', count: badges.length },
            { key: 'stats', label: 'Statistiques' },
          ]}
        />

        <div className="p-5 sm:p-6">
          {/* ---- Overview ---- */}
          {tab === 'overview' && (
            <div className="space-y-6">
              <div>
                <div className="mb-3.5 flex items-center justify-between">
                  <h2 className="flex items-center gap-2 text-[14px] font-bold text-ink">
                    <Icon name="Activity" size={15} className="text-brand-500" /> Ton année de code
                  </h2>
                  <Badge tone="brand" dot>{currentUser.streak} jours de streak</Badge>
                </div>
                <Heatmap />
              </div>

              <div className="grid gap-4 lg:grid-cols-3">
                <div className="rounded-xl border border-line bg-root-850 p-5">
                  <h3 className="text-[13px] font-bold text-ink">Niveau</h3>
                  <div className="mt-4 flex justify-center">
                    <LevelRing level={currentUser.level} progress={currentUser.levelProgress} />
                  </div>
                  <p className="mt-4 text-center text-[11.5px] text-ink-dim">
                    {currentUser.xpToNext.toLocaleString('fr-FR')} XP avant le niveau 7.00
                  </p>
                </div>

                <div className="rounded-xl border border-line bg-root-850 p-5">
                  <h3 className="text-[13px] font-bold text-ink">Réputation</h3>
                  <ul className="mt-4 space-y-3">
                    {reputation.map((r) => (
                      <li key={r.label}>
                        <ProgressBar value={r.value} showLabel label={r.label} height={5} />
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="rounded-xl border border-line bg-root-850 p-5">
                  <div className="flex items-center justify-between">
                    <h3 className="text-[13px] font-bold text-ink">Integrity Score</h3>
                    <span className="font-mono text-[18px] font-extrabold text-ok">{integrityScore.total}</span>
                  </div>
                  <ul className="mt-4 space-y-2.5">
                    {integrityScore.rows.map((r) => (
                      <li key={r.label} className="flex items-center justify-between text-[12px]">
                        <span className="text-ink-dim">{r.label}</span>
                        <span className="flex items-center gap-1.5 font-medium text-ok">
                          <Icon name="Check" size={12} /> {r.value}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* ---- Projects ---- */}
          {tab === 'projects' && (
            <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {projects.filter((p) => p.status !== 'locked').map((p) => (
                <li key={p.id}>
                  <Link
                    to={`/projects/${p.slug}`}
                    className="flex h-full flex-col rounded-lg border border-line bg-root-850 p-4 transition-all hover:-translate-y-0.5 hover:border-brand-500/30"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-[13px] font-bold text-ink">{p.name}</span>
                      <Icon
                        name={p.status === 'done' ? 'CheckCircle2' : p.status === 'failed' ? 'XCircle' : 'Loader'}
                        size={15}
                        className={p.status === 'done' ? 'text-ok' : p.status === 'failed' ? 'text-danger' : 'text-brand-500'}
                      />
                    </div>
                    <p className="mt-1 text-[11px] text-ink-dim">{p.level} · {p.lang}</p>
                    <p className="mt-2 line-clamp-2 flex-1 text-[12px] text-ink-dim">{p.desc}</p>
                    <div className="mt-3 flex items-center justify-between border-t border-line pt-3">
                      <span className="text-[11px] text-ink-faint">{p.duration}</span>
                      <span className="font-mono text-[12px] font-bold text-brand-500">
                        {p.score ? `${p.score}%` : `${p.progress ?? 0}%`}
                      </span>
                    </div>
                  </Link>
                </li>
              ))}
            </ul>
          )}

          {/* ---- Skills ---- */}
          {tab === 'skills' && (
            <div className="grid gap-5 sm:grid-cols-2">
              {skillGraph.map((g) => (
                <div key={g.group} className="rounded-xl border border-line bg-root-850 p-5">
                  <h3 className="flex items-center gap-2 text-[13px] font-bold" style={{ color: g.color }}>
                    <span className="h-2 w-2 rounded-full" style={{ background: g.color }} />
                    {g.group}
                  </h3>
                  <ul className="mt-4 space-y-3">
                    {g.skills.map((s) => (
                      <li key={s.name}>
                        <ProgressBar value={s.value} color={g.color} showLabel label={s.name} height={5} />
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          )}

          {/* ---- Badges ---- */}
          {tab === 'badges' && (
            <ul className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
              {badges.map((b) => {
                const t = TIER[b.tier]
                return (
                  <li
                    key={b.name}
                    className={`flex flex-col items-center rounded-xl border border-line bg-gradient-to-b ${t.bg} to-transparent p-5 text-center transition-transform hover:-translate-y-1`}
                  >
                    <span className={`grid h-12 w-12 place-items-center rounded-full bg-root-900 ring-2 ${t.ring} ${t.text}`}>
                      <Icon name={b.icon} size={22} />
                    </span>
                    <p className="mt-3 text-[12.5px] font-semibold text-ink">{b.name}</p>
                    <p className={`mt-0.5 text-[10px] font-bold uppercase tracking-wider ${t.text}`}>{b.tier}</p>
                  </li>
                )
              })}
            </ul>
          )}

          {/* ---- Stats ---- */}
          {tab === 'stats' && (
            <div className="grid gap-5 lg:grid-cols-2">
              <div className="rounded-xl border border-line bg-root-850 p-5">
                <h3 className="text-[13px] font-bold text-ink">Learning Velocity</h3>
                <ProgressBar value={analytics.velocity} showLabel label="Vitesse d'apprentissage" height={7} className="mt-4" />
                <ProgressBar value={analytics.consistency} showLabel label="Régularité" color="#2ECC71" height={7} className="mt-4" />
                <p className="mt-5 rounded-lg border border-line bg-root-800 p-3.5 text-[12px] leading-relaxed italic text-ink-dim">
                  « {analytics.insight} »
                </p>
              </div>
              <div className="rounded-xl border border-line bg-root-850 p-5">
                <h3 className="text-[13px] font-bold text-ink">Tolérance à la difficulté</h3>
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
              </div>
            </div>
          )}
        </div>
      </section>
    </div>
  )
}
