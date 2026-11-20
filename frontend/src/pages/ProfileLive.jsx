import { useCallback } from 'react'
import usePageHeader from '../hooks/usePageHeader'
import useResource from '../hooks/useResource'
import ResourceState from '../components/ui/ResourceState'
import { authService } from '../services/api'
import Button from '../components/ui/Button'

export default function ProfileLive() {
  usePageHeader({ title: 'Mon profil' })
  const resource = useResource(useCallback(() => authService.meSimple(), []))
  return <div className="container-page space-y-5 py-6">
    <h1 className="text-2xl font-bold">Mon profil</h1>
    {resource.loading || resource.error ? <ResourceState resource={resource} /> : <>
      <section className="card space-y-3 p-6"><h2 className="text-xl font-semibold">{resource.data.displayName || resource.data.username}</h2><p>@{resource.data.username}</p><p className="whitespace-pre-wrap break-words">{resource.data.bio || 'Aucune biographie.'}</p><p>{resource.data.campus} · Depuis {resource.data.joined}</p><p className="break-all">Adresse privée : {resource.data.email}</p></section>
      <dl className="card grid gap-4 p-6 sm:grid-cols-2">{[['Niveau',resource.data.level],['XP',resource.data.xp],['Projets validés',resource.data.projectsDone],['Points de correction',resource.data.correctionPoints]].map(([label,value]) => <div key={label}><dt>{label}</dt><dd className="text-xl font-bold">{value}</dd></div>)}</dl>
      <div className="flex flex-wrap gap-3"><Button to="/progress">Missions, badges et réputation</Button><Button to="/moderation">Mes signalements</Button><Button to="/settings">Modifier le profil et la confidentialité</Button><Button to="/portfolio" variant="outline">Prévisualiser mon portfolio</Button><Button onClick={resource.retry} variant="outline">Actualiser le profil</Button></div>
    </>}
  </div>
}
