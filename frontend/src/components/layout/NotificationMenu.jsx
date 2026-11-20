import { useCallback, useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { notificationService } from '../../services/api'
import Icon from '../ui/Icon'

export default function NotificationMenu() {
  const [open, setOpen] = useState(false)
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const trigger = useRef(null)
  const container = useRef(null)
  const load = useCallback(async () => {
    setBusy(true); setError('')
    try { setData(await notificationService.list()) }
    catch { setError('Impossible de charger les notifications.') }
    finally { setBusy(false) }
  }, [])
  useEffect(() => { load() }, [load])
  useEffect(() => {
    if (!open) return
    const dismiss = (event) => {
      if (event.key === 'Escape') { setOpen(false); trigger.current?.focus() }
      if (event.type === 'pointerdown' && !container.current?.contains(event.target)) setOpen(false)
    }
    document.addEventListener('keydown', dismiss)
    document.addEventListener('pointerdown', dismiss)
    return () => { document.removeEventListener('keydown', dismiss); document.removeEventListener('pointerdown', dismiss) }
  }, [open])
  const markAll = async () => {
    setBusy(true); setError('')
    try { await notificationService.readAll(); await load() }
    catch { setError('Lecture non enregistrée. Réessayez.'); setBusy(false) }
  }
  const read = async (id) => {
    try { await notificationService.read(id); setOpen(false); load() }
    catch { setError('Lecture non enregistrée.'); }
  }
  return <div ref={container} className="relative">
    <button ref={trigger} onClick={() => { setOpen(value => !value); if (!open) load() }} aria-label="Notifications" aria-expanded={open} aria-controls="notification-panel" className="relative grid h-9 w-9 place-items-center rounded-lg text-ink-soft hover:bg-white/[0.06]">
      <Icon name="Bell" size={17} />
      {!!data?.unread_count && <span className="absolute right-0 top-0 rounded-full bg-brand-500 px-1 text-xs text-root-950" aria-label={`${data.unread_count} non lues`}>{data.unread_count}</span>}
    </button>
    {open && <section id="notification-panel" aria-label="Centre de notifications" className="absolute right-0 z-50 mt-2 w-[min(330px,calc(100vw-2rem))] rounded-xl border border-line bg-root-800 p-4 shadow-pop">
      <h2 className="font-semibold">Notifications</h2>
      <p className="my-2 text-xs text-ink-dim">Les 20 dernières · actualisation à l’ouverture</p>
      <div className="flex gap-3 text-sm">
        <button disabled={busy} onClick={load}>Actualiser</button>
        <button disabled={busy || !data?.unread_count} onClick={markAll}>Tout marquer lu</button>
      </div>
      {busy && <p role="status">Chargement…</p>}
      {error && <p role="alert">{error}</p>}
      {!busy && !error && !data?.items.length && <p className="mt-3">Aucune notification.</p>}
      <ul className="max-h-80 overflow-y-auto">{data?.items.map(item => <li key={item.id} className="border-b border-line py-3">
        <Link className={item.read_at ? 'text-ink-dim' : 'font-semibold text-ink'} to={/^\/(?!\/)/.test(item.path) ? item.path : '/dashboard'} onClick={() => read(item.id)}>{item.text}</Link>
        <time className="mt-1 block text-xs text-ink-dim" dateTime={item.created_at}>{new Date(item.created_at).toLocaleString()}</time>
      </li>)}</ul>
    </section>}
  </div>
}
