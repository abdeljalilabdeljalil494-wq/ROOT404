import { authService } from '../../services/api'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import Icon from '../ui/Icon'
import Avatar from '../ui/Avatar'
import ThemeToggle from '../ui/ThemeToggle'
import { useCurrentUser } from '../RequireAuth'

import NotificationMenu from './NotificationMenu'
import GlobalSearch from './GlobalSearch'

export default function AppTopbar({ title, breadcrumb = [], onMenu, actions }) {
  const currentUser = useCurrentUser()
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <header className="sticky top-0 z-30 flex h-[60px] shrink-0 items-center gap-3 border-b border-line bg-root-950/95 px-4 backdrop-blur-xl sm:px-6">
      <button
        onClick={onMenu}
        aria-label="Ouvrir le menu"
        className="grid h-9 w-9 shrink-0 place-items-center rounded-lg text-ink-soft hover:bg-white/[0.06] lg:hidden"
      >
        <Icon name="Menu" size={19} />
      </button>

      <div className="min-w-0 flex-1">
        {breadcrumb.length > 0 ? (
          <nav className="flex items-center gap-1.5 text-[13px]" aria-label="Fil d'Ariane">
            {breadcrumb.map((b, i) => (
              <span key={b.label} className="flex items-center gap-1.5">
                {i > 0 && <Icon name="ChevronRight" size={13} className="text-ink-faint" />}
                {b.to ? (
                  <Link to={b.to} className="text-ink-dim transition-colors hover:text-ink">{b.label}</Link>
                ) : (
                  <span className="font-semibold text-ink">{b.label}</span>
                )}
              </span>
            ))}
          </nav>
        ) : (
          <p className="truncate text-[15px] font-semibold text-ink">{title}</p>
        )}
      </div>

      <GlobalSearch />

      {actions}

      <div className="flex items-center gap-0.5">
        <ThemeToggle />

        <NotificationMenu />

        <div className="relative ml-1">
          <button
            onClick={() => { setMenuOpen((o) => !o) }}
            aria-label="Menu du compte"
            className="rounded-full transition-transform hover:scale-105"
          >
            <Avatar src={currentUser.avatar} name={currentUser.displayName} size="sm" status="online" />
          </button>

          {menuOpen && (
            <>
              <div className="fixed inset-0 z-40" onClick={() => setMenuOpen(false)} />
              <div className="absolute right-0 z-50 mt-2 w-56 overflow-hidden rounded-xl border border-line bg-root-800 py-1.5 shadow-pop">
                <div className="border-b border-line px-4 pb-3 pt-2">
                  <p className="text-[13px] font-semibold text-ink">{currentUser.fullName}</p>
                  <p className="text-[11px] text-ink-dim">Niveau {currentUser.level.toFixed(2)} · {currentUser.campus}</p>
                </div>
                {[
                  { label: 'Mon profil', to: '/profile', icon: 'User' },
                  { label: 'Portfolio public', to: '/portfolio', icon: 'Globe' },
                  { label: 'Paramètres', to: '/settings', icon: 'Settings' },
                ].map((i) => (
                  <Link
                    key={i.to}
                    to={i.to}
                    onClick={() => setMenuOpen(false)}
                    className="flex items-center gap-2.5 px-4 py-2 text-[13px] text-ink-soft transition-colors hover:bg-white/[0.05] hover:text-ink"
                  >
                    <Icon name={i.icon} size={15} /> {i.label}
                  </Link>
                ))}
                <div className="mt-1 border-t border-line pt-1">
                  <Link
                    to="/login"
                    onClick={(event) => { event.preventDefault(); authService.logout().catch(() => {}) }}
                    className="flex items-center gap-2.5 px-4 py-2 text-[13px] text-danger transition-colors hover:bg-danger/10"
                  >
                    <Icon name="LogOut" size={15} /> Déconnexion
                  </Link>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
