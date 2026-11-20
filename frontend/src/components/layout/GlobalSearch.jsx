import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { http } from '../../services/api'

export default function GlobalSearch() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState(null)
  const [state, setState] = useState('idle')
  const [open, setOpen] = useState(false)
  const container = useRef(null)
  useEffect(() => {
    if (!query.trim()) { setResults(null); setState('idle'); return }
    const controller = new AbortController()
    setState('loading'); setResults(null)
    const timer = setTimeout(() => {
      http.get('/search', { params: { q: query.trim() }, signal: controller.signal }).then(response => {
        if (!controller.signal.aborted) {
          if (response.data.error) { setState('error'); return }
          setResults(response.data); setState('loaded')
        }
      }).catch(() => { if (!controller.signal.aborted) setState('error') })
    }, 300)
    return () => { clearTimeout(timer); controller.abort() }
  }, [query])
  useEffect(() => {
    const outside = event => { if (!container.current?.contains(event.target)) setOpen(false) }
    document.addEventListener('pointerdown', outside)
    return () => document.removeEventListener('pointerdown', outside)
  }, [])
  return <div ref={container} className="relative hidden w-56 md:block xl:w-80" onKeyDown={event => { if (event.key === 'Escape') setOpen(false) }}>
    <label className="sr-only" htmlFor="global-search">Rechercher des projets et profils</label>
    <input id="global-search" className="input w-full" type="search" autoComplete="off" maxLength={100} placeholder="Projets et profils…" value={query} onFocus={() => setOpen(true)} onChange={event => { setQuery(event.target.value); setOpen(true) }} aria-controls={open && query.trim() ? 'global-search-results' : undefined} />
    {open && query.trim() && <section id="global-search-results" aria-label="Résultats de recherche" className="absolute right-0 z-50 mt-2 w-full rounded-xl border border-line bg-root-800 p-4 shadow-pop">
      {state === 'loading' && <p role="status">Recherche…</p>}
      {state === 'error' && <p role="alert">Recherche indisponible. Réessayez.</p>}
      {results && <><h2 className="font-semibold">Projets</h2><ul>{results.projects.map(project => <li key={project.slug}><Link className="block py-2" onClick={() => setOpen(false)} to={`/projects/${project.slug}`}>{project.name}</Link></li>)}</ul>{!results.projects.length && <p>Aucun projet.</p>}<h2 className="mt-3 font-semibold">Profils publics</h2><ul>{results.users.map(user => <li key={user.username}><Link className="block py-2" onClick={() => setOpen(false)} to={`/u/${encodeURIComponent(user.username)}`}>{user.displayName || user.username}</Link></li>)}</ul>{!results.users.length && <p>Aucun profil public.</p>}</>}
    </section>}
  </div>
}
