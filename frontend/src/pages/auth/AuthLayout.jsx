import { Link } from 'react-router-dom'
import Logo, { LogoMark } from '../../components/Logo'
import Icon from '../../components/ui/Icon'

const POINTS = [
  { icon: 'Terminal', t: 'Sandbox Ubuntu isolé', d: 'Chaque soumission tourne dans son propre conteneur Docker.' },
  { icon: 'Users', t: 'Correction par les pairs', d: 'Un vrai humain relit ton code, en visio, avec une checklist.' },
  { icon: 'Brain', t: 'AI Mentor socratique', d: "Des questions qui font réfléchir, jamais la solution servie." },
  { icon: 'BadgeCheck', t: 'Portfolio vérifié', d: 'Un profil public que les entreprises peuvent auditer.' },
]

/**
 * Split-screen shell shared by Login & Register: form on the left,
 * branded panel with the medina backdrop on the right.
 */
export default function AuthLayout({ title, subtitle, children, footer }) {
  return (
    <div className="grid min-h-screen bg-root-950 lg:grid-cols-2">
      {/* Form side */}
      <div className="flex flex-col px-5 py-8 sm:px-10">
        <div className="flex items-center justify-between">
          <Logo size={32} />
          <Link
            to="/"
            className="flex items-center gap-1.5 text-[12.5px] text-ink-dim transition-colors hover:text-ink"
          >
            <Icon name="ArrowLeft" size={14} /> Retour au site
          </Link>
        </div>

        <div className="mx-auto flex w-full max-w-[400px] flex-1 flex-col justify-center py-10">
          <h1 className="text-[26px] font-extrabold tracking-tight text-white">{title}</h1>
          <p className="mt-2 text-[13.5px] leading-relaxed text-ink-dim">{subtitle}</p>
          <div className="mt-8">{children}</div>
        </div>

        <p className="text-center text-[12.5px] text-ink-dim">{footer}</p>
      </div>

      {/* Brand side */}
      <div className="relative hidden overflow-hidden border-l border-line lg:block">
        <img src="/hero-medina.jpg" alt="" aria-hidden className="absolute inset-0 h-full w-full object-cover opacity-40" />
        <div className="absolute inset-0 bg-gradient-to-t from-root-950 via-root-950/80 to-root-950/40" />

        <div className="relative flex h-full flex-col justify-center px-12 xl:px-16">
          <div className="relative w-fit">
            <div aria-hidden className="absolute inset-0 -z-10 scale-150 rounded-full bg-brand-500/20 blur-[60px]" />
            <LogoMark size={80} className="drop-shadow-[0_0_22px_rgba(248,133,31,.7)]" />
          </div>

          <h2 className="mt-8 max-w-md text-[30px] font-extrabold leading-tight tracking-tight text-white">
            Apprends. Code. Collabore.
            <br />
            <span className="text-brand-500">Deviens Meilleur.</span>
          </h2>
          <p dir="rtl" lang="ar" className="font-ar mt-4 max-w-sm text-[13px] leading-[2] text-ink-soft">
            منصة تعليمية وتنافسية متكاملة مستوحاة من فلسفة 42
          </p>

          <ul className="mt-10 max-w-md space-y-4">
            {POINTS.map((p) => (
              <li key={p.t} className="flex gap-3.5">
                <span className="grid h-9 w-9 shrink-0 place-items-center rounded-lg border border-brand-500/25 bg-brand-500/10 text-brand-500">
                  <Icon name={p.icon} size={17} />
                </span>
                <div>
                  <p className="text-[13px] font-semibold text-ink">{p.t}</p>
                  <p className="mt-0.5 text-[12px] leading-relaxed text-ink-dim">{p.d}</p>
                </div>
              </li>
            ))}
          </ul>

          <div className="mt-10 flex items-center gap-6 border-t border-line pt-6">
            {[
              { v: '12,487+', l: 'Codeurs' },
              { v: '892+', l: 'Projets' },
              { v: '42', l: 'Coalitions' },
            ].map((s) => (
              <div key={s.l}>
                <p className="font-mono text-[19px] font-extrabold text-brand-500">{s.v}</p>
                <p className="text-[11px] text-ink-dim">{s.l}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
