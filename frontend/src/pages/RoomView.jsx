import { useCallback, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import usePageHeader from '../hooks/usePageHeader'
import { http, roomService } from '../services/api'
import useResource from '../hooks/useResource'
import ResourceState from '../components/ui/ResourceState'
import Button from '../components/ui/Button'

export default function RoomView() {
  usePageHeader({ title: 'Room' })
  const { id } = useParams()
  const navigate = useNavigate()
  const resource = useResource(useCallback(() => roomService.get(id), [id]), 5000)
  const [reportMessage, setReportMessage] = useState('')
  const [reason, setReason] = useState('')
  const [confirmation, setConfirmation] = useState('')
  const [draft, setDraft] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const send = async (event) => {
    event.preventDefault(); setBusy(true); setError('')
    try { await roomService.sendMessage(id, draft.trim()); setDraft(''); resource.retry() }
    catch { setError('Message non confirmé. Réessaie sans perdre ton texte.') }
    finally { setBusy(false) }
  }
  const report = async (event) => {
    event.preventDefault(); setBusy(true); setError(''); setConfirmation('')
    try { await http.post('/moderation/reports', { message_id: reportMessage, reason }); setReportMessage(''); setReason(''); setConfirmation('Signalement enregistré.') }
    catch { setError('Signalement non confirmé (droits, doublon ou validation).') }
    finally { setBusy(false) }
  }
  const leave = async () => {
    setBusy(true); setError('')
    try { const result = await roomService.leave(id); if (!result.ok) throw new Error(); navigate('/rooms') }
    catch { setError('Départ non confirmé.'); setBusy(false) }
  }
  if (resource.loading || resource.error) return <ResourceState resource={resource} />
  const room = resource.data
  return <div className="container-page space-y-5 py-6">
    <h1 className="text-2xl font-bold">{room.name}</h1>
    <p className="text-ink-dim">Messages persistants · actualisation toutes les5secondes (onglet visible). Aucun état de présence en temps réel n’est garanti.</p>
    {error && <p role="alert">{error}</p>}
    {confirmation && <p role="status">{confirmation}</p>}
    {reportMessage && <form onSubmit={report} className="card p-5 space-y-3"><label>Raison du signalement<textarea className="input w-full" minLength={5} maxLength={1000} required value={reason} onChange={e => setReason(e.target.value)} /></label><Button disabled={busy || reason.trim().length < 5} type="submit">Envoyer le signalement</Button><Button type="button" onClick={() => setReportMessage('')}>Annuler</Button></form>}
    <div className="flex flex-wrap gap-3"><Button variant="outline" onClick={resource.retry}>Actualiser les messages</Button><Button variant="outline" disabled={busy} onClick={leave}>Quitter la room</Button></div>
    <section className="card space-y-3 p-5" aria-label="Messages">
      {!room.messages.length && <p>Aucun message.</p>}
      {room.messages.map(message => <article key={message.id} className="border-b border-line py-2"><strong>{message.user}</strong><p className="whitespace-pre-wrap break-words">{message.text}</p>{!message.me && <Button disabled={busy} variant="outline" onClick={() => { setReportMessage(message.id); setConfirmation('') }}>Signaler le message de {message.user}</Button>}</article>)}
    </section>
    <form onSubmit={send} className="card space-y-3 p-5">
      <label className="block">Message<textarea className="input mt-2 w-full" maxLength={2000} required value={draft} onChange={e => setDraft(e.target.value)} /></label>
      <Button type="submit" disabled={busy || !draft.trim()}>Envoyer le message</Button>
    </form>
    <section className="card p-5"><h2 className="font-bold">Membres</h2><ul>{room.members.map(member => <li key={member.id}>{member.displayName} · {member.role}</li>)}</ul></section>
  </div>
}
