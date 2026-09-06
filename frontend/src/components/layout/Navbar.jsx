import { useEffect, useState } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import Logo from '../Logo'
import Button from '../ui/Button'
import Icon from '../ui/Icon'
import ThemeToggle from '../ui/ThemeToggle'
import { navLinks } from '../../data/mock'

export default function Navbar() {
  const [open, setOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)
  const [search, setSearch] = useState(false)
  const { pathname } = useLocation()

  useEffect(() => {
    setOpen(false)
  }, [pathname])

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  useEffect(() => {
    document.body.style.overflow = open ? 'hidden' : ''
    return () => { document.body.style.overflow = '' }
  }, [open])

  return (
    <header
      className={`sticky top-0 z-50 w-full border-b transition-colors duration-300 ${
        scrolled
          ? 'border-line bg-root-950/90 backdrop-blur-xl'
          : 'border-transparent bg-root-950'
      }`}
    >
      <div className="container-page flex h-[64px] items-center justify-between gap-4">
        <Logo size={32} />

        {/* Desktop nav */}
        <nav className="hidden items-center gap-1 lg:flex" aria-label="Navigation principale">
          {navLinks.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              end={l.to === '/'}
              className={({ isActive }) =>
                `relative px-3 py-5 text-[13px] font-medium transition-colors ${
                  isActive ? 'text-brand-500' : 'text-ink-soft hover:text-ink'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  {l.label}
                  {isActive && (
                    <span className="absolute inset-x-3 bottom-0 h-[2px] rounded-full bg-brand-500" />
                  )}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Right cluster */}
        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setSearch((s) => !s)}
            aria-label="Rechercher"
            className="grid h-9 w-9 place-items-center rounded-lg text-ink-soft transition-colors hover:bg-white/[0.06] hover:text-ink"
          >
            <Icon name="Search" size={17} />
          </button>
          <ThemeToggle />
          <Button to="/login" variant="outline" size="sm" className="ml-1 hidden h-9 px-4 sm:inline-flex">
            Se connecter
          </Button>
          <Button to="/register" size="sm" className="hidden h-9 px-4 sm:inline-flex">
            S'inscrire
          </Button>
          <button
            onClick={() => setOpen((o) => !o)}
            aria-label="Menu"
            aria-expanded={open}
            className="grid h-9 w-9 place-items-center rounded-lg text-ink transition-colors hover:bg-white/[0.06] lg:hidden"
          >
            <Icon name={open ? 'X' : 'Menu'} size={20} />
          </button>
        </div>
      </div>

      {/* Slide-down search */}
      {search && (
        <div className="border-t border-line bg-root-950/95 backdrop-blur-xl">
          <div className="container-page flex h-14 items-center gap-3">
            <Icon name="Search" size={16} className="text-ink-dim" />
            <input
              autoFocus
              placeholder="Rechercher un projet, un codeur, une room…"
              className="h-full flex-1 bg-transparent text-sm text-ink placeholder:text-ink-faint focus:outline-none"
            />
            <kbd className="hidden rounded border border-line px-1.5 py-0.5 font-mono text-[10px] text-ink-dim sm:block">
              ESC
            </kbd>
            <button onClick={() => setSearch(false)} className="text-ink-dim hover:text-ink">
              <Icon name="X" size={16} />
            </button>
          </div>
        </div>
      )}

      {/* Mobile drawer */}
      <div
        className={`overflow-hidden border-t border-line bg-root-950 transition-[max-height] duration-300 lg:hidden ${
          open ? 'max-h-[80vh]' : 'max-h-0 border-transparent'
        }`}
      >
        <nav className="container-page flex flex-col py-3">
          {navLinks.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              end={l.to === '/'}
              className={({ isActive }) =>
                `flex items-center justify-between rounded-lg px-3 py-3 text-[14px] font-medium transition-colors ${
                  isActive ? 'bg-brand-500/10 text-brand-500' : 'text-ink-soft hover:bg-white/[0.04]'
                }`
              }
            >
              {l.label}
              <Icon name="ChevronRight" size={15} />
            </NavLink>
          ))}
          <div className="mt-3 grid grid-cols-2 gap-2 border-t border-line pt-4">
            <Button to="/login" variant="outline" size="md">Se connecter</Button>
            <Button to="/register" size="md">S'inscrire</Button>
          </div>
        </nav>
      </div>
    </header>
  )
}
