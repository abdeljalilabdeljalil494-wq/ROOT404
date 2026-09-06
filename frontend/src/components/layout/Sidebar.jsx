import { NavLink } from 'react-router-dom'
import Logo from '../Logo'
import Icon from '../ui/Icon'
import Avatar from '../ui/Avatar'
import ProgressBar from '../ui/ProgressBar'
import { currentUser } from '../../data/mock'

export const SIDEBAR_GROUPS = [
  {
    title: null,
    items: [
      { label: 'Tableau de bord', to: '/dashboard', icon: 'LayoutDashboard' },
      { label: 'Mes projets', to: '/projects', icon: 'FolderKanban' },
      { label: 'Piscine', to: '/piscine', icon: 'Waves' },
      { label: 'Workspace', to: '/workspace', icon: 'Code2' },
    ],
  },
  {
    title: 'Communauté',
    items: [
      { label: 'Rooms', to: '/rooms', icon: 'MessagesSquare', badge: '6' },
      { label: 'Peer Review', to: '/peer-review', icon: 'ClipboardCheck', badge: '2' },
      { label: 'Coalitions', to: '/coalitions', icon: 'Flag' },
      { label: 'Classement', to: '/classement', icon: 'Trophy' },
    ],
  },
  {
    title: 'Progression',
    items: [
      { label: 'Code Journey', to: '/journey', icon: 'Map' },
      { label: 'Skill Graph', to: '/skills', icon: 'Network' },
      { label: 'Analytics 360°', to: '/analytics', icon: 'BarChart3' },
      { label: 'ROOT Arena', to: '/arena', icon: 'Swords' },
    ],
  },
  {
    title: 'Compte',
    items: [
      { label: 'Assistant IA', to: '/mentor', icon: 'Sparkles' },
      { label: 'Profil', to: '/profile', icon: 'User' },
      { label: 'Paramètres', to: '/settings', icon: 'Settings' },
    ],
  },
]

function Item({ item, onNavigate }) {
  return (
    <NavLink
      to={item.to}
      onClick={onNavigate}
      className={({ isActive }) =>
        `group relative flex items-center gap-3 rounded-lg px-3 py-2 text-[13px] font-medium transition-all ${
          isActive
            ? 'bg-brand-500/[0.13] text-brand-500'
            : 'text-ink-soft hover:bg-white/[0.045] hover:text-ink'
        }`
      }
    >
      {({ isActive }) => (
        <>
          {isActive && (
            <span className="absolute inset-y-1.5 left-0 w-[3px] rounded-r-full bg-brand-500" />
          )}
          <Icon name={item.icon} size={17} className="shrink-0" />
          <span className="flex-1 truncate">{item.label}</span>
          {item.badge && (
            <span
              className={`rounded px-1.5 py-0.5 text-[10px] font-bold ${
                isActive ? 'bg-brand-500 text-[#160A00]' : 'bg-white/[0.07] text-ink-dim'
              }`}
            >
              {item.badge}
            </span>
          )}
        </>
      )}
    </NavLink>
  )
}

export default function Sidebar({ open = false, onClose }) {
  return (
    <>
      {/* Mobile scrim */}
      <div
        onClick={onClose}
        className={`fixed inset-0 z-40 bg-black/70 backdrop-blur-sm transition-opacity lg:hidden ${
          open ? 'opacity-100' : 'pointer-events-none opacity-0'
        }`}
      />

      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-[258px] flex-col border-r border-line bg-root-950
                    transition-transform duration-300 lg:translate-x-0 ${
                      open ? 'translate-x-0' : '-translate-x-full'
                    }`}
      >
        <div className="flex h-[60px] shrink-0 items-center justify-between border-b border-line px-4">
          <Logo size={30} compact />
          <button
            onClick={onClose}
            aria-label="Fermer le menu"
            className="grid h-8 w-8 place-items-center rounded-md text-ink-dim hover:bg-white/[0.06] lg:hidden"
          >
            <Icon name="X" size={17} />
          </button>
        </div>

        {/* Level card */}
        <div className="shrink-0 border-b border-line p-3">
          <div className="rounded-lg border border-line bg-root-800 p-3">
            <div className="flex items-center gap-2.5">
              <Avatar src={currentUser.avatar} name={currentUser.displayName} size="sm" status="online" />
              <div className="min-w-0 flex-1">
                <p className="truncate text-[12.5px] font-semibold text-ink">{currentUser.displayName}</p>
                <p className="truncate text-[10.5px] text-ink-dim">@{currentUser.username}</p>
              </div>
            </div>
            <div className="mt-3 flex items-baseline justify-between">
              <span className="text-[10px] font-semibold uppercase tracking-wider text-ink-dim">Niveau</span>
              <span className="font-mono text-[13px] font-bold text-brand-500">{currentUser.level.toFixed(2)}</span>
            </div>
            <ProgressBar value={currentUser.levelProgress} height={5} className="mt-1.5" />
          </div>
        </div>

        <nav className="flex-1 space-y-5 overflow-y-auto px-3 py-4">
          {SIDEBAR_GROUPS.map((g, gi) => (
            <div key={g.title || gi}>
              {g.title && (
                <p className="mb-2 px-3 text-[10px] font-bold uppercase tracking-[0.14em] text-ink-faint">
                  {g.title}
                </p>
              )}
              <div className="space-y-0.5">
                {g.items.map((it) => (
                  <Item key={it.to} item={it} onNavigate={onClose} />
                ))}
              </div>
            </div>
          ))}
        </nav>

        {/* Black Hole countdown */}
        <div className="shrink-0 border-t border-line p-3">
          <div className="rounded-lg border border-brand-500/25 bg-gradient-to-br from-brand-500/[0.12] to-transparent p-3">
            <div className="flex items-center gap-2 text-brand-400">
              <Icon name="CircleDot" size={14} />
              <span className="text-[11px] font-bold uppercase tracking-wide">Black Hole</span>
            </div>
            <p className="mt-1.5 text-[11px] text-ink-soft">
              <span className="font-mono text-base font-bold text-ink">{currentUser.blackHole.daysLeft}</span> jours
              restants
            </p>
            <ProgressBar
              value={(currentUser.blackHole.daysLeft / currentUser.blackHole.total) * 100}
              height={4}
              className="mt-2"
            />
          </div>

          <NavLink
            to="/"
            className="mt-2 flex items-center gap-3 rounded-lg px-3 py-2 text-[13px] font-medium text-ink-dim transition-colors hover:bg-danger/10 hover:text-danger"
          >
            <Icon name="LogOut" size={17} />
            Déconnexion
          </NavLink>
        </div>
      </aside>
    </>
  )
}
