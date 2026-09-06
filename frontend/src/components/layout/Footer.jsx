import { Link } from 'react-router-dom'
import Logo from '../Logo'
import Icon from '../ui/Icon'

const COLUMNS = [
  {
    title: 'Plateforme',
    links: [
      { label: 'Parcours', to: '/parcours' },
      { label: 'Piscine', to: '/piscine' },
      { label: 'ROOT Arena', to: '/arena' },
      { label: 'Classement', to: '/classement' },
      { label: 'Coalitions', to: '/coalitions' },
    ],
  },
  {
    title: 'Apprendre',
    links: [
      { label: 'Code Journey', to: '/journey' },
      { label: 'Skill Graph', to: '/skills' },
      { label: 'Assistant IA', to: '/mentor' },
      { label: 'Analytics 360°', to: '/analytics' },
      { label: 'Knowledge Base', to: '/blog' },
    ],
  },
  {
    title: 'Communauté',
    links: [
      { label: 'Rooms', to: '/rooms' },
      { label: 'Peer Review', to: '/rooms' },
      { label: 'Mentorat', to: '/communaute' },
      { label: 'Blog', to: '/blog' },
      { label: 'Discord', to: '/communaute' },
    ],
  },
  {
    title: 'Entreprise',
    links: [
      { label: 'À propos', to: '/about' },
      { label: 'Recrutement', to: '/about' },
      { label: 'Partenaires', to: '/about' },
      { label: 'API publique', to: '/about' },
      { label: 'Contact', to: '/about' },
    ],
  },
]

const SOCIALS = [
  { icon: 'Github', href: '#', label: 'GitHub' },
  { icon: 'Linkedin', href: '#', label: 'LinkedIn' },
  { icon: 'Twitter', href: '#', label: 'X' },
  { icon: 'Youtube', href: '#', label: 'YouTube' },
]

export default function Footer() {
  return (
    <footer className="relative border-t border-line bg-root-950">
      <div className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-brand-500/40 to-transparent" />

      <div className="container-page py-14">
        <div className="grid gap-10 lg:grid-cols-[1.4fr_repeat(4,1fr)]">
          <div className="max-w-xs">
            <Logo size={34} />
            <p className="mt-4 text-[13px] leading-relaxed text-ink-dim">
              Plateforme éducative et compétitive inspirée de la philosophie de l'école 42, conçue
              pour les étudiants et développeurs tunisiens.
            </p>
            <div className="mt-5 flex items-center gap-2">
              {SOCIALS.map((s) => (
                <a
                  key={s.label}
                  href={s.href}
                  aria-label={s.label}
                  className="grid h-9 w-9 place-items-center rounded-lg border border-line text-ink-dim transition-all hover:border-brand-500/50 hover:text-brand-500"
                >
                  <Icon name={s.icon} size={16} />
                </a>
              ))}
            </div>
          </div>

          {COLUMNS.map((col) => (
            <div key={col.title}>
              <h4 className="text-[12px] font-bold uppercase tracking-wider text-ink">{col.title}</h4>
              <ul className="mt-4 space-y-2.5">
                {col.links.map((l) => (
                  <li key={l.label}>
                    <Link
                      to={l.to}
                      className="text-[13px] text-ink-dim transition-colors hover:text-brand-500"
                    >
                      {l.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-12 flex flex-col items-center justify-between gap-4 border-t border-line pt-7 sm:flex-row">
          <p className="text-[12px] text-ink-faint">
            © {new Date().getFullYear()} ROOT 404 — Elite Coder Platform. Tous droits réservés.
          </p>
          <p className="flex items-center gap-2 text-[12px] text-ink-faint">
            Fait avec <span className="text-danger">❤</span> pour la communauté des développeurs en
            <span className="inline-flex items-center gap-1.5 font-semibold text-ink-soft">
              <span className="grid h-3.5 w-5 place-items-center overflow-hidden rounded-[2px] bg-[#E70013]">
                <span className="h-2 w-2 rounded-full bg-white" />
              </span>
              Tunisie
            </span>
          </p>
        </div>
      </div>
    </footer>
  )
}
