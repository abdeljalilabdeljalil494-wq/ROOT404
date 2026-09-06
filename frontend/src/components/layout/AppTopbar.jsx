import { useState } from 'react'
import { Link } from 'react-router-dom'
import Icon from '../ui/Icon'
import Avatar from '../ui/Avatar'
import ThemeToggle from '../ui/ThemeToggle'
import { currentUser } from '../../data/mock'

const NOTIFS = [
  { icon: 'ClipboardCheck', tone: 'text-brand-500', text: 'nour_dev a réservé un slot de correction pour minishell.', time: '2 min' },
  { icon: 'Trophy', tone: 'text-warn', text: 'Ta coalition The Phoenix est passée 2ᵉ au classement hebdo.', time: '1 h' },
  { icon: 'CheckCircle2', tone: 'text-ok', text: 'Moulinette réussie sur get_next_line — 100/100.', time: '2 h' },
  { icon: 'AlertTriangle', tone: 'text-danger', text: 'philosophers : Moulinette échouée, nouvelle tentative dans 2 j.', time: '4 j' },
]

export default function AppTopbar({ title, breadcrumb = [], onMenu, actions }) {
  const [notifOpen, setNotifOpen] = useState(false)
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
          <h1 className="truncate text-[15px] font-semibold text-ink">{title}</h1>
        )}
      </div>

      {/* Search */}
      <label className="relative hidden h-9 w-56 items-center md:flex xl:w-80">
        <Icon name="Search" size={15} className="pointer-events-none absolute left-3 text-ink-faint" />
        <input
          placeholder="Rechercher…"
          className="h-full w-full rounded-lg border border-line bg-root-850 pl-9 pr-3 text-[13px] text-ink placeholder:text-ink-faint focus:border-brand-500/50 focus:outline-none"
        />
      </label>

      {actions}

      <div className="flex items-center gap-0.5">
        <ThemeToggle />

        <div className="relative">
          <button
            onClick={() => { setNotifOpen((o) => !o); setMenuOpen(false) }}
            aria-label="Notifications"
            className="relative grid h-9 w-9 place-items-center rounded-lg text-ink-soft transition-colors hover:bg-white/[0.06] hover:text-ink"
          >
            <Icon name="Bell" size={17} />
            <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-brand-500 ring-2 ring-root-950" />
          </button>

          {notifOpen && (
            <>
              <div className="fixed inset-0 z-40" onClick={() => setNotifOpen(false)} />
              <div className="absolute right-0 z-50 mt-2 w-[330px] overflow-hidden rounded-xl border border-line bg-root-800 shadow-pop">
                <div className="flex items-center justify-between border-b border-line px-4 py-3">
                  <span className="text-[13px] font-semibold text-ink">Notifications</span>
                  <button className="text-[11px] font-medium text-brand-500 hover:underline">Tout marquer lu</button>
                </div>
                <ul className="max-h-80 overflow-y-auto">
                  {NOTIFS.map((n, i) => (
                    <li key={i} className="flex gap-3 border-b border-line/60 px-4 py-3 transition-colors last:border-0 hover:bg-white/[0.03]">
                      <span className={`mt-0.5 shrink-0 ${n.tone}`}><Icon name={n.icon} size={16} /></span>
                      <div className="min-w-0">
                        <p className="text-[12.5px] leading-snug text-ink-soft">{n.text}</p>
                        <p className="mt-1 text-[11px] text-ink-faint">il y a {n.time}</p>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            </>
          )}
        </div>

        <div className="relative ml-1">
          <button
            onClick={() => { setMenuOpen((o) => !o); setNotifOpen(false) }}
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
                    to="/"
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
