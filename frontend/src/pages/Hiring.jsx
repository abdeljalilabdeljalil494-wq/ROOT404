import { useState } from 'react'
import usePageHeader from '../hooks/usePageHeader'
import Icon from '../components/ui/Icon'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import { hiringService } from '../services/api'

const COMPANIES = [
  { id: 'c1', name: 'InstaDeep', sector: 'AI', location: 'Tunis', positions: 5, logo: 'ID' },
  { id: 'c2', name: 'Talan Tunisie', sector: 'SRE', location: 'Tunis', positions: 3, logo: 'TA' },
  { id: 'c3', name: 'Expensya', sector: 'FinTech', location: 'Tunis', positions: 8, logo: 'EX' },
  { id: 'c4', name: 'Kaoun', sector: 'FinTech', location: 'Tunis', positions: 2, logo: 'KA' },
]

const CHALLENGES = [
  { id: 'hc1', company: 'InstaDeep', title: 'Optimise un pipeline de données', difficulty: 4, xp: 2000, applicants: 24, deadline: '01 oct. 2026', tags: ['Python', 'Data'] },
  { id: 'hc2', company: 'Talan', title: 'Débug un microservice en prod', difficulty: 5, xp: 3000, applicants: 18, deadline: '25 sept. 2026', tags: ['Docker', 'SRE'] },
  { id: 'hc3', company: 'Expensya', title: 'Refactor le moteur de facturation', difficulty: 3, xp: 1800, applicants: 31, deadline: '10 oct. 2026', tags: ['C++', 'Algo'] },
]

export default function Hiring() {
  usePageHeader({ title: 'Portail Emploi', breadcrumb: [{ label: 'Emploi' }] })
  const [tab, setTab] = useState('challenges')

  return (
    <div className="container-page space-y-6 py-6">
      {/* Header */}
      <div className="card relative overflow-hidden">
        <div aria-hidden className="absolute inset-0 bg-gradient-to-br from-brand-500/[0.12] via-transparent to-info/[0.12]" />
        <div className="relative p-6 lg:p-8">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <div className="flex items-center gap-3">
                <span className="grid h-11 w-11 place-items-center rounded-xl bg-brand-500/15 text-brand-500">
                  <Icon name="Briefcase" size={22} />
                </span>
                <h1 className="text-[26px] font-extrabold tracking-tight text-white">Portail Emploi & Partenaires</h1>
                <Badge tone="brand">12 entreprises</Badge>
              </div>
              <p className="mt-3 max-w-2xl text-[13px] leading-relaxed text-ink-soft">
                Ton portfolio ROOT 404 est vérifiable et basé sur des projets réels. Les entreprises partenaires recrutent directement depuis la plateforme — pas de CV bidon, juste du code qui marche.
              </p>
            </div>
            <div className="flex gap-2">
              <Button icon="FileText">Mon portfolio</Button>
              <Button variant="outline" icon="Calendar">Partner Fair — 15 oct.</Button>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        {[
          { k: 'challenges', l: 'Hiring Challenges', c: CHALLENGES.length },
          { k: 'companies', l: 'Entreprises', c: COMPANIES.length },
          { k: 'fair', l: 'Partner Fair' },
        ].map((t) => (
          <button
            key={t.k}
            onClick={() => setTab(t.k)}
            className={`flex items-center gap-2 rounded-lg border px-4 py-2 text-[13px] font-medium transition-colors ${
              tab === t.k ? 'border-brand-500/50 bg-brand-500/10 text-brand-400' : 'border-line text-ink-dim hover:border-line-strong hover:text-ink'
            }`}
          >
            {t.l} {t.c != null && <span className="rounded-full bg-white/10 px-1.5 py-0.5 text-[10px]">{t.c}</span>}
          </button>
        ))}
      </div>

      {tab === 'challenges' && (
        <div className="grid gap-4 lg:grid-cols-2">
          {CHALLENGES.map((ch) => (
            <div key={ch.id} className="card p-5 transition-all hover:-translate-y-0.5 hover:border-brand-500/30">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-[14px] font-bold text-ink">{ch.title}</h3>
                    <Badge tone="brand">{ch.company}</Badge>
                  </div>
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {ch.tags.map((tag) => (
                      <span key={tag} className="chip text-[10px]">{tag}</span>
                    ))}
                  </div>
                </div>
                <span className="font-mono text-[12px] font-bold text-brand-500">+{ch.xp} XP</span>
              </div>
              <div className="mt-4 flex items-center justify-between border-t border-line pt-3 text-[11.5px] text-ink-dim">
                <span className="flex items-center gap-1.5"><Icon name="Users" size={12} /> {ch.applicants} candidats</span>
                <span className="flex items-center gap-1.5"><Icon name="Clock" size={12} /> {ch.deadline}</span>
                <span className="flex items-center gap-1"><Icon name="Star" size={12} className="text-warn" /> {ch.difficulty}/5</span>
              </div>
              <Button size="sm" full className="mt-4" iconRight="ArrowRight">Postuler avec mon portfolio</Button>
            </div>
          ))}
        </div>
      )}

      {tab === 'companies' && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {COMPANIES.map((co) => (
            <div key={co.id} className="card p-5 text-center">
              <span className="mx-auto grid h-12 w-12 place-items-center rounded-xl bg-root-750 font-mono text-[14px] font-bold text-brand-500">{co.logo}</span>
              <h3 className="mt-3 text-[14px] font-bold text-ink">{co.name}</h3>
              <p className="mt-1 text-[11.5px] text-ink-dim">{co.sector} · {co.location}</p>
              <Badge tone="ok" className="mt-3">{co.positions} postes ouverts</Badge>
              <Button variant="outline" size="sm" full className="mt-4">Voir les offres</Button>
            </div>
          ))}
        </div>
      )}

      {tab === 'fair' && (
        <div className="card p-6">
          <h2 className="flex items-center gap-2 text-[16px] font-bold text-ink">
            <Icon name="Calendar" size={18} className="text-brand-500" /> ROOT 404 Partner Fair — Automne 2026
          </h2>
          <p className="mt-2 text-[13px] text-ink-dim">15 octobre 2026 · Campus Tunis · 12 entreprises · 47 postes</p>
          <div className="mt-6 grid gap-6 lg:grid-cols-2">
            <div>
              <h3 className="text-[13px] font-bold text-ink">Workshops</h3>
              <ul className="mt-3 space-y-2">
                <li className="flex items-center gap-3 rounded-lg border border-line bg-root-850 p-3">
                  <Icon name="Mic" size={14} className="text-brand-500" />
                  <div className="flex-1"><p className="text-[12.5px] font-medium text-ink">Comment réussir un entretien système</p><p className="text-[11px] text-ink-dim">Talan · 10:00</p></div>
                </li>
                <li className="flex items-center gap-3 rounded-lg border border-line bg-root-850 p-3">
                  <Icon name="Server" size={14} className="text-info" />
                  <div className="flex-1"><p className="text-[12.5px] font-medium text-ink">De 0 à 10k utilisateurs : infra</p><p className="text-[11px] text-ink-dim">Expensya · 14:00</p></div>
                </li>
              </ul>
            </div>
            <div className="rounded-lg border border-brand-500/25 bg-brand-500/[0.06] p-4">
              <p className="text-[12px] font-bold uppercase tracking-wider text-brand-400">Stats édition précédente</p>
              <div className="mt-3 grid grid-cols-3 gap-4 text-center">
                <div><p className="font-mono text-[22px] font-extrabold text-white">12</p><p className="text-[11px] text-ink-dim">Entreprises</p></div>
                <div><p className="font-mono text-[22px] font-extrabold text-white">47</p><p className="text-[11px] text-ink-dim">Postes</p></div>
                <div><p className="font-mono text-[22px] font-extrabold text-brand-500">23</p><p className="text-[11px] text-ink-dim">Recrutés</p></div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
