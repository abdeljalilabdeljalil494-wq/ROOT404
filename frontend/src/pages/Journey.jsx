import usePageHeader from '../hooks/usePageHeader'
import Icon from '../components/ui/Icon'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import ProgressBar from '../components/ui/ProgressBar'
import { journeyStages, currentUser } from '../data/mock'

const STATUS = {
  done: { color: '#2ECC71', icon: 'CheckCircle2', label: 'Terminé' },
  current: { color: '#F8851F', icon: 'Loader', label: 'En cours' },
  next: { color: '#3B9EFF', icon: 'Unlock', label: 'Débloqué' },
  locked: { color: '#495562', icon: 'Lock', label: 'Verrouillé' },
}

export default function Journey() {
  usePageHeader({ title: 'Code Journey' })

  return (
    <div className="container-page space-y-5 py-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-[24px] font-extrabold tracking-tight text-white">Code Journey</h1>
          <p className="mt-1.5 text-[13px] text-ink-dim">
            Ta carte de progression, du LEVEL 00 au projet final — recalculée à chaque validation.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge tone="brand">Niveau {currentUser.level.toFixed(2)}</Badge>
          <Button to="/skills" variant="outline" size="sm" icon="Network">Skill Graph</Button>
        </div>
      </div>

      {/* Global track */}
      <section className="card p-6">
        <div className="flex items-center justify-between text-[12px]">
          <span className="font-semibold text-ink">Progression globale du cursus</span>
          <span className="font-mono font-bold text-brand-500">
            {Math.round(journeyStages.reduce((a, s) => a + s.progress, 0) / journeyStages.length)}%
          </span>
        </div>
        <ProgressBar
          value={journeyStages.reduce((a, s) => a + s.progress, 0) / journeyStages.length}
          height={8}
          className="mt-3"
        />
        <div className="mt-4 flex flex-wrap gap-x-6 gap-y-2 text-[11.5px] text-ink-dim">
          <span className="flex items-center gap-1.5"><Icon name="CheckCircle2" size={13} className="text-ok" /> 2 étapes terminées</span>
          <span className="flex items-center gap-1.5"><Icon name="Loader" size={13} className="text-brand-500" /> 1 en cours</span>
          <span className="flex items-center gap-1.5"><Icon name="Lock" size={13} /> 3 verrouillées</span>
          <span className="flex items-center gap-1.5"><Icon name="CalendarCheck" size={13} /> Fin estimée : mars 2027</span>
        </div>
      </section>

      {/* Vertical timeline */}
      <section className="relative">
        <div aria-hidden className="absolute bottom-6 left-[27px] top-6 w-px bg-line sm:left-[31px]" />
        <ol className="space-y-4">
          {journeyStages.map((s) => {
            const st = STATUS[s.status]
            return (
              <li key={s.id} className="relative flex gap-4 sm:gap-5">
                <span
                  className="relative z-10 mt-1 grid h-14 w-14 shrink-0 place-items-center rounded-xl border-2 sm:h-[62px] sm:w-[62px]"
                  style={{
                    borderColor: `${st.color}55`,
                    background: `${st.color}12`,
                    color: st.color,
                    boxShadow: s.status === 'current' ? `0 0 26px -6px ${st.color}` : 'none',
                  }}
                >
                  <Icon
                    name={st.icon}
                    size={22}
                    className={s.status === 'current' ? 'animate-spin [animation-duration:6s]' : ''}
                  />
                </span>

                <div
                  className={`card flex-1 p-5 transition-colors ${
                    s.status === 'locked' ? 'opacity-55' : 'hover:border-line-strong'
                  }`}
                >
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <h2 className="text-[15px] font-bold text-ink">{s.title}</h2>
                        <span
                          className="badge"
                          style={{ background: `${st.color}18`, color: st.color }}
                        >
                          {st.label}
                        </span>
                      </div>
                      <p className="mt-1 text-[12px] text-ink-dim">{s.projects} projets dans cette étape</p>
                    </div>
                    <span className="font-mono text-[16px] font-extrabold" style={{ color: st.color }}>
                      {s.progress}%
                    </span>
                  </div>

                  <ProgressBar value={s.progress} color={st.color} height={5} className="mt-3.5" />

                  <div className="mt-4 flex flex-wrap items-center gap-1.5">
                    <span className="text-[10.5px] uppercase tracking-wider text-ink-faint">Compétences</span>
                    {s.skills.map((k) => <span key={k} className="chip">{k}</span>)}
                  </div>

                  {s.status === 'current' && (
                    <div className="mt-4 flex flex-wrap items-center justify-between gap-3 rounded-lg border border-brand-500/25 bg-brand-500/[0.07] p-3.5">
                      <p className="text-[12px] text-ink-soft">
                        Prochain jalon : valider <span className="font-mono font-semibold text-ink">minishell</span> pour débloquer Memory / Systems.
                      </p>
                      <Button to="/projects/minishell" size="sm" iconRight="ArrowRight">Continuer</Button>
                    </div>
                  )}
                  {s.status === 'locked' && (
                    <p className="mt-4 flex items-center gap-2 text-[11.5px] text-ink-faint">
                      <Icon name="Lock" size={12} /> Termine l'étape précédente pour débloquer.
                    </p>
                  )}
                </div>
              </li>
            )
          })}
        </ol>
      </section>

      {/* Final */}
      <section className="card relative overflow-hidden p-8 text-center">
        <div aria-hidden className="absolute inset-0 bg-gradient-to-b from-brand-500/[0.09] to-transparent" />
        <div className="relative">
          <Icon name="Trophy" size={34} className="mx-auto text-brand-500" />
          <h2 className="mt-3 text-[18px] font-extrabold text-white">LEVEL 10+ — Advanced Developer</h2>
          <p className="mx-auto mt-2 max-w-md text-[13px] leading-relaxed text-ink-dim">
            Au-delà du tronc commun s'ouvrent le mentorat, les Hiring Challenges et le portfolio
            vérifié partagé avec les entreprises partenaires.
          </p>
        </div>
      </section>
    </div>
  )
}
