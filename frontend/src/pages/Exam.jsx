import { useState } from 'react'
import usePageHeader from '../hooks/usePageHeader'
import Icon from '../components/ui/Icon'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import ProgressBar from '../components/ui/ProgressBar'

const TRACKS = [
  { id: 'c', name: 'C Programming', exams: 24, next_gate: 'Level 3.00', color: '#3B9EFF', icon: 'Code2' },
  { id: 'algo', name: 'Algorithms', exams: 18, next_gate: 'Level 5.00', color: '#F8851F', icon: 'GitBranch' },
  { id: 'system', name: 'Systems', exams: 15, next_gate: 'Level 7.00', color: '#2ECC71', icon: 'Server' },
]

const GATES = [
  { level: '3.00', track: 'C', status: 'passed', score: 85 },
  { level: '5.00', track: 'Algo', status: 'available', score: null },
  { level: '7.00', track: 'Systems', status: 'locked', score: null },
  { level: '10.00', track: 'Final', status: 'locked', score: null },
]

const HISTORY = [
  { id: 'exam_123', track: 'C', date: '15 août 2026', score: 85, passed: true, exercises: 4 },
  { id: 'exam_124', track: 'Algo', date: '20 août 2026', score: 92, passed: true, exercises: 3 },
]

export default function Exam() {
  usePageHeader({ title: 'Exam Mode', breadcrumb: [{ label: 'Examens' }] })
  const [starting, setStarting] = useState(false)

  const startExam = () => {
    setStarting(true)
    setTimeout(() => setStarting(false), 2000)
  }

  return (
    <div className="container-page space-y-6 py-6">
      {/* Hero */}
      <div className="card relative overflow-hidden">
        <div aria-hidden className="absolute inset-0 bg-gradient-to-br from-danger/[0.12] via-transparent to-brand-500/[0.12]" />
        <div className="relative p-6 lg:p-8">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div className="flex items-center gap-3">
              <span className="grid h-11 w-11 place-items-center rounded-xl bg-danger/15 text-danger">
                <Icon name="ShieldAlert" size={22} />
              </span>
              <div>
                <h1 className="text-[26px] font-extrabold tracking-tight text-white">Exam Mode</h1>
                <p className="mt-1 text-[13px] text-ink-dim">Environnement verrouillé · correction peer obligatoire · banque aléatoire</p>
              </div>
            </div>
            <div className="flex gap-2">
              <Button icon="Play" onClick={startExam} loading={starting}>Lancer un exam</Button>
              <Button variant="outline" icon="History">Historique</Button>
            </div>
          </div>

          <div className="mt-6 grid gap-3 rounded-lg border border-warn/25 bg-warn/[0.06] p-4">
            <p className="flex gap-2.5 text-[12.5px] leading-relaxed text-ink-soft">
              <Icon name="Info" size={15} className="mt-0.5 shrink-0 text-warn" />
              Les exams sont des gates obligatoires pour passer certains niveaux. Chaque étudiant reçoit une combinaison différente d'exercices de même difficulté pour éviter la triche collective.
            </p>
          </div>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1fr_340px]">
        {/* Tracks */}
        <div className="space-y-4">
          <h2 className="text-[15px] font-bold text-ink">Parcours d'examens</h2>
          <div className="grid gap-4 sm:grid-cols-3">
            {TRACKS.map((t) => (
              <div key={t.id} className="card p-5 transition-all hover:-translate-y-1 hover:border-line-strong">
                <div className="flex items-center gap-3">
                  <span className="grid h-10 w-10 place-items-center rounded-lg" style={{ background: `${t.color}18`, color: t.color }}>
                    <Icon name={t.icon} size={18} />
                  </span>
                  <div>
                    <h3 className="text-[13.5px] font-bold text-ink">{t.name}</h3>
                    <p className="text-[11px] text-ink-dim">{t.exams} exams disponibles</p>
                  </div>
                </div>
                <div className="mt-4 flex items-center justify-between">
                  <span className="text-[11px] text-ink-faint">Prochain gate: {t.next_gate}</span>
                  <Badge tone="brand">{t.exams} exams</Badge>
                </div>
                <Button size="sm" variant="outline" full className="mt-4">Voir les sujets</Button>
              </div>
            ))}
          </div>

          {/* Gates */}
          <div className="card overflow-hidden">
            <header className="flex items-center justify-between border-b border-line px-5 py-3.5">
              <h3 className="flex items-center gap-2 text-[13.5px] font-semibold text-ink">
                <Icon name="Flag" size={15} className="text-brand-500" /> Gates de progression
              </h3>
              <Badge tone="muted">4 gates</Badge>
            </header>
            <div className="divide-y divide-line/70">
              {GATES.map((g) => (
                <div key={g.level} className="flex items-center gap-4 px-5 py-4">
                  <span className={`grid h-8 w-8 place-items-center rounded-full text-[12px] font-bold ${
                    g.status === 'passed' ? 'bg-ok/15 text-ok' : g.status === 'available' ? 'bg-brand-500/15 text-brand-500' : 'bg-white/5 text-ink-faint'
                  }`}>
                    <Icon name={g.status === 'passed' ? 'Check' : g.status === 'available' ? 'Play' : 'Lock'} size={14} />
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="text-[13px] font-semibold text-ink">Level {g.level} — {g.track}</p>
                    <p className="text-[11px] text-ink-dim">
                      {g.status === 'passed' ? `Validé avec ${g.score}%` : g.status === 'available' ? 'Disponible — lance l\'exam' : 'Verrouillé — complète le niveau précédent'}
                    </p>
                  </div>
                  <Badge tone={g.status === 'passed' ? 'ok' : g.status === 'available' ? 'brand' : 'muted'}>{g.status}</Badge>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <aside className="space-y-4">
          <div className="card p-5">
            <h3 className="text-[13px] font-bold text-ink">Règles Exam Mode</h3>
            <ul className="mt-3 space-y-2.5 text-[12px] text-ink-soft">
              <li className="flex gap-2"><Icon name="Ban" size={14} className="mt-0.5 shrink-0 text-danger" /> Pas d'accès internet</li>
              <li className="flex gap-2"><Icon name="Copy" size={14} className="mt-0.5 shrink-0 text-danger" /> Copier-coller externe désactivé</li>
              <li className="flex gap-2"><Icon name="Eye" size={14} className="mt-0.5 shrink-0 text-warn" /> Caméra optionnelle (avec consentement)</li>
              <li className="flex gap-2"><Icon name="Users" size={14} className="mt-0.5 shrink-0 text-brand-500" /> Peer review obligatoire après</li>
              <li className="flex gap-2"><Icon name="Shuffle" size={14} className="mt-0.5 shrink-0 text-info" /> Banque aléatoire par étudiant</li>
            </ul>
          </div>

          <div className="card overflow-hidden">
            <header className="border-b border-line px-5 py-3.5">
              <h3 className="text-[13px] font-bold text-ink">Historique récent</h3>
            </header>
            <ul className="divide-y divide-line/70">
              {HISTORY.map((h) => (
                <li key={h.id} className="flex items-center gap-3 px-5 py-3.5">
                  <span className={`grid h-8 w-8 place-items-center rounded-full ${h.passed ? 'bg-ok/15 text-ok' : 'bg-danger/15 text-danger'}`}>
                    <Icon name={h.passed ? 'CheckCircle2' : 'XCircle'} size={16} />
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="text-[12.5px] font-semibold text-ink">{h.track} — {h.exercises} exercices</p>
                    <p className="text-[11px] text-ink-faint">{h.date}</p>
                  </div>
                  <span className={`font-mono text-[13px] font-bold ${h.passed ? 'text-ok' : 'text-danger'}`}>{h.score}%</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="card p-5">
            <h3 className="text-[13px] font-bold text-ink">Prochain exam suggéré</h3>
            <div className="mt-3 rounded-lg border border-line bg-root-850 p-3.5">
              <p className="font-mono text-[12px] font-bold text-ink">Level 5.00 — Algo Gate</p>
              <p className="mt-1 text-[11.5px] text-ink-dim">3 exercices · 90 min · difficulté moyenne</p>
              <ProgressBar value={62} height={4} className="mt-3" />
              <p className="mt-2 text-[10.5px] text-ink-faint">Préparation: 62% — révise les arbres binaires</p>
            </div>
            <Button size="sm" full className="mt-4" icon="Play">Lancer la préparation</Button>
          </div>
        </aside>
      </div>
    </div>
  )
}
