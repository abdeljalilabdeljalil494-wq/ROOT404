import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import usePageHeader from '../hooks/usePageHeader'
import Icon from '../components/ui/Icon'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import Tabs from '../components/ui/Tabs'
import Avatar from '../components/ui/Avatar'
import ProgressBar from '../components/ui/ProgressBar'
import EmptyState from '../components/ui/EmptyState'
import { projects, moulinetteTests, currentUser } from '../data/mock'

const OBJECTIVES = [
  'Afficher un prompt et lire une ligne avec la bibliothèque readline.',
  'Gérer un historique de commandes fonctionnel.',
  'Chercher et lancer le bon exécutable (PATH, chemin relatif, chemin absolu).',
  'Implémenter les builtins : echo -n, cd, pwd, export, unset, env, exit.',
  'Gérer les redirections <, >, <<, >> et les pipes |.',
  'Gérer les variables d’environnement et $? .',
  'Gérer ctrl-C, ctrl-D et ctrl-\\ comme dans bash.',
]

const CONSTRAINTS = [
  { icon: 'Ban', text: 'Aucune fuite mémoire tolérée (hors readline).' },
  { icon: 'Ruler', text: 'Norminette : 25 lignes max par fonction, 5 fonctions par fichier.' },
  { icon: 'FileCode', text: 'Un Makefile avec les règles all, clean, fclean, re, bonus.' },
  { icon: 'Users', text: 'Projet en binôme — les deux membres doivent défendre le code.' },
  { icon: 'ShieldAlert', text: 'Une seule variable globale autorisée, pour le numéro de signal reçu.' },
]

const DISCUSSIONS = [
  { user: 'mehdi42', avatar: 'https://i.pravatar.cc/64?img=33', time: 'il y a 3 h', text: 'Petit rappel : `waitpid` dans une boucle sur tous les enfants, sinon vos zombies vous hanteront à la correction.', votes: 24 },
  { user: 'ines_dev', avatar: 'https://i.pravatar.cc/64?img=47', time: 'il y a 1 j', text: 'Quelqu’un a réussi à gérer le heredoc avec expansion des variables ? Je bloque sur le cas `<< "EOF"`.', votes: 11 },
  { user: 'chaimacoder', avatar: 'https://i.pravatar.cc/64?img=45', time: 'il y a 2 j', text: 'Astuce : testez avec `cat | cat | ls`, c’est le cas qui casse 80 % des minishells.', votes: 47 },
]

const CORRECTIONS = [
  { peer: 'nour_dev', avatar: 'https://i.pravatar.cc/64?img=32', date: '28 août 2026', score: 92, comment: 'Parsing solide, gestion des quotes impeccable. Quelques leaks sur les heredocs imbriqués.' },
  { peer: 'skhalifa', avatar: 'https://i.pravatar.cc/64?img=26', date: '26 août 2026', score: 78, comment: 'Bonne architecture mais `exec.c` fait 400 lignes — à découper avant la prochaine soutenance.' },
]

export default function ProjectDetail() {
  const { slug } = useParams()
  const p = projects.find((x) => x.slug === slug) || projects[2]
  const [tab, setTab] = useState('description')

  usePageHeader(
    { title: p.name, breadcrumb: [{ label: 'Mes projets', to: '/projects' }, { label: p.name }] },
    [p.slug],
  )

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
                    Ce projet consiste à créer un shell simple. Tu vas plonger dans les processus et les
                    descripteurs de fichiers, et découvrir pourquoi bash est un exploit d'ingénierie
                    plus qu'un simple programme.
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
                    {['libft', 'get_next_line', 'ft_printf', 'pipex'].map((r) => (
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

            {tab === 'instructions' && (
              <div className="space-y-5">
                <div className="rounded-lg border border-info/25 bg-info/[0.06] p-4">
                  <p className="flex gap-2.5 text-[12.5px] leading-relaxed text-ink-soft">
                    <Icon name="Info" size={15} className="mt-0.5 shrink-0 text-info" />
                    Ton code est exécuté dans un conteneur Ubuntu 22.04 isolé, sans accès réseau,
                    limité à 1 vCPU et 512 Mo de RAM.
                  </p>
                </div>
                {[
                  { n: '01', t: 'Cloner le dépôt', c: 'git clone git@root404.tn:abdeljalil/minishell.git' },
                  { n: '02', t: 'Compiler', c: 'make -j4' },
                  { n: '03', t: 'Vérifier la norme', c: 'norminette src/ includes/' },
                  { n: '04', t: 'Chasser les fuites', c: 'valgrind --leak-check=full ./minishell' },
                  { n: '05', t: 'Soumettre', c: 'root404 submit minishell' },
                ].map((s) => (
                  <div key={s.n} className="flex gap-4">
                    <span className="grid h-8 w-8 shrink-0 place-items-center rounded-lg border border-line bg-root-850 font-mono text-[11px] font-bold text-brand-500">
                      {s.n}
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="text-[13px] font-semibold text-ink">{s.t}</p>
                      <pre className="mt-2 overflow-x-auto rounded-lg border border-line bg-[#080D12] px-3.5 py-2.5 font-mono text-[12px] text-ok">
                        <code>$ {s.c}</code>
                      </pre>
                    </div>
                  </div>
                ))}
              </div>
            )}

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
                      <Button size="sm" icon="Send">Publier</Button>
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
                { label: 'Moulinette', value: `${passed}/${moulinetteTests.length}`, tone: 'ok', icon: 'Cpu' },
                { label: 'Peer Review', value: '2 / 3', tone: 'brand', icon: 'Users' },
                { label: 'AI Review', value: '81/100', tone: 'info', icon: 'Sparkles' },
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
