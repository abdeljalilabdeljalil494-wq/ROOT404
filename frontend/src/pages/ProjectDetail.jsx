import { useState, useCallback } from 'react'
import { Link, useParams } from 'react-router-dom'
import usePageHeader from '../hooks/usePageHeader'
import Icon from '../components/ui/Icon'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import Tabs from '../components/ui/Tabs'
import Avatar from '../components/ui/Avatar'
import ProgressBar from '../components/ui/ProgressBar'
import EmptyState from '../components/ui/EmptyState'
import { projectService } from '../services/api'
import { useCurrentUser } from '../components/RequireAuth'
import useResource from '../hooks/useResource'
import ResourceState from '../components/ui/ResourceState'

export default function ProjectDetail() {
  const { slug } = useParams()
  const currentUser = useCurrentUser()
  const resource = useResource(useCallback(() => projectService.bySlug(slug), [slug]))
  const p = resource.data ? { ...resource.data, status: resource.data.status === 'passed' ? 'done' : resource.data.status } : { name: 'Projet', slug, tags: [] }
  const OBJECTIVES = p.objectives || []
  const CONSTRAINTS = (p.constraints || []).map(c => typeof c === 'string' ? { text: c, icon: 'Info' } : c)
  const CORRECTIONS = []
  const DISCUSSIONS = []
  const moulinetteTests = p.submissions?.[0]?.tests || []
  const [tab, setTab] = useState('description')

  usePageHeader(
    { title: p.name, breadcrumb: [{ label: 'Mes projets', to: '/projects' }, { label: p.name }] },
    [p.slug],
  )

  if (resource.loading || resource.error) return <ResourceState resource={resource} />

  const passed = moulinetteTests.filter((t) => t.status === 'pass').length

  return (
    <div className="container-page py-6">
      {/* ---------- Header ---------- */}
      <div className="card mb-5 overflow-hidden">
        <div className="relative p-5 sm:p-6">
          <div
            aria-hidden
            className="absolute inset-0 opacity-40"
            style={{ background: `radial-gradient(700px 180px at 12% 0%, ${p.langColor}1F, transparent)` }}
          />
          <div className="relative flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
            <div className="flex min-w-0 items-start gap-4">
              <span
                className="grid h-16 w-16 shrink-0 place-items-center rounded-xl border border-line font-mono text-xl font-bold"
                style={{ background: `radial-gradient(circle at 35% 25%, ${p.langColor}26, #0A1017 70%)`, color: p.langColor }}
              >
                {p.name.slice(0, 2)}
              </span>
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <h1 className="font-mono text-[24px] font-extrabold tracking-tight text-white">{p.name}</h1>
                  <Badge tone="brand">{p.level}</Badge>
                  <Badge tone={p.status === 'done' ? 'ok' : p.status === 'failed' ? 'danger' : 'info'}>
                    {p.status === 'progress' ? 'En cours' : p.status === 'done' ? 'Terminé' : p.status === 'failed' ? 'Échoué' : 'Disponible'}
                  </Badge>
                </div>
                <p className="mt-2 max-w-xl text-[13px] leading-relaxed text-ink-dim">{p.desc}</p>
                <div className="mt-3.5 flex flex-wrap items-center gap-1.5">
                  <span className="chip" style={{ color: p.langColor }}>
                    <span className="h-1.5 w-1.5 rounded-full" style={{ background: p.langColor }} />
                    {p.lang}
                  </span>
                  {p.tags.map((t) => <span key={t} className="chip">{t}</span>)}
                  <span className="chip"><Icon name="Clock" size={11} /> {p.duration}</span>
                  <span className="chip">
                    <Icon name="Flame" size={11} className="text-brand-500" /> Difficulté {p.difficulty}/5
                  </span>
                </div>
              </div>
            </div>

            <div className="flex shrink-0 flex-wrap items-center gap-2">
              <Button to={`/workspace/${p.slug}`} icon="Code2">Ouvrir le workspace</Button>
              <Button variant="outline" icon="FileText">Sujet PDF</Button>
              <Button variant="ghost" icon="Star" className="px-2.5" aria-label="Favori" />
            </div>
          </div>

          {p.status === 'progress' && (
            <div className="relative mt-6 rounded-lg border border-line bg-root-850 p-4">
              <div className="flex items-center justify-between text-[12px]">
                <span className="font-semibold text-ink">Progression du projet</span>
                <span className="font-mono font-bold text-brand-500">{p.progress}%</span>
              </div>
              <ProgressBar value={p.progress} height={7} className="mt-2.5" />
              <div className="mt-3 flex flex-wrap gap-x-6 gap-y-2 text-[11.5px] text-ink-dim">
                <span className="flex items-center gap-1.5"><Icon name="GitCommit" size={12} /> 47 commits</span>
                <span className="flex items-center gap-1.5"><Icon name="Upload" size={12} /> 3 soumissions</span>
                <span className="flex items-center gap-1.5"><Icon name="CalendarClock" size={12} /> Deadline dans 11 j.</span>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="grid gap-5 xl:grid-cols-[1fr_340px]">
        {/* ---------- Main ---------- */}
        <div className="card overflow-hidden">
          <Tabs
            active={tab}
            onChange={setTab}
            tabs={[
              { key: 'description', label: 'Description' },
              { key: 'instructions', label: 'Instructions' },
              { key: 'corrections', label: 'Corrections', count: CORRECTIONS.length },
              { key: 'discussions', label: 'Discussions', count: DISCUSSIONS.length },
            ]}
          />

          <div className="p-5 sm:p-6">
            {tab === 'description' && (
              <div className="space-y-7">
                <section>
                  <h2 className="flex items-center gap-2 text-[14px] font-bold text-ink">
                    <Icon name="Target" size={16} className="text-brand-500" /> Objectif
                  </h2>
                  <p className="mt-3 text-[13.5px] leading-[1.75] text-ink-soft">
                    {p.long_description || p.desc}
                  </p>
                  <ul className="mt-4 space-y-2.5">
                    {OBJECTIVES.map((o) => (
                      <li key={o} className="flex gap-2.5 text-[13px] leading-relaxed text-ink-soft">
                        <Icon name="Check" size={15} className="mt-0.5 shrink-0 text-ok" />
                        {o}
                      </li>
                    ))}
                  </ul>
                </section>

                <section>
                  <h2 className="flex items-center gap-2 text-[14px] font-bold text-ink">
                    <Icon name="ShieldAlert" size={16} className="text-brand-500" /> Contraintes
                  </h2>
                  <div className="mt-3 grid gap-2.5 sm:grid-cols-2">
                    {CONSTRAINTS.map((c) => (
                      <div key={c.text} className="flex gap-2.5 rounded-lg border border-line bg-root-850 p-3">
                        <Icon name={c.icon} size={15} className="mt-0.5 shrink-0 text-ink-dim" />
                        <span className="text-[12.5px] leading-relaxed text-ink-soft">{c.text}</span>
                      </div>
                    ))}
                  </div>
                </section>

                <section>
                  <h2 className="flex items-center gap-2 text-[14px] font-bold text-ink">
                    <Icon name="GitFork" size={16} className="text-brand-500" /> Prérequis
                  </h2>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {(p.requires ? [p.requires] : []).map((r) => (
                      <Link
                        key={r}
                        to={`/projects/${r}`}
                        className="chip transition-colors hover:border-brand-500/40 hover:text-brand-500"
                      >
                        <Icon name="CheckCircle2" size={11} className="text-ok" /> {r}
                      </Link>
                    ))}
                  </div>
                </section>
              </div>
            )}

            {tab === 'instructions' && <p className="text-ink-dim">Ouvre le workspace pour écrire, exécuter et soumettre ton code. L’évaluation nécessite un exécuteur isolé configuré et une suite de tests du projet.</p>}

            {tab === 'corrections' &&
              (CORRECTIONS.length ? (
                <ul className="space-y-3">
                  {CORRECTIONS.map((c) => (
                    <li key={c.peer} className="rounded-lg border border-line bg-root-850 p-4">
                      <div className="flex items-center gap-3">
                        <Avatar src={c.avatar} name={c.peer} size="sm" />
                        <div className="min-w-0 flex-1">
                          <p className="text-[13px] font-semibold text-ink">@{c.peer}</p>
                          <p className="text-[11px] text-ink-faint">{c.date}</p>
                        </div>
                        <span
                          className={`font-mono text-[16px] font-extrabold ${
                            c.score >= 80 ? 'text-ok' : c.score >= 50 ? 'text-warn' : 'text-danger'
                          }`}
                        >
                          {c.score}
                        </span>
                      </div>
                      <p className="mt-3 text-[12.5px] leading-relaxed text-ink-soft">{c.comment}</p>
                    </li>
                  ))}
                </ul>
              ) : (
                <EmptyState icon="ClipboardCheck" title="Aucune correction" text="Réserve un slot pour être corrigé." />
              ))}

            {tab === 'discussions' && (
              <div className="space-y-4">
                <div className="flex gap-3">
                  <Avatar src={currentUser.avatar} name={currentUser.displayName} size="sm" />
                  <div className="flex-1">
                    <textarea
                      rows={2}
                      placeholder="Pose une question sans spoiler la solution…"
                      className="input h-auto resize-none py-2.5"
                    />
                    <div className="mt-2 flex justify-end">
                      <Button size="sm" disabled title="Discussions non implémentées" icon="Send">Publication indisponible</Button>
                    </div>
                  </div>
                </div>
                <ul className="space-y-3">
                  {DISCUSSIONS.map((d) => (
                    <li key={d.user} className="flex gap-3 rounded-lg border border-line bg-root-850 p-4">
                      <Avatar src={d.avatar} name={d.user} size="sm" />
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2">
                          <span className="text-[12.5px] font-semibold text-ink">@{d.user}</span>
                          <span className="text-[11px] text-ink-faint">{d.time}</span>
                        </div>
                        <p className="mt-1.5 text-[12.5px] leading-relaxed text-ink-soft">{d.text}</p>
                        <div className="mt-2.5 flex items-center gap-4 text-[11.5px] text-ink-dim">
                          <button className="flex items-center gap-1.5 transition-colors hover:text-brand-500">
                            <Icon name="ArrowBigUp" size={14} /> {d.votes}
                          </button>
                          <button className="flex items-center gap-1.5 transition-colors hover:text-brand-500">
                            <Icon name="MessageSquare" size={13} /> Répondre
                          </button>
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>

        {/* ---------- Sidebar ---------- */}
        <aside className="space-y-4">
          <section className="card p-5">
            <h2 className="text-[13px] font-bold text-ink">Validations & XP</h2>
            <ul className="mt-4 space-y-3">
              {[
                { label: 'Moulinette', value: `${p.submissions?.length || 0} soumissions`, tone: 'ok', icon: 'Cpu' },
                { label: 'Peer Review', value: 'Non disponible', tone: 'brand', icon: 'Users' },
                { label: 'AI Review', value: 'Non effectué', tone: 'info', icon: 'Sparkles' },
                { label: 'Bonus', value: 'Non tenté', tone: 'muted', icon: 'Gift' },
              ].map((r) => (
                <li key={r.label} className="flex items-center gap-3">
                  <Icon name={r.icon} size={15} className="shrink-0 text-ink-dim" />
                  <span className="flex-1 text-[12.5px] text-ink-soft">{r.label}</span>
                  <Badge tone={r.tone}>{r.value}</Badge>
                </li>
              ))}
            </ul>
            <div className="mt-5 rounded-lg border border-brand-500/25 bg-brand-500/[0.07] p-3.5 text-center">
              <p className="text-[10.5px] font-semibold uppercase tracking-wider text-ink-dim">
                Récompense totale
              </p>
              <p className="mt-1 font-mono text-[22px] font-extrabold text-brand-500">
                +{p.xp.toLocaleString('fr-FR')} XP
              </p>
            </div>
          </section>

          <section className="card p-5">
            <h2 className="text-[13px] font-bold text-ink">Derniers tests Moulinette</h2>
            <ul className="mt-3.5 space-y-2">
              {moulinetteTests.map((t) => (
                <li key={t.name} className="flex items-center gap-2.5 text-[12px]">
                  <Icon
                    name={t.status === 'pass' ? 'CheckCircle2' : t.status === 'warn' ? 'AlertTriangle' : 'XCircle'}
                    size={14}
                    className={t.status === 'pass' ? 'text-ok' : t.status === 'warn' ? 'text-warn' : 'text-danger'}
                  />
                  <span className="flex-1 truncate text-ink-soft">{t.name}</span>
                  <span
                    className={`shrink-0 font-mono text-[11px] ${
                      t.status === 'pass' ? 'text-ok' : t.status === 'warn' ? 'text-warn' : 'text-danger'
                    }`}
                  >
                    {t.detail}
                  </span>
                </li>
              ))}
            </ul>
            <Button to={`/workspace/${p.slug}`} variant="outline" size="sm" full className="mt-4" icon="RefreshCw">
              Relancer la Moulinette
            </Button>
          </section>

          <section className="card p-5">
            <h2 className="text-[13px] font-bold text-ink">Prochaine étape</h2>
            <p className="mt-2 text-[12.5px] leading-relaxed text-ink-dim">
              Corrige le handler de <span className="font-mono text-ink">SIGQUIT</span>, puis réserve
              un slot de peer review pour valider le projet.
            </p>
            <Button to="/peer-review" size="sm" full className="mt-4" iconRight="ArrowRight">
              Réserver un slot
            </Button>
          </section>
        </aside>
      </div>
    </div>
  )
}
