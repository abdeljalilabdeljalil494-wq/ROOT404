import { useEffect, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import usePageHeader from '../hooks/usePageHeader'
import Icon from '../components/ui/Icon'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import Avatar from '../components/ui/Avatar'
import ProgressBar from '../components/ui/ProgressBar'
import { chatChannels, chatMessages, roomMembers as mockMembers, rooms as mockRooms, roomTypes } from '../data/mock'
import useAuthUser from '../hooks/useAuthUser'
import { roomService } from '../services/api'

const CHECKLIST = [
  { text: 'Le dépôt clone et compile sans warning', done: true },
  { text: 'La Norminette passe sur tous les fichiers', done: true },
  { text: 'Aucune fuite mémoire (valgrind)', done: true },
  { text: 'Les builtins se comportent comme bash', done: true },
  { text: 'Pipes et redirections combinés', done: false },
  { text: 'Signaux : ctrl-C, ctrl-D, ctrl-\\', done: false },
  { text: 'L’étudiant explique son architecture', done: false },
]

export default function RoomView() {
  const { id = 'r1' } = useParams()
  const me = useAuthUser()
  const fallbackRoom = mockRooms.find((r) => r.id === id) || mockRooms[0]
  const [room, setRoom] = useState(fallbackRoom)
  const [members, setMembers] = useState(mockMembers)
  const [isMember, setIsMember] = useState(false)
  const [joinError, setJoinError] = useState(null)
  const type = roomTypes.find((t) => t.key === room.type) || roomTypes[0]

  usePageHeader(
    { title: room.name, breadcrumb: [{ label: 'Rooms', to: '/rooms' }, { label: room.name }] },
    [id],
  )

  const [messages, setMessages] = useState(chatMessages)
  const [draft, setDraft] = useState('')
  const [channel, setChannel] = useState('minishell')
  const [checks, setChecks] = useState(CHECKLIST)
  const [muted, setMuted] = useState(false)
  const [cam, setCam] = useState(false)
  const scrollRef = useRef(null)

  useEffect(() => {
    let alive = true
    setJoinError(null)
    Promise.all([roomService.detail(id), roomService.messages(id)])
      .then(([d, msgs]) => {
        if (!alive) return
        if (d?.room) setRoom(d.room)
        if (Array.isArray(d?.members) && d.members.length) setMembers(d.members)
        setIsMember(Boolean(d?.isMember))
        if (Array.isArray(msgs) && msgs.length) setMessages(msgs)
      })
      .catch(() => {})
    return () => {
      alive = false
    }
  }, [id])

  useEffect(() => {
    const el = scrollRef.current
    if (el) el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' })
  }, [messages])

  const join = async () => {
    try {
      const r = await roomService.join(id)
      if (r?.id) setRoom(r)
      const d = await roomService.detail(id)
      if (d?.members) setMembers(d.members)
      setIsMember(Boolean(d?.isMember))
    } catch (err) {
      setJoinError(err.response?.data?.detail || err.message)
    }
  }

  const send = async (e) => {
    e.preventDefault()
    if (!draft.trim()) return
    const optimistic = {
      id: Date.now(),
      user: me.username,
      avatar: me.avatar,
      time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
      text: draft.trim(),
      me: true,
    }
    setMessages((m) => [...m, optimistic])
    setDraft('')
    try {
      const saved = await roomService.send(id, draft.trim())
      if (saved?.id) setMessages((m) => m.map((x) => (x.id === optimistic.id ? saved : x)))
    } catch {
      /* garde le message optimiste */
    }
  }

  const doneCount = checks.filter((c) => c.done).length
  const progress = Math.round((doneCount / checks.length) * 100)

  return (
    <div className="flex h-[calc(100vh-60px)] overflow-hidden">
      {/* -------- Channels -------- */}
      <aside className="hidden w-[210px] shrink-0 flex-col border-r border-line bg-root-950 lg:flex">
        <div className="flex h-12 shrink-0 items-center gap-2 border-b border-line px-4">
          <Icon name="MessagesSquare" size={15} className="text-brand-500" />
          <span className="truncate text-[13px] font-bold text-ink">ROOT 404</span>
        </div>
        <div className="flex-1 space-y-4 overflow-y-auto px-2 py-3">
          {chatChannels.map((g) => (
            <div key={g.group}>
              <p className="mb-1 px-2 text-[10px] font-bold uppercase tracking-[0.13em] text-ink-faint">
                {g.group}
              </p>
              {g.items.map((c) => (
                <button
                  key={c.name}
                  onClick={() => setChannel(c.name)}
                  className={`flex w-full items-center gap-2 rounded px-2 py-[6px] text-[12.5px] transition-colors ${
                    channel === c.name ? 'bg-brand-500/12 text-brand-400' : 'text-ink-dim hover:bg-white/[0.04] hover:text-ink'
                  }`}
                >
                  <Icon name={c.icon} size={13} className="shrink-0" />
                  <span className="truncate">{c.name}</span>
                </button>
              ))}
            </div>
          ))}
        </div>
        <div className="flex shrink-0 items-center gap-2 border-t border-line p-2.5">
          <Avatar src={me.avatar} name={me.displayName} size="xs" status="online" />
          <div className="min-w-0 flex-1">
            <p className="truncate text-[11.5px] font-semibold text-ink">{me.displayName}</p>
            <p className="truncate text-[10px] text-ok">En ligne</p>
          </div>
          <button className="grid h-7 w-7 place-items-center rounded text-ink-faint hover:text-ink" aria-label="Paramètres">
            <Icon name="Settings" size={13} />
          </button>
        </div>
      </aside>

      {/* -------- Chat -------- */}
      <section className="flex min-w-0 flex-1 flex-col bg-root-900">
        <header className="flex h-12 shrink-0 items-center gap-3 border-b border-line px-4">
          <span className="grid h-7 w-7 place-items-center rounded-md" style={{ background: `${type.color}18`, color: type.color }}>
            <Icon name={type.icon} size={14} />
          </span>
          <div className="min-w-0">
            <h1 className="truncate text-[13.5px] font-semibold text-ink">{room.name}</h1>
            <p className="truncate font-mono text-[10.5px] text-ink-dim">{room.project}</p>
          </div>
          {room.live && <Badge tone="danger" dot className="ml-1">Live</Badge>}
          {isMember ? (
            <Badge tone="ok" dot className="ml-1">Tu es membre</Badge>
          ) : (
            <Button size="sm" variant="outline" icon="Users" className="ml-1" onClick={join}>
              Rejoindre
            </Button>
          )}
          {joinError && <span className="ml-1 text-[11px] text-danger">{joinError}</span>}
          <div className="ml-auto flex items-center gap-1">
            {['Video', 'Monitor', 'Users', 'MoreHorizontal'].map((i) => (
              <button key={i} aria-label={i} className="grid h-8 w-8 place-items-center rounded-md text-ink-dim transition-colors hover:bg-white/[0.06] hover:text-ink">
                <Icon name={i} size={15} />
              </button>
            ))}
          </div>
        </header>

        <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto p-4">
          <div className="mx-auto max-w-md rounded-lg border border-line bg-root-850 p-4 text-center">
            <Icon name="ShieldCheck" size={20} className="mx-auto text-brand-500" />
            <p className="mt-2 text-[12px] font-semibold text-ink">Session de correction enregistrée</p>
            <p className="mt-1 text-[11.5px] leading-relaxed text-ink-dim">
              Un rapport de session sera généré automatiquement et attaché aux deux profils.
            </p>
          </div>

          {messages.map((m) => (
            <div key={m.id} className={`flex gap-3 ${m.me ? 'flex-row-reverse' : ''}`}>
              <Avatar src={m.avatar} name={m.user} size="sm" />
              <div className={`max-w-[76%] ${m.me ? 'items-end text-right' : ''} flex flex-col`}>
                <div className={`flex items-center gap-2 ${m.me ? 'flex-row-reverse' : ''}`}>
                  <span className="text-[12px] font-semibold text-ink">@{m.user}</span>
                  <span className="text-[10.5px] text-ink-faint">{m.time}</span>
                </div>
                <p
                  className={`mt-1.5 rounded-xl px-3.5 py-2.5 text-[13px] leading-relaxed ${
                    m.me
                      ? 'rounded-tr-sm bg-brand-500/15 text-ink'
                      : 'rounded-tl-sm border border-line bg-root-800 text-ink-soft'
                  }`}
                >
                  {m.text}
                </p>
              </div>
            </div>
          ))}
                  </div>

        {/* Call bar */}
        <div className="flex shrink-0 items-center justify-center gap-2 border-t border-line bg-root-950 py-2.5">
          {[
            { i: muted ? 'MicOff' : 'Mic', on: !muted, act: () => setMuted((v) => !v), label: 'Micro' },
            { i: cam ? 'Video' : 'VideoOff', on: cam, act: () => setCam((v) => !v), label: 'Caméra' },
            { i: 'MonitorUp', on: false, act: () => {}, label: 'Partager l’écran' },
            { i: 'Hand', on: false, act: () => {}, label: 'Lever la main' },
          ].map((b) => (
            <button
              key={b.i}
              onClick={b.act}
              aria-label={b.label}
              title={b.label}
              className={`grid h-9 w-9 place-items-center rounded-lg transition-colors ${
                b.on ? 'bg-white/10 text-ink' : 'text-ink-dim hover:bg-white/[0.06] hover:text-ink'
              }`}
            >
              <Icon name={b.i} size={16} />
            </button>
          ))}
          <button
            aria-label="Quitter l'appel"
            className="ml-2 grid h-9 w-11 place-items-center rounded-lg bg-danger text-white transition-colors hover:bg-danger/85"
          >
            <Icon name="PhoneOff" size={16} />
          </button>
        </div>

        <form onSubmit={send} className="flex shrink-0 items-center gap-2 border-t border-line p-3">
          <button type="button" aria-label="Joindre" className="grid h-9 w-9 shrink-0 place-items-center rounded-lg text-ink-dim hover:bg-white/[0.06] hover:text-ink">
            <Icon name="Paperclip" size={16} />
          </button>
          <input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder={`Écrire dans #${channel}…`}
            className="input flex-1"
          />
          <Button type="submit" size="sm" className="h-10 w-10 shrink-0 !px-0" aria-label="Envoyer">
            <Icon name="Send" size={15} />
          </Button>
        </form>
      </section>

      {/* -------- Right rail -------- */}
      <aside className="hidden w-[290px] shrink-0 flex-col overflow-y-auto border-l border-line bg-root-950 xl:flex">
        <div className="border-b border-line p-4">
          <div className="flex items-center justify-between">
            <h2 className="text-[12px] font-bold uppercase tracking-wider text-ink-dim">Checklist</h2>
            <span className="font-mono text-[11.5px] font-bold text-brand-500">{doneCount}/{checks.length}</span>
          </div>
          <ProgressBar value={progress} height={5} className="mt-2.5" />
          <ul className="mt-3.5 space-y-1.5">
            {checks.map((c, i) => (
              <li key={c.text}>
                <button
                  onClick={() => setChecks((cs) => cs.map((x, j) => (j === i ? { ...x, done: !x.done } : x)))}
                  className="flex w-full items-start gap-2.5 rounded-md px-1.5 py-1.5 text-left transition-colors hover:bg-white/[0.03]"
                >
                  <span
                    className={`mt-0.5 grid h-4 w-4 shrink-0 place-items-center rounded border ${
                      c.done ? 'border-ok bg-ok text-[#04090E]' : 'border-line-strong'
                    }`}
                  >
                    {c.done && <Icon name="Check" size={11} strokeWidth={3} />}
                  </span>
                  <span className={`text-[11.5px] leading-snug ${c.done ? 'text-ink-faint line-through' : 'text-ink-soft'}`}>
                    {c.text}
                  </span>
                </button>
              </li>
            ))}
          </ul>
          <Button size="sm" full className="mt-3.5" icon="Send">Valider la correction</Button>
        </div>

        <div className="p-4">
          <h2 className="mb-3 text-[12px] font-bold uppercase tracking-wider text-ink-dim">
            Membres — {members.length}
          </h2>
          <ul className="space-y-1">
            {members.map((m) => (
              <li
                key={m.name}
                className={`flex items-center gap-2.5 rounded-md px-1.5 py-1.5 transition-colors hover:bg-white/[0.03] ${
                  m.me ? 'bg-brand-500/[0.07]' : ''
                }`}
              >
                <Avatar src={m.avatar} name={m.name} size="xs" status={m.status} />
                <div className="min-w-0 flex-1">
                  <p className={`truncate text-[12px] ${m.status === 'offline' ? 'text-ink-faint' : 'text-ink-soft'}`}>
                    @{m.name}
                  </p>
                  <p className="truncate text-[10px] text-ink-faint">{m.role}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>

        <div className="mt-auto border-t border-line p-4">
          <Link
            to="/mentor"
            className="flex items-center gap-2.5 rounded-lg border border-brand-500/25 bg-brand-500/[0.07] p-3 transition-colors hover:bg-brand-500/[0.12]"
          >
            <Icon name="Sparkles" size={16} className="text-brand-500" />
            <div className="min-w-0">
              <p className="text-[12px] font-semibold text-ink">AI Mentor</p>
              <p className="truncate text-[10.5px] text-ink-dim">Invite l'assistant dans la room</p>
            </div>
          </Link>
        </div>
      </aside>
    </div>
  )
}
