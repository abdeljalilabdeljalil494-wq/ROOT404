import { useEffect, useState } from 'react'
import Icon from '../ui/Icon'
import SectionHeading from '../ui/SectionHeading'
import Badge from '../ui/Badge'
import ProgressBar from '../ui/ProgressBar'

const LINES = [
  { p: '$', t: 'root404 submit minishell', c: 'text-ink' },
  { p: '›', t: 'Création du conteneur Ubuntu 22.04…', c: 'text-ink-dim' },
  { p: '›', t: 'Sandbox durci : réseau off · 512 Mo · 1 vCPU', c: 'text-ink-dim' },
  { p: '✓', t: 'Norminette — OK', c: 'text-ok' },
  { p: '✓', t: 'Valgrind — 0 bytes lost', c: 'text-ok' },
  { p: '✓', t: 'Tests fonctionnels — 38/38', c: 'text-ok' },
  { p: '⚠', t: 'Heredoc — 2 cas limites', c: 'text-warn' },
  { p: '›', t: 'Score Moulinette : 98/100', c: 'text-brand-400' },
  { p: '›', t: 'Peer review requis → matchmaking…', c: 'text-ink-dim' },
]

const SYSTEMS = [
  { icon: 'CircleDot', title: 'Black Hole', text: 'Un compte à rebours de survie par parcours, avec zone d’avertissement et plan de rattrapage proposé par l’IA.', tone: '#F8851F' },
  { icon: 'Network', title: 'Skill Graph', text: 'Un profil de compétences dynamique alimenté par la Moulinette, les peer reviews et les challenges.', tone: '#3B9EFF' },
  { icon: 'ShieldCheck', title: 'Integrity Score', text: 'AST fingerprinting, patterns de frappe et dépendance à l’IA — toute sanction passe par un humain.', tone: '#2ECC71' },
  { icon: 'Flame', title: 'Anti-Burnout', text: 'Le streak surveille ta charge réelle et propose une session allégée avant l’épuisement.', tone: '#E5484D' },
]

export default function SystemsShowcase() {
  const [shown, setShown] = useState(0)

  useEffect(() => {
    if (shown >= LINES.length) return
    const id = setTimeout(() => setShown((s) => s + 1), shown === 0 ? 400 : 480)
    return () => clearTimeout(id)
  }, [shown])

  return (
    <section className="border-t border-line bg-root-900 py-20 sm:py-24">
      <div className="container-page grid items-center gap-12 lg:grid-cols-2 lg:gap-16">
        {/* Terminal mock */}
        <div className="order-2 lg:order-1">
          <div className="overflow-hidden rounded-xl border border-line bg-[#080D12] shadow-pop">
            <div className="flex items-center gap-2 border-b border-line bg-root-850 px-4 py-2.5">
              <span className="flex gap-1.5">
                <span className="h-2.5 w-2.5 rounded-full bg-[#FF5F57]" />
                <span className="h-2.5 w-2.5 rounded-full bg-[#FEBC2E]" />
                <span className="h-2.5 w-2.5 rounded-full bg-[#28C840]" />
              </span>
              <span className="ml-2 font-mono text-[11px] text-ink-dim">
                abdeljalil@root404 — moulinette
              </span>
              <Badge tone="ok" className="ml-auto" dot>Live</Badge>
            </div>

            <div className="min-h-[268px] space-y-1.5 p-4 font-mono text-[11.5px] leading-relaxed sm:text-[12.5px]">
              {LINES.slice(0, shown).map((l, i) => (
                <div key={i} className="flex animate-fade-in gap-2.5">
                  <span className={`shrink-0 ${l.c}`}>{l.p}</span>
                  <span className={l.c}>{l.t}</span>
                </div>
              ))}
              {shown >= LINES.length ? (
                <div className="mt-4 rounded-lg border border-ok/25 bg-ok/[0.07] p-3">
                  <div className="flex items-center gap-2 text-ok">
                    <Icon name="CheckCircle2" size={15} />
                    <span className="text-[12px] font-bold">RÉSULTAT FINAL — 98 / 100</span>
                  </div>
                  <ProgressBar value={98} color="#2ECC71" height={5} className="mt-2.5" />
                </div>
              ) : (
                <span className="inline-block h-3.5 w-2 animate-blink bg-brand-500 align-middle" />
              )}
            </div>
          </div>
        </div>

        {/* Copy */}
        <div className="order-1 lg:order-2">
          <SectionHeading
            align="left"
            eyebrow="ROOT 404 Ultimate"
            title="Plus qu'une académie —"
            highlight="un OS d'apprentissage"
            text="Learn, Compete, Community : trois piliers reliés par un seul Code Engine. Chaque soumission alimente ton niveau, ta réputation et ton portfolio public."
          />

          <div className="mt-9 grid gap-3 sm:grid-cols-2">
            {SYSTEMS.map((s) => (
              <div
                key={s.title}
                className="rounded-xl border border-line bg-root-800/70 p-4 transition-colors hover:border-line-strong"
              >
                <span
                  className="grid h-9 w-9 place-items-center rounded-lg"
                  style={{ background: `${s.tone}18`, color: s.tone }}
                >
                  <Icon name={s.icon} size={18} />
                </span>
                <h3 className="mt-3 text-[13px] font-bold text-white">{s.title}</h3>
                <p className="mt-1.5 text-[12px] leading-relaxed text-ink-dim">{s.text}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
