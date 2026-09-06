import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import usePageHeader from '../hooks/usePageHeader'
import Icon from '../components/ui/Icon'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import Avatar from '../components/ui/Avatar'
import EmptyState from '../components/ui/EmptyState'
import { rooms as mockRooms, roomTypes } from '../data/mock'
import { roomService } from '../services/api'

const FEATURES = ['Chat', 'Voice / Video', 'Code Editor', 'Shared Terminal', 'Screen Sharing', 'AI Mentor', 'Checklist', 'Session Report']

export default function Rooms() {
  usePageHeader({ title: 'Rooms' })
  const [rooms, setRooms] = useState(mockRooms)
  const [type, setType] = useState('all')
  const [creating, setCreating] = useState(false)
  const [busy, setBusy] = useState(false)
  const [notice, setNotice] = useState(null)
  const [form, setForm] = useState({ name: '', type: 'study', project: '', capacity: 10 })

  const load = async () => {
    try {
      const d = await roomService.list()
      if (Array.isArray(d) && d.length) setRooms(d)
    } catch {
      /* offline → mock fallback déjà en place */
    }
  }

  useEffect(() => {
    load()
  }, [])

  const flash = (tone, text) => {
    setNotice({ tone, text })
    setTimeout(() => setNotice(null), 5000)
  }

  const createRoom = async (e) => {
    e.preventDefault()
    if (!form.name.trim()) return
    setBusy(true)
    try {
      await roomService.create({ ...form, name: form.name.trim(), capacity: Number(form.capacity) })
      flash('ok', `Room « ${form.name.trim()} » créée — tu es l'hôte.`)
      setCreating(false)
      setForm({ name: '', type: 'study', project: '', capacity: 10 })
      load()
    } catch (err) {
      flash('danger', err.response?.data?.detail || err.message)
    } finally {
      setBusy(false)
    }
  }

  const list = type === 'all' ? rooms : rooms.filter((r) => r.type === type)

  return (
    <div className="container-page space-y-5 py-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-[24px] font-extrabold tracking-tight text-white">Collaboration Rooms</h1>
          <p className="mt-1.5 text-[13px] text-ink-dim">
            {rooms.filter((r) => r.live).length} rooms actives · WebRTC + WebSockets · Enregistrement du rapport de session
          </p>
        </div>
        <Button icon="Plus" variant={creating ? 'outline' : 'solid'} onClick={() => setCreating((v) => !v)}>
          {creating ? 'Fermer' : 'Créer une room'}
        </Button>
      </div>

      {/* Room creator */}
      {creating && (
        <form onSubmit={createRoom} className="card flex flex-wrap items-end gap-3 p-4">
          <label className="flex flex-col gap-1 text-[11px] font-semibold uppercase tracking-wider text-ink-dim">
            Nom
            <input
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              placeholder="Ex : Correction minishell — binôme"
              className="input h-9 w-56 py-0 text-[12.5px] font-normal normal-case tracking-normal"
            />
          </label>
          <label className="flex flex-col gap-1 text-[11px] font-semibold uppercase tracking-wider text-ink-dim">
            Type
            <select
              value={form.type}
              onChange={(e) => setForm((f) => ({ ...f, type: e.target.value }))}
              className="input h-9 w-44 py-0 text-[12.5px] font-normal normal-case tracking-normal"
            >
              {roomTypes.map((t) => (
                <option key={t.key} value={t.key}>{t.label}</option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-1 text-[11px] font-semibold uppercase tracking-wider text-ink-dim">
            Projet
            <input
              value={form.project}
              onChange={(e) => setForm((f) => ({ ...f, project: e.target.value }))}
              placeholder="minishell…"
              className="input h-9 w-36 py-0 font-mono text-[12px] font-normal normal-case tracking-normal"
            />
          </label>
          <label className="flex flex-col gap-1 text-[11px] font-semibold uppercase tracking-wider text-ink-dim">
            Capacité
            <input
              type="number"
              min="2"
              max="500"
              value={form.capacity}
              onChange={(e) => setForm((f) => ({ ...f, capacity: e.target.value }))}
              className="input h-9 w-20 py-0 text-[12.5px] font-normal normal-case tracking-normal"
            />
          </label>
          <Button size="sm" type="submit" loading={busy} className="ml-auto" disabled={!form.name.trim()}>
            Créer la room
          </Button>
        </form>
      )}

      {notice && (
        <div
          className={`flex items-center gap-2.5 rounded-lg border px-4 py-3 text-[12.5px] ${
            notice.tone === 'ok' ? 'border-ok/30 bg-ok/[0.07] text-ok' : 'border-danger/30 bg-danger/[0.07] text-danger'
          }`}
        >
          <Icon name={notice.tone === 'ok' ? 'CircleCheck' : 'AlertTriangle'} size={15} />
          {notice.text}
        </div>
      )}

      {/* Type filter */}
      <div className="no-scrollbar -mx-1 flex gap-2 overflow-x-auto px-1 pb-1">
        <button
          onClick={() => setType('all')}
          className={`shrink-0 rounded-lg border px-3.5 py-2 text-[12px] font-semibold transition-colors ${
            type === 'all' ? 'border-brand-500/50 bg-brand-500/12 text-brand-500' : 'border-line text-ink-dim hover:text-ink'
          }`}
        >
          Toutes ({rooms.length})
        </button>
        {roomTypes.map((t) => {
          const n = rooms.filter((r) => r.type === t.key).length
          const on = type === t.key
          return (
            <button
              key={t.key}
              onClick={() => setType(t.key)}
              className={`flex shrink-0 items-center gap-2 rounded-lg border px-3.5 py-2 text-[12px] font-semibold transition-colors ${
                on ? 'border-brand-500/50 bg-brand-500/12 text-brand-500' : 'border-line text-ink-dim hover:text-ink'
              }`}
            >
              <Icon name={t.icon} size={14} style={{ color: on ? undefined : t.color }} />
              {t.label} <span className="text-ink-faint">({n})</span>
            </button>
          )
        })}
      </div>

      {list.length === 0 ? (
        <div className="card"><EmptyState icon="MessagesSquare" title="Aucune room de ce type" text="Crée la première et invite ta coalition." action={<Button size="sm" icon="Plus">Créer une room</Button>} /></div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {list.map((r) => {
            const t = roomTypes.find((x) => x.key === r.type)
            const full = r.members >= r.capacity
            return (
              <article key={r.id} className="card group flex flex-col p-5 transition-all hover:-translate-y-1 hover:border-line-strong">
                <div className="flex items-start justify-between gap-3">
                  <span className="grid h-10 w-10 place-items-center rounded-lg" style={{ background: `${t.color}18`, color: t.color }}>
                    <Icon name={t.icon} size={19} />
                  </span>
                  {r.live ? <Badge tone="danger" dot>Live</Badge> : <Badge tone="muted">Planifiée</Badge>}
                </div>

                <h3 className="mt-4 text-[14.5px] font-bold text-ink">{r.name}</h3>
                <p className="mt-1 text-[11.5px] font-medium" style={{ color: t.color }}>{t.label}</p>
                <p className="mt-2 font-mono text-[12px] text-ink-dim">{r.project}</p>

                <div className="mt-3 flex flex-wrap gap-1.5">
                  {r.tags.map((tag) => <span key={tag} className="chip">{tag}</span>)}
                </div>

                <div className="mt-auto flex items-center justify-between gap-3 border-t border-line pt-4 [margin-top:1.25rem]">
                  <div className="flex items-center gap-2">
                    <div className="flex -space-x-2">
                      {Array.from({ length: Math.min(3, r.members) }).map((_, i) => (
                        <Avatar key={i} src={`https://i.pravatar.cc/48?img=${20 + i + r.id.length}`} name={`m${i}`} size="xs" className="ring-2 ring-root-800" />
                      ))}
                    </div>
                    <span className="text-[11.5px] text-ink-dim">{r.members}/{r.capacity}</span>
                  </div>
                  <Button to={`/rooms/${r.id}`} size="sm" variant={full ? 'outline' : 'primary'} iconRight="ArrowRight">
                    {full ? 'Observer' : 'Rejoindre'}
                  </Button>
                </div>
              </article>
            )
          })}
        </div>
      )}

      {/* Capability strip */}
      <section className="card p-6">
        <h2 className="text-[14px] font-bold text-ink">Chaque room embarque</h2>
        <p className="mt-1.5 text-[12.5px] text-ink-dim">
          Le même socle technique quel que soit le type de session.
        </p>
        <div className="mt-5 grid grid-cols-2 gap-2.5 sm:grid-cols-4">
          {FEATURES.map((f) => (
            <div key={f} className="flex items-center gap-2 rounded-lg border border-line bg-root-850 px-3 py-2.5">
              <Icon name="Check" size={13} className="shrink-0 text-ok" />
              <span className="truncate text-[12px] text-ink-soft">{f}</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
