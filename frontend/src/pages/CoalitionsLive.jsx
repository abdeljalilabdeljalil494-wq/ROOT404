import { useCallback, useState } from 'react'
import { coalitionService } from '../services/api'
import useResource from '../hooks/useResource'
import ResourceState from '../components/ui/ResourceState'
import Button from '../components/ui/Button'
import usePageHeader from '../hooks/usePageHeader'

export default function CoalitionsLive() {
  usePageHeader({ title: 'Coalitions' })
  const resource = useResource(useCallback(async () => ({ list: await coalitionService.list(), mine: await coalitionService.me() }), []))
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const join = async (id) => {
    setBusy(true); setError('')
    try { await coalitionService.join(id); resource.retry() }
    catch { setError('Adhésion impossible. Une seule coalition par compte ; aucun transfert automatique.') }
    finally { setBusy(false) }
  }
  if (resource.loading || resource.error) return <ResourceState resource={resource} />
  return <div className="container-page space-y-5 py-6">
    <h1 className="text-2xl font-bold">Coalitions</h1>
    <p>Classement calculé à partir des XP des comptes actifs. Les guerres et récompenses collectives sont à venir.</p>
    {error && <p role="alert">{error}</p>}
    {!resource.data.list.length && <p role="status">Aucune coalition disponible.</p>}
    <ul className="space-y-3">{resource.data.list.map(coalition => <li className="card p-5" key={coalition.id}>
      <h2 className="font-bold">{coalition.rank}. {coalition.name}</h2>
      <p>{coalition.motto}</p><p>{coalition.members} membres · {coalition.points} XP</p>
      {resource.data.mine.id === coalition.id ? <p role="status">Votre coalition</p> : !resource.data.mine.id && <Button disabled={busy} onClick={() => join(coalition.id)}>Rejoindre {coalition.name}</Button>}
    </li>)}</ul>
  </div>
}
