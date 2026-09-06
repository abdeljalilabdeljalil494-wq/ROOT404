import { useState } from 'react'
import usePageHeader from '../hooks/usePageHeader'
import Icon from '../components/ui/Icon'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import Avatar from '../components/ui/Avatar'
import { currentUser } from '../data/mock'

const SECTIONS = [
  { key: 'profile', label: 'Profil', icon: 'User' },
  { key: 'account', label: 'Compte & sécurité', icon: 'Lock' },
  { key: 'notifications', label: 'Notifications', icon: 'Bell' },
  { key: 'appearance', label: 'Apparence', icon: 'Palette' },
  { key: 'privacy', label: 'Confidentialité', icon: 'Eye' },
  { key: 'api', label: 'API & Webhooks', icon: 'Webhook' },
]

function Field({ label, hint, children }) {
  return (
    <div className="grid gap-2 border-b border-line py-5 last:border-0 sm:grid-cols-[220px_1fr] sm:gap-6">
      <div>
        <label className="text-[13px] font-semibold text-ink">{label}</label>
        {hint && <p className="mt-1 text-[11.5px] leading-relaxed text-ink-dim">{hint}</p>}
      </div>
      <div>{children}</div>
    </div>
  )
}

function Toggle({ on, onChange, label }) {
  return (
    <button
      role="switch"
      aria-checked={on}
      aria-label={label}
      onClick={() => onChange(!on)}
      className={`relative h-6 w-11 shrink-0 rounded-full transition-colors ${on ? 'bg-brand-500' : 'bg-white/[0.12]'}`}
    >
      <span
        className={`absolute top-0.5 h-5 w-5 rounded-full bg-white transition-transform ${on ? 'translate-x-[22px]' : 'translate-x-0.5'}`}
      />
    </button>
  )
}

export default function Settings() {
  usePageHeader({ title: 'Paramètres' })
  const [section, setSection] = useState('profile')
  const [prefs, setPrefs] = useState({
    peerReview: true, moulinette: true, coalition: false, weekly: true, marketing: false,
    publicProfile: true, showEmail: false, leaderboard: true,
  })
  const set = (k) => (v) => setPrefs((p) => ({ ...p, [k]: v }))

  return (
    <div className="container-page py-6">
      <h1 className="text-[24px] font-extrabold tracking-tight text-white">Paramètres</h1>
      <p className="mt-1.5 text-[13px] text-ink-dim">Gère ton profil, ta sécurité et tes préférences.</p>

      <div className="mt-5 grid gap-5 lg:grid-cols-[230px_1fr]">
        {/* Nav */}
        <nav className="card h-fit p-2">
          {SECTIONS.map((s) => (
            <button
              key={s.key}
              onClick={() => setSection(s.key)}
              className={`flex w-full items-center gap-2.5 rounded-lg px-3 py-2.5 text-[13px] font-medium transition-colors ${
                section === s.key ? 'bg-brand-500/12 text-brand-500' : 'text-ink-soft hover:bg-white/[0.04]'
              }`}
            >
              <Icon name={s.icon} size={16} /> {s.label}
            </button>
          ))}
        </nav>

        <div className="card p-5 sm:p-6">
          {section === 'profile' && (
            <>
              <h2 className="text-[15px] font-bold text-ink">Profil public</h2>
              <div className="mt-2">
                <Field label="Photo de profil" hint="JPG ou PNG, 2 Mo maximum.">
                  <div className="flex items-center gap-4">
                    <Avatar src={currentUser.avatar} name={currentUser.fullName} size="lg" />
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline" icon="Upload">Changer</Button>
                      <Button size="sm" variant="ghost" className="text-danger">Supprimer</Button>
                    </div>
                  </div>
                </Field>
                <Field label="Nom complet">
                  <input className="input" defaultValue={currentUser.fullName} />
                </Field>
                <Field label="Nom d'utilisateur" hint="Utilisé dans l'URL de ton portfolio public.">
                  <div className="flex items-center gap-2">
                    <span className="shrink-0 font-mono text-[12px] text-ink-faint">root404.tn/u/</span>
                    <input className="input" defaultValue={currentUser.username} />
                  </div>
                </Field>
                <Field label="Bio" hint="280 caractères maximum.">
                  <textarea rows={3} className="input h-auto resize-none py-2.5" defaultValue={currentUser.bio} />
                </Field>
                <Field label="Campus">
                  <select className="select" defaultValue={currentUser.campus}>
                    <option>Tunis</option><option>Sfax</option><option>Sousse</option>
                  </select>
                </Field>
              </div>
              <div className="mt-6 flex justify-end gap-2 border-t border-line pt-5">
                <Button variant="ghost" size="md">Annuler</Button>
                <Button size="md" icon="Check">Enregistrer</Button>
              </div>
            </>
          )}

          {section === 'account' && (
            <>
              <h2 className="text-[15px] font-bold text-ink">Compte & sécurité</h2>
              <div className="mt-2">
                <Field label="Adresse e-mail" hint="Utilisée pour l'authentification par OTP.">
                  <div className="flex items-center gap-2">
                    <input className="input" defaultValue="abdeljalil@root404.tn" />
                    <Badge tone="ok">Vérifiée</Badge>
                  </div>
                </Field>
                <Field label="Authentification" hint="ROOT 404 utilise un code temporaire par e-mail — aucun mot de passe à retenir.">
                  <div className="rounded-lg border border-line bg-root-850 p-4">
                    <p className="flex items-center gap-2 text-[12.5px] text-ink-soft">
                      <Icon name="MailCheck" size={15} className="text-ok" /> OTP par e-mail activé
                    </p>
                  </div>
                </Field>
                <Field label="Sessions actives">
                  <ul className="space-y-2">
                    {[
                      { d: 'Chrome — Ubuntu 22.04', l: 'Tunis, TN', c: true },
                      { d: 'Safari — iPhone 15', l: 'Ariana, TN', c: false },
                    ].map((s) => (
                      <li key={s.d} className="flex items-center gap-3 rounded-lg border border-line bg-root-850 p-3">
                        <Icon name={s.c ? 'Monitor' : 'Smartphone'} size={16} className="text-ink-dim" />
                        <div className="min-w-0 flex-1">
                          <p className="truncate text-[12.5px] text-ink">{s.d}</p>
                          <p className="text-[11px] text-ink-faint">{s.l}</p>
                        </div>
                        {s.c ? <Badge tone="ok">Actuelle</Badge> : <Button size="sm" variant="ghost" className="text-danger">Révoquer</Button>}
                      </li>
                    ))}
                  </ul>
                </Field>
                <Field label="Zone dangereuse" hint="Cette action est irréversible et supprime tous tes projets.">
                  <Button variant="danger" size="md" icon="Trash2">Supprimer mon compte</Button>
                </Field>
              </div>
            </>
          )}

          {section === 'notifications' && (
            <>
              <h2 className="text-[15px] font-bold text-ink">Notifications</h2>
              <ul className="mt-4">
                {[
                  { k: 'peerReview', l: 'Slots de peer review', d: 'Quand un pair réserve ou annule un créneau.' },
                  { k: 'moulinette', l: 'Résultats Moulinette', d: 'Dès qu’une soumission a fini d’être évaluée.' },
                  { k: 'coalition', l: 'Coalition & Wars', d: 'Événements et classements de ta coalition.' },
                  { k: 'weekly', l: 'Rapport hebdomadaire', d: 'Un résumé de ta progression chaque lundi.' },
                  { k: 'marketing', l: 'Actualités ROOT 404', d: 'Nouveautés produit et événements partenaires.' },
                ].map((n) => (
                  <li key={n.k} className="flex items-center justify-between gap-4 border-b border-line py-4 last:border-0">
                    <div>
                      <p className="text-[13px] font-semibold text-ink">{n.l}</p>
                      <p className="mt-0.5 text-[11.5px] text-ink-dim">{n.d}</p>
                    </div>
                    <Toggle on={prefs[n.k]} onChange={set(n.k)} label={n.l} />
                  </li>
                ))}
              </ul>
            </>
          )}

          {section === 'appearance' && (
            <>
              <h2 className="text-[15px] font-bold text-ink">Apparence</h2>
              <div className="mt-2">
                <Field label="Thème" hint="Le thème sombre est recommandé pour les longues sessions.">
                  <div className="grid grid-cols-2 gap-3 sm:max-w-md">
                    {[
                      { k: 'dark', l: 'Sombre', bg: '#04090E', fg: '#F8851F' },
                      { k: 'light', l: 'Clair', bg: '#F6F7F9', fg: '#F8851F' },
                    ].map((t) => (
                      <button key={t.k} className="rounded-lg border border-line p-3 transition-colors hover:border-brand-500/40">
                        <span className="block h-16 rounded-md border border-line" style={{ background: t.bg }}>
                          <span className="ml-2 mt-2 block h-2 w-10 rounded-full" style={{ background: t.fg }} />
                        </span>
                        <span className="mt-2 block text-[12px] font-medium text-ink">{t.l}</span>
                      </button>
                    ))}
                  </div>
                </Field>
                <Field label="Langue de l'interface">
                  <select className="select sm:max-w-xs"><option>Français</option><option>العربية</option><option>English</option></select>
                </Field>
                <Field label="Police de l'éditeur">
                  <select className="select sm:max-w-xs"><option>JetBrains Mono</option><option>Fira Code</option><option>Source Code Pro</option></select>
                </Field>
              </div>
            </>
          )}

          {section === 'privacy' && (
            <>
              <h2 className="text-[15px] font-bold text-ink">Confidentialité</h2>
              <ul className="mt-4">
                {[
                  { k: 'publicProfile', l: 'Portfolio public', d: 'Rendre root404.tn/u/abdeljalil accessible à tous.' },
                  { k: 'showEmail', l: 'Afficher mon e-mail', d: 'Visible par les entreprises partenaires uniquement.' },
                  { k: 'leaderboard', l: 'Apparaître au classement', d: 'Te retirer te rend invisible dans les leaderboards publics.' },
                ].map((n) => (
                  <li key={n.k} className="flex items-center justify-between gap-4 border-b border-line py-4 last:border-0">
                    <div>
                      <p className="text-[13px] font-semibold text-ink">{n.l}</p>
                      <p className="mt-0.5 text-[11.5px] text-ink-dim">{n.d}</p>
                    </div>
                    <Toggle on={prefs[n.k]} onChange={set(n.k)} label={n.l} />
                  </li>
                ))}
              </ul>
            </>
          )}

          {section === 'api' && (
            <>
              <h2 className="text-[15px] font-bold text-ink">API & Webhooks</h2>
              <p className="mt-1.5 text-[12.5px] text-ink-dim">
                Connecte tes réussites à un portfolio externe, un bot Discord ou Telegram.
              </p>
              <div className="mt-5 rounded-lg border border-line bg-root-850 p-4">
                <p className="text-[11px] font-semibold uppercase tracking-wider text-ink-dim">Clé API</p>
                <div className="mt-2 flex items-center gap-2">
                  <code className="flex-1 overflow-x-auto rounded-md border border-line bg-[#080D12] px-3 py-2.5 font-mono text-[11.5px] text-ok">
                    r404_sk_live_••••••••••••••••••••7f2a
                  </code>
                  <Button size="sm" variant="outline" icon="Copy">Copier</Button>
                  <Button size="sm" variant="ghost" icon="RefreshCw" aria-label="Régénérer" />
                </div>
              </div>
              <div className="mt-4 rounded-lg border border-line bg-root-850 p-4">
                <p className="text-[11px] font-semibold uppercase tracking-wider text-ink-dim">Endpoint webhook</p>
                <input className="input mt-2" placeholder="https://exemple.tn/webhooks/root404" />
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {['project.passed', 'level.up', 'review.completed', 'coalition.war'].map((e) => (
                    <span key={e} className="chip font-mono">{e}</span>
                  ))}
                </div>
              </div>
              <Button variant="outline" size="sm" className="mt-4" icon="ExternalLink">
                Documentation Swagger / OpenAPI
              </Button>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
