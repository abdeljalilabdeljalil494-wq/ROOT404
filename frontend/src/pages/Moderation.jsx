import { useCallback, useState } from 'react'
import { http } from '../services/api'
import { useCurrentUser } from '../components/RequireAuth'
import useResource from '../hooks/useResource'
import ResourceState from '../components/ui/ResourceState'
import Button from '../components/ui/Button'
import usePageHeader from '../hooks/usePageHeader'

export default function Moderation() {
  usePageHeader({ title: 'Signalements' })
  const user = useCurrentUser()
  const [offset, setOffset] = useState(0)
  const resource = useResource(useCallback(() => http.get(`/moderation/reports?offset=${offset}&limit=50`).then(r => r.data), [offset]), 10000)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const resolve = async (id, action) => {
    setBusy(true); setError('')
    try { await http.post(`/moderation/reports/${id}/resolve`, { action }); resource.retry() }
    catch { setError('Décision non confirmée. Vérifiez les droits et conflits d’intérêts, puis actualisez.') }
    finally { setBusy(false) }
  }
  if (resource.loading || resource.error) return <ResourceState resource={resource} />
  return <div className="container-page space-y-5 py-6">
    <h1 className="text-2xl font-bold">{user.isAdmin ? 'Modération des signalements' : 'Mes signalements'}</h1>
    <p>Actualisation toutes les10secondes (onglet visible). Les raisons restent privées au déclarant et aux administrateurs.</p>
    {error && <p role="alert">{error}</p>}
    {!resource.data.length && <p>Aucun signalement.</p>}
    <ul className="space-y-3">{resource.data.map(report => <li className="card space-y-3 p-5" key={report.id}>
      <p className="whitespace-pre-wrap break-words">{report.reason}</p><p>Statut : {report.status}</p>
      {user.isAdmin && <blockquote className="whitespace-pre-wrap break-words">{report.message}</blockquote>}
      {user.isAdmin && report.status === 'open' && <div className="flex gap-3">
        <Button disabled={busy || report.can_resolve === false} onClick={() => resolve(report.id, 'remove')}>Retirer le message</Button>
        <Button disabled={busy || report.can_resolve === false} onClick={() => resolve(report.id, 'dismiss')}>Classer sans suite</Button>
      </div>}
    </li>)}</ul>
    <div className="flex gap-3"><Button disabled={!offset} onClick={() => setOffset(n => Math.max(0, n - 50))}>Précédent</Button><Button disabled={resource.data.length < 50} onClick={() => setOffset(n => n + 50)}>Suivant</Button></div>
  </div>
}
