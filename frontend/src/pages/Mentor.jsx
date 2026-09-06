import { useEffect, useRef, useState } from 'react'
import usePageHeader from '../hooks/usePageHeader'
import Icon from '../components/ui/Icon'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import Avatar from '../components/ui/Avatar'
import ProgressBar from '../components/ui/ProgressBar'
import { aiConversation, aiLevels, currentUser, skillGraph } from '../data/mock'

const CANNED = [
  "Bonne question. Reformule-moi d'abord le problème avec tes propres mots : qu'attends-tu exactement en sortie, et qu'obtiens-tu à la place ?",
  "Je ne vais pas écrire ce code à ta place. Mais dis-moi : que se passe-t-il si tu traces la valeur juste avant l'appel ? Que devrais-tu voir ?",
  "Le concept sous-jacent ici s'appelle l'ownership de la mémoire. Qui alloue ? Qui libère ? Tant que cette réponse n'est pas nette, le bug reviendra.",
  "Essaie de réduire le cas au minimum reproductible : trois lignes qui plantent, sans le reste. Tu trouveras souvent la réponse en le faisant.",
]

const SUGGESTIONS = [
  { icon: 'Bug', text: 'Pourquoi mon programme segfault ?' },
  { icon: 'BookOpen', text: 'Explique-moi les pointeurs de fonction' },
  { icon: 'Gauge', text: 'Comment réduire la complexité de ma fonction ?' },
  { icon: 'Droplet', text: 'Comment traquer une fuite mémoire ?' },
]

function Bubble({ m }) {
  if (m.role === 'user') {
    return (
      <div className="flex flex-row-reverse gap-3">
        <Avatar src={currentUser.avatar} name={currentUser.displayName} size="sm" />
        <div className="max-w-[78%] rounded-xl rounded-tr-sm bg-brand-500/15 px-4 py-3 text-[13.5px] leading-relaxed text-ink">
          {m.text}
        </div>
      </div>
    )
  }
  return (
    <div className="flex gap-3">
      <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full border border-brand-500/30 bg-brand-500/12 text-brand-500">
        <Icon name="Sparkles" size={15} />
      </span>
      <div className="max-w-[78%]">
        <div className="rounded-xl rounded-tl-sm border border-line bg-root-800 px-4 py-3">
          <p className="text-[13.5px] leading-relaxed text-ink-soft">{m.text}</p>
          {m.list && (
            <ol className="mt-3 space-y-2">
              {m.list.map((q, i) => (
                <li key={i} className="flex gap-2.5 text-[13px] leading-relaxed text-ink">
                  <span className="grid h-5 w-5 shrink-0 place-items-center rounded-full bg-brand-500/15 font-mono text-[10px] font-bold text-brand-500">
                    {i + 1}
                  </span>
                  {q}
                </li>
              ))}
            </ol>
          )}
          {m.footer && (
            <p className="mt-3 border-t border-line pt-3 text-[12.5px] italic leading-relaxed text-ink-dim">
              {m.footer}
            </p>
          )}
        </div>
        {m.chips && (
          <div className="mt-2.5 flex flex-wrap gap-2">
            {m.chips.map((c) => (
              <button
                key={c}
                className="rounded-full border border-brand-500/30 bg-brand-500/[0.07] px-3 py-1.5 text-[11.5px] font-medium text-brand-400 transition-colors hover:bg-brand-500/15"
              >
                {c}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default function Mentor() {
  usePageHeader({ title: 'Assistant IA' })

  const [messages, setMessages] = useState(aiConversation)
  const [draft, setDraft] = useState('')
  const [typing, setTyping] = useState(false)
  const [level, setLevel] = useState(2)
  const scrollRef = useRef(null)

  useEffect(() => {
    const el = scrollRef.current
    if (el) el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' })
  }, [messages, typing])

  const ask = (text) => {
    if (!text.trim()) return
    setMessages((m) => [...m, { role: 'user', text: text.trim() }])
    setDraft('')
    setTyping(true)
    setTimeout(() => {
      setTyping(false)
      setMessages((m) => [...m, { role: 'ai', text: CANNED[m.length % CANNED.length] }])
    }, 1100)
  }

  const gaps = skillGraph
    .flatMap((g) => g.skills.map((s) => ({ ...s, group: g.group, color: g.color })))
    .sort((a, b) => a.value - b.value)
    .slice(0, 4)

  return (
    <div className="container-page py-6">
      <div className="grid gap-5 xl:grid-cols-[1fr_320px]">
        {/* ---------- Chat ---------- */}
        <section className="card flex h-[calc(100vh-140px)] min-h-[560px] flex-col overflow-hidden">
          <header className="flex shrink-0 items-center gap-3 border-b border-line px-5 py-3.5">
            <span className="relative grid h-9 w-9 place-items-center rounded-lg bg-brand-500/12 text-brand-500">
              <Icon name="Sparkles" size={18} />
              <span className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full bg-ok ring-2 ring-root-800" />
            </span>
            <div className="min-w-0">
              <h1 className="text-[14px] font-bold text-ink">AI Mentor 2.0</h1>
              <p className="text-[11.5px] text-ink-dim">
                Guide socratique · contexte : <span className="font-mono text-ink-soft">minishell</span>
              </p>
            </div>
            <Badge tone="brand" className="ml-auto hidden sm:inline-flex">Niveau d'aide {level}/5</Badge>
            <button className="grid h-8 w-8 place-items-center rounded-md text-ink-dim hover:bg-white/[0.06] hover:text-ink" aria-label="Nouvelle conversation">
              <Icon name="RotateCcw" size={15} />
            </button>
          </header>

          <div ref={scrollRef} className="flex-1 space-y-5 overflow-y-auto p-5">
            <div className="rounded-lg border border-warn/25 bg-warn/[0.06] px-4 py-3">
              <p className="flex gap-2.5 text-[12px] leading-relaxed text-ink-soft">
                <Icon name="Info" size={14} className="mt-0.5 shrink-0 text-warn" />
                L'assistant ne donne jamais la solution finale d'un projet. Il pose des questions,
                explique des concepts et signale les schémas de copier-coller au système anti-triche.
              </p>
            </div>

            {messages.map((m, i) => <Bubble key={i} m={m} />)}

            {typing && (
              <div className="flex gap-3">
                <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full border border-brand-500/30 bg-brand-500/12 text-brand-500">
                  <Icon name="Sparkles" size={15} />
                </span>
                <div className="flex items-center gap-1.5 rounded-xl rounded-tl-sm border border-line bg-root-800 px-4 py-3.5">
                  {[0, 1, 2].map((i) => (
                    <span
                      key={i}
                      className="h-1.5 w-1.5 animate-pulse-glow rounded-full bg-brand-500"
                      style={{ animationDelay: `${i * 0.18}s` }}
                    />
                  ))}
                </div>
              </div>
            )}
                      </div>

          {/* Suggestions + composer */}
          <div className="shrink-0 border-t border-line p-4">
            <div className="no-scrollbar mb-3 flex gap-2 overflow-x-auto">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s.text}
                  onClick={() => ask(s.text)}
                  className="flex shrink-0 items-center gap-1.5 rounded-full border border-line bg-root-850 px-3 py-1.5 text-[11.5px] text-ink-dim transition-colors hover:border-brand-500/40 hover:text-brand-500"
                >
                  <Icon name={s.icon} size={12} /> {s.text}
                </button>
              ))}
            </div>
            <form
              onSubmit={(e) => { e.preventDefault(); ask(draft) }}
              className="flex items-end gap-2"
            >
              <div className="relative flex-1">
                <textarea
                  rows={1}
                  value={draft}
                  onChange={(e) => setDraft(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); ask(draft) }
                  }}
                  placeholder="Pose ta question… (Entrée pour envoyer)"
                  className="input h-auto max-h-32 resize-none py-2.5 pr-10"
                />
                <button type="button" aria-label="Joindre du code" className="absolute right-2.5 top-2.5 text-ink-faint hover:text-ink">
                  <Icon name="Code2" size={15} />
                </button>
              </div>
              <Button type="submit" className="h-10 w-10 shrink-0 !px-0" aria-label="Envoyer">
                <Icon name="Send" size={15} />
              </Button>
            </form>
          </div>
        </section>

        {/* ---------- Rail ---------- */}
        <aside className="space-y-4">
          <section className="card p-5">
            <h2 className="text-[13px] font-bold text-ink">Niveaux d'assistance</h2>
            <p className="mt-1.5 text-[11.5px] leading-relaxed text-ink-dim">
              Choisis jusqu'où l'assistant peut aller. Plus le niveau est haut, plus l'aide est
              explicite — et plus l'AI Dependency de ton Integrity Score augmente.
            </p>
            <ul className="mt-4 space-y-1.5">
              {aiLevels.map((l) => (
                <li key={l.n}>
                  <button
                    onClick={() => setLevel(l.n)}
                    className={`flex w-full items-center gap-2.5 rounded-lg border px-3 py-2.5 text-left transition-colors ${
                      level === l.n
                        ? 'border-brand-500/45 bg-brand-500/[0.09] text-brand-400'
                        : 'border-line text-ink-dim hover:border-line-strong hover:text-ink'
                    }`}
                  >
                    <span
                      className={`grid h-5 w-5 shrink-0 place-items-center rounded-full font-mono text-[10px] font-bold ${
                        level === l.n ? 'bg-brand-500 text-[#160A00]' : 'bg-white/[0.07]'
                      }`}
                    >
                      {l.n}
                    </span>
                    <span className="text-[12px] font-medium">{l.label}</span>
                  </button>
                </li>
              ))}
            </ul>
          </section>

          <section className="card p-5">
            <h2 className="flex items-center gap-2 text-[13px] font-bold text-ink">
              <Icon name="Radar" size={15} className="text-brand-500" /> Knowledge Gaps détectés
            </h2>
            <ul className="mt-4 space-y-3.5">
              {gaps.map((g) => (
                <li key={`${g.group}-${g.name}`}>
                  <div className="mb-1.5 flex items-center justify-between text-[11.5px]">
                    <span className="text-ink-soft">
                      {g.name} <span className="text-ink-faint">· {g.group}</span>
                    </span>
                    <span className="font-mono font-semibold" style={{ color: g.color }}>{g.value}%</span>
                  </div>
                  <ProgressBar value={g.value} color={g.color} height={4} />
                </li>
              ))}
            </ul>
            <Button variant="outline" size="sm" full className="mt-4" iconRight="ArrowRight">
              Micro-challenges suggérés
            </Button>
          </section>

          <section className="card p-5">
            <h2 className="flex items-center gap-2 text-[13px] font-bold text-ink">
              <Icon name="ShieldCheck" size={15} className="text-ok" /> AI Dependency
            </h2>
            <div className="mt-3 flex items-baseline gap-2">
              <span className="font-mono text-[26px] font-extrabold text-ok">Low</span>
              <span className="text-[11.5px] text-ink-dim">12 requêtes / 30 j.</span>
            </div>
            <ProgressBar value={18} color="#2ECC71" height={5} className="mt-3" />
            <p className="mt-3 text-[11px] leading-relaxed text-ink-faint">
              Une dépendance faible renforce ton Integrity Score et ta crédibilité en peer review.
            </p>
          </section>
        </aside>
      </div>
    </div>
  )
}
