import { useCallback, useEffect, useState } from 'react'
import usePageHeader from '../hooks/usePageHeader'
import Icon from '../components/ui/Icon'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import Tabs from '../components/ui/Tabs'
import Avatar from '../components/ui/Avatar'
import ProgressBar from '../components/ui/ProgressBar'
import EmptyState from '../components/ui/EmptyState'
import useAuthUser from '../hooks/useAuthUser'
import { peerService, projectService } from '../services/api'

const EMPTY_DATA = {
  upcoming: [],
  available: [],
  history: [],
  stats: { given: 0, received: 0 },
}

/* Preset times for « Ouvrir un créneau » (local ISO, backend formats it). */
const SLOT_TIMES = [
  { label: "Aujourd'hui", hours: 1 },
  { label: "Aujourd'hui +2 h", hours: 2 },
  { label: 'Demain 10:00', hours: 20 },
  { label: 'Demain 14:00', hours: 24 },
]

function MatchRing({ value }) {
  const tone = value >= 90 ? '#2ECC71' : value >= 80 ? '#F8851F' : '#F5B942'
  return (
    <div className="flex flex-col items-center">
      <span className="font-mono text-[15px] font-extrabold" style={{ color: tone }}>{value}%</span>
      <span className="text-[9.5px] uppercase tracking-wider text-ink-faint">match</span>
    </div>
  )
}

/* Inline correction form for the reviewer on a « Tu corriges » row. */
function CorrectionForm({ slot, onDone, onErr }) {
  const [score, setScore] = useState(100)
  const [comment, setComment] = useState('')
  const [busy, setBusy] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true)
    try {
      const r = await peerService.complete(slot.id, score, comment)
      onDone(r)
    } catch (err) {
      onErr(err.response?.data?.detail || err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <form onSubmit={submit} className="mt-3 w-full max-w-xl rounded-lg border border-line bg-root-850 p-3.5">
      <div className="flex items-center gap-4">
        <label className="flex items-center gap-2 text-[12px] text-ink-soft" htmlFor={`score-${slot.id}`}>
          Note
          <input
            id={`score-${slot.id}`}
            type="range"
            min="0"
            max="100"
            step="5"
            value={score}
            onChange={(e) => setScore(Number(e.target.value))}
            className="w-40 accent-[#F8851F]"
          />
          <span className={`w-9 text-right font-mono text-[14px] font-bold ${score >= 75 ? 'text-ok' : 'text-danger'}`}>
            {score}
          </span>
        </label>
        <input
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="Commentaire (facultatif)…"
          className="input h-8 flex-1 py-0 text-[12px]"
        />
        <Button size="sm" type="submit" loading={busy} disabled={busy}>
          Valider la correction
        </Button>
      </div>
      <p className="mt-2 text-[10.5px] text-ink-faint">
        ≥ 75 → le projet est validé · &lt; 75 → retour en échec (pénalité 2 j) · tu gagnes +20 CP et +50 XP.
      </p>
    </form>
  )
}

export default function PeerReview() {
  usePageHeader({ title: 'Peer Review' })
  const currentUser = useAuthUser()
  const [tab, setTab] = useState('upcoming')
  const [data, setData] = useState(EMPTY_DATA)
  const [loading, setLoading] = useState(true)
  const [notice, setNotice] = useState(null) // { tone, text }
  const [busyId, setBusyId] = useState(null)
  const [reviewing, setReviewing] = useState(null) // slot id with the form open

  // Slot-creator state
  const [creatorOpen, setCreatorOpen] = useState(false)
  const [projects, setProjects] = useState([])
  const [pickProject, setPickProject] = useState('')
  const [pickWhen, setPickWhen] = useState(SLOT_TIMES[0].hours)

  const load = useCallback(async () => {
    try {
      const d = await peerService.list()
      setData({ ...EMPTY_DATA, ...(d || {}) })
    } catch {
      setData(EMPTY_DATA)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const flash = (tone, text) => {
    setNotice({ tone, text })
    setTimeout(() => setNotice(null), 5000)
  }

  const openCreator = async () => {
    if (creatorOpen) {
      setCreatorOpen(false)
      return
    }
    try {
      const list = await projectService.list()
      const done = (list || []).filter((p) => p.status === 'done')
      setProjects(done)
      if (done.length) setPickProject(done[0].slug)
      setCreatorOpen(true)
    } catch {
      flash('danger', 'Impossible de charger tes projets validés.')
    }
  }

  const createSlot = async (e) => {
    e.preventDefault()
    if (!pickProject) return
    setBusyId('create')
    try {
      const when = new Date(Date.now() + pickWhen * 3600 * 1000).toISOString()
      await peerService.createSlot(pickProject, when)
      flash('ok', `Créneau ouvert pour « ${pickProject} » — les correcteurs peuvent maintenant se proposer.`)
      setCreatorOpen(false)
      load()
    } catch (err) {
      flash('danger', err.response?.data?.detail || err.message)
    } finally {
      setBusyId(null)
    }
  }

  const reserve = async (slot) => {
    setBusyId(slot.id)
    try {
      await peerService.reserve(slot.id)
      flash('ok', `Correction réservée — tu corriges @${slot.peer} sur « ${slot.project} ».`)
      load()
    } catch (err) {
      flash('danger', err.response?.data?.detail || err.message)
    } finally {
      setBusyId(null)
    }
  }

  const cancel = async (slot) => {
    setBusyId(slot.id)
    try {
      await peerService.cancel(slot.id)
      flash('ok', slot.role === 'Tu corriges' ? 'Tu t’es retiré de ce créneau.' : 'Créneau annulé.')
      load()
    } catch (err) {
      flash('danger', err.response?.data?.detail || err.message)
    } finally {
      setBusyId(null)
    }
  }

  const { upcoming, available, history, stats } = data

  return (
    <div className="container-page space-y-5 py-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-[24px] font-extrabold tracking-tight text-white">Peer Review</h1>
          <p className="mt-1.5 text-[13px] text-ink-dim">
            Smart Matchmaking · niveau, disponibilité, langue et réputation pris en compte
          </p>
        </div>
        <Button icon="CalendarPlus" variant={creatorOpen ? 'outline' : 'solid'} onClick={openCreator}>
          {creatorOpen ? 'Fermer' : 'Ouvrir un créneau'}
        </Button>
      </div>

      {/* Slot creator */}
      {creatorOpen && (
        <form onSubmit={createSlot} className="card flex flex-wrap items-center gap-3 p-4">
          <Icon name="CalendarPlus" size={16} className="text-brand-500" />
          <label className="text-[12px] text-ink-soft" htmlFor="slot-project">Projet validé</label>
          <select
            id="slot-project"
            value={pickProject}
            onChange={(e) => setPickProject(e.target.value)}
            className="input h-9 w-44 py-0 font-mono text-[12px]"
          >
            {projects.length === 0 && <option value="">Aucun projet validé</option>}
            {projects.map((p) => (
              <option key={p.slug} value={p.slug}>{p.slug}</option>
            ))}
          </select>
          <label className="text-[12px] text-ink-soft" htmlFor="slot-when">Horaires</label>
          <select
            id="slot-when"
            value={pickWhen}
            onChange={(e) => setPickWhen(Number(e.target.value))}
            className="input h-9 w-36 py-0 text-[12px]"
          >
            {SLOT_TIMES.map((t) => (
              <option key={t.hours} value={t.hours}>{t.label}</option>
            ))}
          </select>
          <Button size="sm" type="submit" loading={busyId === 'create'} className="ml-auto" disabled={!pickProject}>
            Ouvrir le créneau
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

      {/* KPI */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {[
          { l: 'Correction Points', v: currentUser.correctionPoints.toLocaleString('fr-FR'), i: 'Coins', t: 'text-brand-500' },
          { l: 'Corrections données', v: stats.given, i: 'ClipboardCheck', t: 'text-ok' },
          { l: 'Corrections reçues', v: stats.received, i: 'Inbox', t: 'text-info' },
          { l: 'Reputation Score', v: `${currentUser.reputation}/100`, i: 'Star', t: 'text-warn' },
        ].map((s) => (
          <div key={s.l} className="card flex items-center gap-3.5 p-4">
            <span className={`grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-white/[0.04] ${s.t}`}>
              <Icon name={s.i} size={18} />
            </span>
            <div>
              <p className="text-[11px] uppercase tracking-wider text-ink-dim">{s.l}</p>
              <p className="font-mono text-[18px] font-extrabold text-ink">{s.v}</p>
            </div>
          </div>
        ))}
      </div>

      <section className="card overflow-hidden">
        <Tabs
          active={tab}
          onChange={setTab}
          tabs={[
            { key: 'upcoming', label: 'Mes slots', count: upcoming.length },
            { key: 'available', label: 'Slots disponibles', count: available.length },
            { key: 'history', label: 'Historique', count: history.length },
          ]}
        />

        {loading ? (
          <div className="grid place-items-center py-14">
            <span className="h-6 w-6 animate-spin rounded-full border-2 border-line border-t-brand-500" />
          </div>
        ) : (
          <>
            {tab === 'upcoming' && (
              <ul className="divide-y divide-line/70">
                {upcoming.length === 0 && (
                  <li>
                    <EmptyState icon="CalendarClock" title="Aucun slot en cours" text="Ouvre un créneau pour ton projet validé." />
                  </li>
                )}
                {upcoming.map((r) => (
                  <li key={r.id} className="px-5 py-4">
                    <div className="flex flex-wrap items-center gap-4">
                      {r.peer ? (
                        <Avatar src={r.avatar} name={r.peer} size="md" status="online" />
                      ) : (
                        <span className="grid h-10 w-10 shrink-0 place-items-center rounded-full border border-dashed border-line text-ink-faint">
                          <Icon name="Clock" size={16} />
                        </span>
                      )}
                      <div className="min-w-0 flex-1">
                        <div className="flex flex-wrap items-center gap-2">
                          {r.peer ? (
                            <p className="text-[13.5px] font-semibold text-ink">@{r.peer}</p>
                          ) : (
                            <p className="text-[13.5px] font-semibold text-ink-soft">En attente d'un correcteur…</p>
                          )}
                          {r.peer && <Badge tone="muted">Niv. {Number(r.level).toFixed(2)}</Badge>}
                          <Badge tone={r.role === 'Tu corriges' ? 'brand' : 'info'}>{r.role}</Badge>
                        </div>
                        <p className="mt-1 flex flex-wrap items-center gap-x-4 gap-y-1 text-[11.5px] text-ink-dim">
                          <span className="font-mono text-ink-soft">{r.project}</span>
                          <span className="flex items-center gap-1.5"><Icon name="CalendarClock" size={12} /> {r.when}</span>
                          {r.peer && (
                            <span className="flex items-center gap-1.5"><Icon name="Languages" size={12} /> {r.languages}</span>
                          )}
                        </p>
                      </div>
                      {r.peer && <MatchRing value={r.match} />}
                      <div className="flex gap-2">
                        <Button to="/rooms/r1" size="sm" icon="Video">Rejoindre</Button>
                        {r.role === 'Tu corriges' && (
                          <Button
                            size="sm"
                            variant="outline"
                            icon="ClipboardCheck"
                            onClick={() => setReviewing((v) => (v === r.id ? null : r.id))}
                          >
                            Terminer
                          </Button>
                        )}
                        {r.canCancel && (
                          <Button
                            size="sm"
                            variant="ghost"
                            icon="X"
                            className="px-2.5"
                            aria-label="Annuler"
                            loading={busyId === r.id}
                            onClick={() => cancel(r)}
                          />
                        )}
                      </div>
                    </div>
                    {reviewing === r.id && (
                      <CorrectionForm
                        slot={r}
                        onDone={(res) => {
                          setReviewing(null)
                          flash(
                            res.passed ? 'ok' : 'danger',
                            res.passed
                              ? `Correction validée — « ${r.project} » validé. +20 CP, +50 XP.`
                              : `Note ${res.score} < 75 — le projet repasse en échec (pénalité 2 j). +20 CP, +50 XP.`,
                          )
                          load()
                        }}
                        onErr={(m) => flash('danger', m)}
                      />
                    )}
                  </li>
                ))}
              </ul>
            )}

            {tab === 'available' && (
              <ul className="divide-y divide-line/70">
                {available.length === 0 && (
                  <li>
                    <EmptyState icon="Users" title="Aucun slot disponible" text="Les créneaux ouverts par les autres étudiants apparaîtront ici." />
                  </li>
                )}
                {available.map((r) => (
                  <li key={r.id} className="flex flex-wrap items-center gap-4 px-5 py-4 transition-colors hover:bg-white/[0.02]">
                    <Avatar src={r.avatar} name={r.peer} size="md" />
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <p className="text-[13.5px] font-semibold text-ink">@{r.peer}</p>
                        <Badge tone="muted">Niv. {Number(r.level).toFixed(2)}</Badge>
                        {r.rep >= 90 && <Badge tone="ok"><Icon name="ShieldCheck" size={10} /> Trusted</Badge>}
                      </div>
                      <p className="mt-1 flex flex-wrap items-center gap-x-4 gap-y-1 text-[11.5px] text-ink-dim">
                        <span className="font-mono text-ink-soft">{r.project}</span>
                        <span className="flex items-center gap-1.5"><Icon name="CalendarClock" size={12} /> {r.when}</span>
                        <span className="flex items-center gap-1.5"><Icon name="Languages" size={12} /> {r.languages}</span>
                      </p>
                      <div className="mt-2 flex items-center gap-2">
                        <span className="text-[10.5px] text-ink-faint">Réputation</span>
                        <ProgressBar value={r.rep} height={4} className="w-24" />
                        <span className="font-mono text-[10.5px] text-ink-soft">{r.rep}</span>
                      </div>
                    </div>
                    <MatchRing value={r.match} />
                    <Button
                      size="sm"
                      variant="outline"
                      iconRight="ArrowRight"
                      disabled={!r.canReserve || busyId === r.id}
                      loading={busyId === r.id}
                      title={r.canReserve ? undefined : 'Ton niveau doit être ≥ au sien pour le corriger'}
                      onClick={() => reserve(r)}
                    >
                      Réserver
                    </Button>
                  </li>
                ))}
              </ul>
            )}

            {tab === 'history' && (
              history.length ? (
                <ul className="divide-y divide-line/70">
                  {history.map((h) => (
                    <li key={h.id} className="flex items-center gap-4 px-5 py-4">
                      <Avatar src={h.avatar} name={h.peer} size="sm" />
                      <div className="min-w-0 flex-1">
                        <p className="text-[13px] font-semibold text-ink">@{h.peer}</p>
                        <p className="font-mono text-[11.5px] text-ink-dim">{h.project}</p>
                      </div>
                      <Badge tone={h.given ? 'brand' : 'info'}>{h.given ? 'Donnée' : 'Reçue'}</Badge>
                      <span className="hidden w-28 text-right text-[11.5px] text-ink-faint sm:block">{h.date}</span>
                      <span className={`w-12 text-right font-mono text-[15px] font-extrabold ${h.score >= 100 ? 'text-ok' : h.score >= 75 ? 'text-warn' : 'text-danger'}`}>
                        {h.score}
                      </span>
                    </li>
                  ))}
                </ul>
              ) : (
                <EmptyState icon="History" title="Aucune correction" text="Ton historique apparaîtra ici." />
              )
            )}
          </>
        )}
      </section>
    </div>
  )
}
