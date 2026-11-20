import { useCallback, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import usePageHeader from '../hooks/usePageHeader'
import { roomService } from '../services/api'
import useResource from '../hooks/useResource'
import ResourceState from '../components/ui/ResourceState'
import Button from '../components/ui/Button'

export default function Rooms() {
  usePageHeader({ title: 'Rooms' })
  const navigate = useNavigate()
  const resource = useResource(useCallback(() => roomService.list(), []))
  const [name, setName] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const enter = async (room) => {
    setBusy(true); setError('')
    try { await roomService.join(room.id); navigate(`/rooms/${room.id}`) }
    catch (failure) { setError(failure.response?.data?.detail || 'Impossible de rejoindre la room.') }
    finally { setBusy(false) }
  }
  const create = async (event) => {
    event.preventDefault(); setBusy(true); setError('')
    try { const room = await roomService.create({ name: name.trim(), type: 'study', capacity: 10 }); navigate(`/rooms/${room.id}`) }
    catch { setError('Création impossible. Aucune room confirmée.') }
    finally { setBusy(false) }
  }
  return <div className="container-page space-y-5 py-6">
    <h1 className="text-2xl font-bold">Collaboration Rooms</h1>
    <p className="text-ink-dim">Salons publics et messages persistants. Actualisation manuelle ; audio, vidéo, partage d’écran et édition collaborative non intégrés.</p>
    <form className="card flex flex-wrap gap-3 p-5" onSubmit={create}>
      <label className="flex-1">Nom de la room<input className="input mt-2 w-full" maxLength={100} required value={name} onChange={e => setName(e.target.value)} /></label>
      <Button type="submit" disabled={busy || !name.trim()}>Créer une room</Button>
    </form>
    {error && <p role="alert">{String(error)}</p>}
    {resource.loading || resource.error ? <ResourceState resource={resource} /> : <>
      <Button variant="outline" onClick={resource.retry}>Actualiser les rooms</Button>
      {!resource.data.length && <p>Aucune room publique.</p>}
      <div className="grid gap-4 md:grid-cols-2">{resource.data.map(room => <section key={room.id} className="card space-y-3 p-5">
        <h2 className="font-bold">{room.name}</h2><p>{room.members}/{room.capacity} membres · {room.host}</p>
        <Button disabled={busy} onClick={() => enter(room)}>Rejoindre {room.name}</Button>
      </section>)}</div>
    </>}
  </div>
}
