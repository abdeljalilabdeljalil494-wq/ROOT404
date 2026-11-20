import { useCallback, useState } from 'react'
import { Link } from 'react-router-dom'
import { http } from '../services/api'
import useResource from '../hooks/useResource'
import ResourceState from '../components/ui/ResourceState'
import Button from '../components/ui/Button'
import usePageHeader from '../hooks/usePageHeader'

export default function BetaProgress() {
  usePageHeader({ title: 'Missions et récompenses' })
  const resource = useResource(useCallback(() => http.get('/progress').then(r => r.data), []))
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const claim = async () => {
    setBusy(true); setError('')
    try { await http.post('/progress/mission/claim'); resource.retry() }
    catch { setError('Récompense non confirmée. Une soumission réussie aujourd’hui est requise ; une seule récompense par jour.') }
    finally { setBusy(false) }
  }
  if (resource.loading || resource.error) return <ResourceState resource={resource} />
  const { mission, achievements } = resource.data
  return <div className="container-page space-y-5 py-6">
    <h1 className="text-2xl font-bold">Missions et récompenses</h1>
    {error && <p role="alert">{error}</p>}
    <section className="card space-y-3 p-5"><h2 className="text-xl">{mission.title}</h2>
      <p>{mission.day} · {mission.reward_xp} XP · {mission.status}</p>
      <p>Mission exécutable via le projet Stream Sum. Le juge public reste désactivé : aucune réussite ni XP ne sera simulé.</p>
      {mission.project_slug && <Link to={`/workspace/${mission.project_slug}`}>Ouvrir la mission dans l’éditeur</Link>}
      <Button disabled={busy || mission.status !== 'ready'} onClick={claim}>Réclamer la récompense</Button>
    </section>
    <section className="card space-y-3 p-5"><h2 className="text-xl">Réputation : {achievements.reputation}/100</h2>
      <p>Politique bêta v1 : base50 +2 par projet (max30) +2 par auteur distinct corrigé (max20) −5 par message retiré (max50). Ce n’est pas une certification de confiance.</p>
      <p>Série : {achievements.streak} jours de soumission UTC.</p>
      <ul>{achievements.badges.map(badge => <li key={badge.id}>{badge.name} · {badge.tier} · {badge.earned ? 'Critère atteint' : 'À débloquer'}</li>)}</ul>
      <p className="text-sm">Badges recalculés à partir des données actuelles ; pas de XP supplémentaire ni d’attribution client.</p>
    </section>
  </div>
}
