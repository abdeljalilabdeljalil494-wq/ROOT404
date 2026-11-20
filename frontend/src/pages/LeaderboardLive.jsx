import { useCallback, useState } from 'react'
import usePageHeader from '../hooks/usePageHeader'
import useResource from '../hooks/useResource'
import ResourceState from '../components/ui/ResourceState'
import { leaderboardService } from '../services/api'
import Button from '../components/ui/Button'

export default function LeaderboardLive() {
  usePageHeader({ title: 'Classement' })
  const [campus, setCampus] = useState('')
  const resource = useResource(useCallback(() => leaderboardService.global({ campus, limit: 100 }), [campus]))
  return <div className="container-page space-y-5 py-6">
    <h1 className="text-2xl font-bold">Classement ROOT404</h1>
    <p className="text-ink-dim">Les 100 premiers profils actifs ayant choisi d’apparaître dans l’annuaire. Rang dans le filtre sélectionné, trié par niveau puis XP. Votre visibilité se règle dans les paramètres.</p>
    <label className="block">Campus<select className="select ml-3" value={campus} onChange={event => setCampus(event.target.value)}><option value="">Tous</option>{['Tunis','Sousse','Sfax','Paris','Remote'].map(name => <option key={name}>{name}</option>)}</select></label>
    <Button variant="outline" onClick={resource.retry}>Actualiser le classement</Button>
    {resource.loading || resource.error ? <ResourceState resource={resource} /> : !resource.data.length ? <p>Aucun profil visible pour ce filtre.</p> : <div className="overflow-x-auto"><table className="w-full text-left"><caption className="sr-only">Classement par niveau et expérience</caption><thead><tr>{['Rang','Profil','Niveau','XP','Campus','Coalition'].map(label => <th key={label} scope="col" className="p-3">{label}</th>)}</tr></thead><tbody>{resource.data.map(row => <tr key={row.user} className="border-t border-line"><td className="p-3">{row.rank}</td><th scope="row" className="p-3">{row.name || row.user}{row.me ? ' (vous)' : ''}</th><td className="p-3">{row.level}</td><td className="p-3">{row.xp}</td><td className="p-3">{row.campus}</td><td className="p-3">{row.coalition}</td></tr>)}</tbody></table></div>}
  </div>
}
