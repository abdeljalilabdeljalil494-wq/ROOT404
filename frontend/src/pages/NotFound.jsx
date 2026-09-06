import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import Logo, { LogoMark } from '../components/Logo'
import Button from '../components/ui/Button'
import Icon from '../components/ui/Icon'

const LINKS = [
  { to: '/dashboard', label: 'Tableau de bord', icon: 'LayoutDashboard' },
  { to: '/projects', label: 'Mes projets', icon: 'FolderKanban' },
  { to: '/classement', label: 'Classement', icon: 'Trophy' },
  { to: '/rooms', label: 'Rooms', icon: 'MessagesSquare' },
]

export default function NotFound() {
  useEffect(() => { document.title = '404 — ROOT 404' }, [])

  return (
    <div className="relative grid min-h-screen place-items-center overflow-hidden bg-root-950 px-5">
      <div aria-hidden className="absolute inset-0 bg-grid opacity-40" />
      <div
        aria-hidden
        className="absolute left-1/2 top-1/2 h-96 w-96 -translate-x-1/2 -translate-y-1/2 rounded-full bg-brand-500/[0.13] blur-[110px]"
      />

      <div className="relative w-full max-w-lg text-center">
        <div className="mx-auto w-fit">
          <div className="relative">
            <div aria-hidden className="absolute inset-0 -z-10 scale-150 rounded-full bg-brand-500/20 blur-[50px]" />
            <LogoMark size={90} className="drop-shadow-[0_0_22px_rgba(248,133,31,.7)]" />
          </div>
        </div>

        <p className="mt-8 font-mono text-[13px] text-ink-dim">
          <span className="text-brand-500">$</span> cd /page/introuvable
        </p>
        <h1 className="mt-2 font-mono text-[64px] font-extrabold leading-none tracking-tight text-white sm:text-[86px]">
          4<span className="text-brand-500">0</span>4
        </h1>
        <p className="mt-3 font-mono text-[13px] text-danger">
          bash: cette page: Aucun fichier ou dossier de ce type
        </p>

        <p className="mx-auto mt-6 max-w-sm text-[13.5px] leading-relaxed text-ink-soft">
          Ironique, sur une plateforme qui s'appelle ROOT 404. La page que tu cherches a été
          déplacée, supprimée — ou n'a jamais compilé.
        </p>

        <div className="mt-8 flex flex-wrap justify-center gap-3">
          <Button to="/" size="lg" icon="Home">Retour à l'accueil</Button>
          <Button to="/dashboard" variant="outline" size="lg" iconRight="ArrowRight">Mon tableau de bord</Button>
        </div>

        <div className="mt-10 border-t border-line pt-7">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-ink-faint">
            Ou continue par là
          </p>
          <div className="mt-4 flex flex-wrap justify-center gap-2">
            {LINKS.map((l) => (
              <Link
                key={l.to}
                to={l.to}
                className="flex items-center gap-2 rounded-lg border border-line bg-root-850 px-3.5 py-2 text-[12.5px] text-ink-soft transition-colors hover:border-brand-500/40 hover:text-brand-500"
              >
                <Icon name={l.icon} size={14} /> {l.label}
              </Link>
            ))}
          </div>
        </div>

        <div className="mt-10 flex justify-center">
          <Logo size={26} compact to={null} />
        </div>
      </div>
    </div>
  )
}
