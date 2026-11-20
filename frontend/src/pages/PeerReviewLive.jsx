import { useCallback, useState } from 'react'
import usePageHeader from '../hooks/usePageHeader'
import useResource from '../hooks/useResource'
import ResourceState from '../components/ui/ResourceState'
import Button from '../components/ui/Button'
import { peerReviewService, projectService } from '../services/api'

export default function PeerReviewLive() {
  usePageHeader({ title: 'Peer Review' })
  const resource = useResource(useCallback(async () => {
    const [reviews, slots, projects] = await Promise.all([peerReviewService.list(), peerReviewService.slots(), projectService.list()])
    return { reviews, slots, projects }
  }, []))
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [detail, setDetail] = useState(null)
  const [score, setScore] = useState(0)
  const [comment, setComment] = useState('')
  const act = async (operation, success) => {
    setBusy(true); setError(''); setMessage('')
    try { await operation(); setMessage(success); resource.retry() }
    catch (failure) { setError(typeof failure.response?.data?.detail === 'string' ? failure.response.data.detail : 'Opération impossible. Aucun succès confirmé.') }
    finally { setBusy(false) }
  }
  const create = (event) => {
    event.preventDefault()
    const values = new FormData(event.currentTarget)
    act(() => peerReviewService.createSlot({ project_id: values.get('project'), start_time: new Date(values.get('start')).toISOString(), end_time: new Date(values.get('end')).toISOString() }), 'Créneau publié.')
  }
  const inspect = async (review) => {
    setBusy(true); setError('')
    try { setDetail({ ...await peerReviewService.get(review.id), role: review.role }); setScore(review.score ?? 0); setComment('') }
    catch { setError('Impossible de charger la correction.') }
    finally { setBusy(false) }
  }
  const submit = (event) => {
    event.preventDefault()
    act(async () => { await peerReviewService.review(detail.id, { score: Number(score), comment }); setDetail(null) }, 'Avis enregistré. Aucun résultat automatique du Judge n’est remplacé.')
  }
  if (resource.loading || resource.error) return <div className="container-page py-6"><ResourceState resource={resource} /></div>
  const { reviews, slots, projects } = resource.data
  return <div className="container-page space-y-5 py-6">
    <h1 className="text-2xl font-bold">Peer Review</h1>
    <p className="text-ink-dim">Publiez un créneau, réservez avec une soumission existante, consultez et rédigez un avis humain. Horaires dans votre fuseau local. Les avis ne valident pas automatiquement un projet.</p>
    {error && <p role="alert">{error}</p>}{message && <p role="status">{message}</p>}
    <Button disabled={busy} variant="outline" onClick={resource.retry}>Actualiser les corrections</Button>
    <form onSubmit={create} className="card grid gap-4 p-5 md:grid-cols-2">
      <h2 className="font-semibold md:col-span-2">Proposer un créneau (5 à 120 minutes)</h2>
      <label>Projet<select name="project" className="select mt-1 w-full" required>{projects.map(project => <option key={project.id} value={project.id}>{project.name}</option>)}</select></label>
      <label>Début<input name="start" className="input mt-1 w-full" type="datetime-local" required /></label>
      <label>Fin<input name="end" className="input mt-1 w-full" type="datetime-local" required /></label>
      <Button type="submit" disabled={busy}>Publier le créneau</Button>
    </form>
    <section className="card space-y-3 p-5"><h2 className="font-semibold">Créneaux disponibles</h2>
      {!slots.length && <p>Aucun créneau disponible.</p>}
      {slots.map(slot => <div key={slot.id} className="flex flex-wrap items-center justify-between gap-3 border-b border-line py-3">
        <p>{projects.find(project => project.id === slot.project_id)?.name || 'Projet non précisé'} · {slot.corrector} · {new Date(slot.start_time+'Z').toLocaleString()}</p>
        <Button disabled={busy} onClick={() => act(() => peerReviewService.bookSlot(slot.id), 'Correction réservée.')}>Réserver ce créneau</Button>
      </div>)}
    </section>
    <section className="card space-y-3 p-5"><h2 className="font-semibold">Mes corrections</h2>
      {!reviews.total && <p>Aucune correction.</p>}
      {[...reviews.as_corrector, ...reviews.as_author].map(review => <div key={review.id} className="flex flex-wrap items-center justify-between gap-3 border-b border-line py-3">
        <p>{review.project_name} · {review.role === 'corrector' ? 'Correcteur' : 'Auteur'} · {review.status}{review.score != null ? ` · ${review.score}/100` : ''}</p>
        <Button disabled={busy} onClick={() => inspect(review)}>Consulter la correction</Button>
      </div>)}
    </section>
    {detail && <section className="card space-y-3 p-5" aria-label="Détail de la correction">
      <h2 className="font-semibold">{detail.project} · {detail.status}</h2>
      <Button variant="outline" onClick={() => setDetail(null)}>Fermer le détail</Button>
      {Object.entries(detail.files).map(([name, content]) => <details key={name}><summary>{name}</summary><pre className="max-h-96 overflow-auto whitespace-pre-wrap break-all text-sm">{content}</pre></details>)}
      <p>{detail.comment || 'Aucun commentaire.'}</p>
      {detail.role === 'corrector' && detail.status !== 'completed' && <form onSubmit={submit} className="space-y-3">
        <label className="block">Note sur 100<input className="input ml-2" type="number" min="0" max="100" required value={score} onChange={event => setScore(event.target.value)} /></label>
        <label className="block">Commentaire<textarea className="input mt-2 w-full" maxLength={5000} value={comment} onChange={event => setComment(event.target.value)} /></label>
        <Button type="submit" disabled={busy}>Enregistrer l’avis définitif</Button>
      </form>}
    </section>}
  </div>
}
