import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import AuthLayout from './AuthLayout'
import Button from '../../components/ui/Button'
import Icon from '../../components/ui/Icon'
import ProgressBar from '../../components/ui/ProgressBar'

const CAMPUSES = ['Tunis', 'Sfax', 'Sousse']
const LEVELS = [
  { k: 'none', l: 'Jamais codé', d: 'Je pars de zéro, et c’est très bien.' },
  { k: 'some', l: 'Quelques bases', d: 'J’ai déjà écrit des scripts ou suivi des tutoriels.' },
  { k: 'good', l: 'À l’aise', d: 'Je code régulièrement, je veux structurer mes bases.' },
]

export default function Register() {
  const navigate = useNavigate()
  const [step, setStep] = useState(1)
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({ name: '', email: '', campus: 'Tunis', level: 'some', terms: false })

  useEffect(() => { document.title = 'Postuler — ROOT 404' }, [])

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }))

  const next = (e) => {
    e.preventDefault()
    if (step < 3) return setStep(step + 1)
    setLoading(true)
    setTimeout(() => navigate('/dashboard'), 1000)
  }

  return (
    <AuthLayout
      title="Rejoins la prochaine Piscine"
      subtitle="Quatre semaines intensives, aucun prérequis, aucun frais. Il ne reste que la volonté d'apprendre."
      footer={
        <>
          Déjà inscrit ?{' '}
          <Link to="/login" className="font-semibold text-brand-500 hover:underline">Se connecter</Link>
        </>
      }
    >
      <div className="mb-6">
        <div className="mb-2 flex items-center justify-between text-[11.5px]">
          <span className="text-ink-dim">Étape {step} sur 3</span>
          <span className="font-semibold text-brand-500">{Math.round((step / 3) * 100)}%</span>
        </div>
        <ProgressBar value={(step / 3) * 100} height={4} />
      </div>

      <form onSubmit={next} className="space-y-4">
        {step === 1 && (
          <>
            <div>
              <label htmlFor="name" className="mb-1.5 block text-[12.5px] font-semibold text-ink">Nom complet</label>
              <div className="relative">
                <Icon name="User" size={15} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-ink-faint" />
                <input id="name" required value={form.name} onChange={(e) => set('name', e.target.value)} placeholder="Ton nom et prénom" className="input h-11 pl-9" />
              </div>
            </div>
            <div>
              <label htmlFor="mail" className="mb-1.5 block text-[12.5px] font-semibold text-ink">Adresse e-mail</label>
              <div className="relative">
                <Icon name="Mail" size={15} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-ink-faint" />
                <input id="mail" type="email" required value={form.email} onChange={(e) => set('email', e.target.value)} placeholder="ton.nom@exemple.tn" className="input h-11 pl-9" />
              </div>
            </div>
            <div>
              <label className="mb-1.5 block text-[12.5px] font-semibold text-ink">Campus souhaité</label>
              <div className="grid grid-cols-3 gap-2">
                {CAMPUSES.map((c) => (
                  <button
                    key={c}
                    type="button"
                    onClick={() => set('campus', c)}
                    className={`rounded-lg border px-3 py-2.5 text-[12.5px] font-medium transition-colors ${
                      form.campus === c ? 'border-brand-500 bg-brand-500/10 text-brand-500' : 'border-line text-ink-dim hover:text-ink'
                    }`}
                  >
                    {c}
                  </button>
                ))}
              </div>
            </div>
          </>
        )}

        {step === 2 && (
          <div className="space-y-2.5">
            <label className="block text-[12.5px] font-semibold text-ink">Où en es-tu aujourd'hui ?</label>
            {LEVELS.map((l) => (
              <button
                key={l.k}
                type="button"
                onClick={() => set('level', l.k)}
                className={`flex w-full items-start gap-3 rounded-lg border p-4 text-left transition-colors ${
                  form.level === l.k ? 'border-brand-500 bg-brand-500/[0.08]' : 'border-line hover:border-line-strong'
                }`}
              >
                <span
                  className={`mt-0.5 grid h-4.5 h-[18px] w-[18px] shrink-0 place-items-center rounded-full border-2 ${
                    form.level === l.k ? 'border-brand-500' : 'border-line-strong'
                  }`}
                >
                  {form.level === l.k && <span className="h-2 w-2 rounded-full bg-brand-500" />}
                </span>
                <span>
                  <span className="block text-[13px] font-semibold text-ink">{l.l}</span>
                  <span className="mt-0.5 block text-[12px] leading-relaxed text-ink-dim">{l.d}</span>
                </span>
              </button>
            ))}
            <p className="flex items-start gap-2 pt-2 text-[11.5px] leading-relaxed text-ink-faint">
              <Icon name="Info" size={13} className="mt-0.5 shrink-0 text-info" />
              Cette réponse n'influence pas ton admission — elle calibre seulement tes premiers exercices.
            </p>
          </div>
        )}

        {step === 3 && (
          <div className="space-y-4">
            <div className="rounded-lg border border-line bg-root-850 p-4">
              <h3 className="text-[13px] font-semibold text-ink">Récapitulatif</h3>
              <dl className="mt-3 space-y-2 text-[12.5px]">
                {[
                  ['Nom', form.name || '—'],
                  ['E-mail', form.email || '—'],
                  ['Campus', form.campus],
                  ['Niveau', LEVELS.find((l) => l.k === form.level)?.l],
                  ['Session', 'Piscine — octobre 2026'],
                ].map(([k, v]) => (
                  <div key={k} className="flex justify-between gap-4">
                    <dt className="text-ink-dim">{k}</dt>
                    <dd className="truncate font-medium text-ink">{v}</dd>
                  </div>
                ))}
              </dl>
            </div>

            <label className="flex cursor-pointer items-start gap-2.5">
              <input
                type="checkbox"
                required
                checked={form.terms}
                onChange={(e) => set('terms', e.target.checked)}
                className="mt-0.5 h-4 w-4 shrink-0 accent-[#F8851F]"
              />
              <span className="text-[12px] leading-relaxed text-ink-dim">
                J'accepte les conditions d'utilisation, la politique de confidentialité et le règlement
                anti-triche de ROOT 404.
              </span>
            </label>
          </div>
        )}

        <div className="flex gap-2.5 pt-2">
          {step > 1 && (
            <Button type="button" variant="outline" size="lg" icon="ArrowLeft" onClick={() => setStep(step - 1)}>
              Retour
            </Button>
          )}
          <Button type="submit" size="lg" full loading={loading} iconRight="ArrowRight">
            {step === 3 ? 'Envoyer ma candidature' : 'Continuer'}
          </Button>
        </div>
      </form>
    </AuthLayout>
  )
}
