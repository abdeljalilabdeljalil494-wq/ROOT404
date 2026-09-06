import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import usePageHeader from '../hooks/usePageHeader'
import Icon from '../components/ui/Icon'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import Tabs from '../components/ui/Tabs'
import ProgressBar from '../components/ui/ProgressBar'
import EmptyState from '../components/ui/EmptyState'
import { projectService } from '../services/api'
import { projects as mockProjects, projectStatusMap } from '../data/mock'

/* ---------- Status pill ---------- */
function StatusCell({ p }) {
  const s = projectStatusMap[p.status]
  if (p.status === 'progress') {
    return (
      <div className="w-full max-w-[190px]">
        <span className="flex items-center gap-1.5 text-[12px] font-semibold text-brand-500">
          <Icon name="Loader" size={13} className="animate-spin [animation-duration:3s]" />
          En cours
        </span>
        <div className="mt-2 flex items-center gap-2">
          <ProgressBar value={p.progress} height={5} className="flex-1" />
          <span className="font-mono text-[11px] font-semibold text-ink-soft">{p.progress}%</span>
        </div>
      </div>
    )
  }
  if (p.status === 'done') {
    return (
      <span className="flex items-center gap-1.5 text-[12px] font-semibold text-ok">
        <Icon name="CheckCircle2" size={14} />
        Terminé {p.bonus && <span className="text-brand-500">+ bonus</span>}
        <span className="ml-1 font-mono text-ink-soft">{p.score}%</span>
      </span>
    )
  }
  if (p.status === 'failed') {
    return (
      <span className="flex items-center gap-1.5 text-[12px] font-semibold text-danger">
        <Icon name="XCircle" size={14} /> Échoué <span className="font-mono">{p.score}%</span>
      </span>
    )
  }
  return (
    <span
      className={`flex items-center gap-1.5 text-[12px] font-semibold ${
        p.status === 'locked' ? 'text-ink-dim' : 'text-info'
      }`}
    >
      <Icon name={s.icon} size={14} /> {s.label}
    </span>
  )
}

/* ---------- Project thumbnail ---------- */
function Thumb({ p, size = 52 }) {
  return (
    <span
      className="grid shrink-0 place-items-center rounded-lg border border-line font-mono text-[15px] font-bold"
      style={{
        width: size,
        height: size,
        background: `radial-gradient(circle at 35% 25%, ${p.langColor}26, #0A1017 70%)`,
        color: p.langColor,
      }}
      aria-hidden
    >
      {p.lang === 'Docker' ? <Icon name="Container" size={22} /> : p.name.slice(0, 2)}
    </span>
  )
}

/* ---------- List row ---------- */
function ProjectRow({ p }) {
  return (
    <li className="group relative flex flex-col gap-4 border-b border-line/70 px-4 py-4 transition-colors last:border-0 hover:bg-white/[0.02] sm:px-5 lg:flex-row lg:items-center">
      <div className="flex min-w-0 flex-1 items-start gap-4">
        <Thumb p={p} />
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <Link
              to={`/projects/${p.slug}`}
              className="font-mono text-[14px] font-bold text-ink transition-colors group-hover:text-brand-500"
            >
              {p.name}
            </Link>
            <Badge tone="brand">{p.level}</Badge>
            {p.status === 'locked' && <Icon name="Lock" size={12} className="text-ink-faint" />}
          </div>
          <p className="mt-1 line-clamp-2 text-[12.5px] leading-relaxed text-ink-dim">{p.desc}</p>
          <div className="mt-2.5 flex flex-wrap items-center gap-1.5">
            <span className="chip" style={{ color: p.langColor }}>
              <span className="h-1.5 w-1.5 rounded-full" style={{ background: p.langColor }} />
              {p.lang}
            </span>
            {p.tags.map((t) => (
              <span key={t} className="chip">{t}</span>
            ))}
          </div>
        </div>
      </div>

      <div className="flex shrink-0 items-center justify-between gap-6 lg:w-[300px]">
        <div className="min-w-0 flex-1">
          <p className="mb-1.5 text-[10.5px] font-semibold uppercase tracking-wider text-ink-faint">
            Statut
          </p>
          <StatusCell p={p} />
        </div>
        <div className="text-right">
          <p className="mb-1 text-[10.5px] font-semibold uppercase tracking-wider text-ink-faint">
            XP
          </p>
          <p className="font-mono text-[13px] font-bold text-brand-500">
            {p.xp.toLocaleString('fr-FR')}
          </p>
        </div>
        <button
          aria-label="Options"
          className="grid h-8 w-8 place-items-center rounded-md text-ink-faint transition-colors hover:bg-white/[0.06] hover:text-ink"
        >
          <Icon name="MoreVertical" size={16} />
        </button>
      </div>
    </li>
  )
}

/* ---------- Grid card ---------- */
function ProjectCard({ p }) {
  return (
    <Link
      to={`/projects/${p.slug}`}
      className="card group flex flex-col p-4 transition-all hover:-translate-y-1 hover:border-brand-500/30"
    >
      <div className="flex items-start justify-between gap-3">
        <Thumb p={p} size={46} />
        <Badge tone="brand">{p.level}</Badge>
      </div>
      <h3 className="mt-3.5 font-mono text-[14px] font-bold text-ink transition-colors group-hover:text-brand-500">
        {p.name}
      </h3>
      <p className="mt-1.5 line-clamp-2 flex-1 text-[12px] leading-relaxed text-ink-dim">{p.desc}</p>
      <div className="mt-4 border-t border-line pt-3.5">
        <StatusCell p={p} />
        <div className="mt-3 flex items-center justify-between text-[11px] text-ink-dim">
          <span className="flex items-center gap-1.5"><Icon name="Clock" size={12} /> {p.duration}</span>
          <span className="font-mono font-bold text-brand-500">{p.xp.toLocaleString('fr-FR')} XP</span>
        </div>
      </div>
    </Link>
  )
}

export default function Projects() {
  usePageHeader({ title: 'Mes projets', breadcrumb: [{ label: 'Mes projets' }] })

  // Real per-user project states from the backend (mock fallback when offline).
  const [projects, setProjects] = useState(mockProjects)
  useEffect(() => {
    let alive = true
    projectService
      .list()
      .then((list) => {
        if (alive && list?.length) setProjects(list)
      })
      .catch(() => {}) // unauthenticated / offline → keep the mock list below
    return () => {
      alive = false
    }
  }, [])

  const [tab, setTab] = useState('all')
  const [q, setQ] = useState('')
  const [status, setStatus] = useState('all')
  const [lang, setLang] = useState('all')
  const [view, setView] = useState('list')

  const langs = useMemo(() => [...new Set(projects.map((p) => p.lang))], [])

  const filtered = useMemo(
    () =>
      projects.filter((p) => {
        if (tab === 'progress' && p.status !== 'progress') return false
        if (tab === 'done' && p.status !== 'done') return false
        if (tab === 'available' && p.status !== 'available') return false
        if (tab === 'locked' && p.status !== 'locked') return false
        if (status !== 'all' && p.status !== status) return false
        if (lang !== 'all' && p.lang !== lang) return false
        if (q && !`${p.name} ${p.desc} ${p.tags.join(' ')}`.toLowerCase().includes(q.toLowerCase()))
          return false
        return true
      }),
    [tab, q, status, lang],
  )

  const count = (s) => projects.filter((p) => p.status === s).length

  return (
    <div className="container-page py-6">
      <div className="mb-5 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-[24px] font-extrabold tracking-tight text-white">Mes projets</h1>
          <p className="mt-1.5 text-[13px] text-ink-dim">
            {projects.length} projets dans ton parcours · {count('done')} validés ·{' '}
            {count('progress')} en cours
          </p>
        </div>
        <Button to="/journey" variant="outline" size="sm" icon="Map">Voir le Code Journey</Button>
      </div>

      <div className="card overflow-hidden">
        <Tabs
          active={tab}
          onChange={setTab}
          tabs={[
            { key: 'all', label: 'Tous', count: projects.length },
            { key: 'progress', label: 'En cours', count: count('progress') },
            { key: 'done', label: 'Terminés', count: count('done') },
            { key: 'available', label: 'Disponibles', count: count('available') },
            { key: 'locked', label: 'Verrouillés', count: count('locked') },
          ]}
        />

        {/* Toolbar */}
        <div className="flex flex-wrap items-center gap-2.5 border-b border-line p-4">
          <label className="relative flex h-10 min-w-[200px] flex-1 items-center">
            <Icon name="Search" size={15} className="pointer-events-none absolute left-3 text-ink-faint" />
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Rechercher un projet…"
              className="input h-full pl-9"
            />
          </label>

          <select value={status} onChange={(e) => setStatus(e.target.value)} className="select w-auto min-w-[130px]">
            <option value="all">Statut</option>
            {Object.entries(projectStatusMap).map(([k, v]) => (
              <option key={k} value={k}>{v.label}</option>
            ))}
          </select>

          <select value={lang} onChange={(e) => setLang(e.target.value)} className="select w-auto min-w-[130px]">
            <option value="all">Langage</option>
            {langs.map((l) => <option key={l} value={l}>{l}</option>)}
          </select>

          <div className="flex overflow-hidden rounded-lg border border-line">
            {[
              { k: 'grid', i: 'LayoutGrid' },
              { k: 'list', i: 'List' },
            ].map((v) => (
              <button
                key={v.k}
                onClick={() => setView(v.k)}
                aria-label={v.k}
                aria-pressed={view === v.k}
                className={`grid h-[38px] w-10 place-items-center transition-colors ${
                  view === v.k ? 'bg-brand-500 text-[#160A00]' : 'text-ink-dim hover:bg-white/[0.05]'
                }`}
              >
                <Icon name={v.i} size={15} />
              </button>
            ))}
          </div>
        </div>

        {filtered.length === 0 ? (
          <EmptyState
            icon="SearchX"
            title="Aucun projet trouvé"
            text="Ajuste tes filtres ou lance une nouvelle recherche."
            action={
              <Button size="sm" variant="outline" onClick={() => { setQ(''); setStatus('all'); setLang('all'); setTab('all') }}>
                Réinitialiser
              </Button>
            }
          />
        ) : view === 'list' ? (
          <ul>{filtered.map((p) => <ProjectRow key={p.id} p={p} />)}</ul>
        ) : (
          <div className="grid gap-4 p-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {filtered.map((p) => <ProjectCard key={p.id} p={p} />)}
          </div>
        )}
      </div>
    </div>
  )
}
