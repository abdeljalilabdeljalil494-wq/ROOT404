import { useCallback } from 'react'
import { Link, useParams } from 'react-router-dom'
import { http } from '../services/api'
import useResource from '../hooks/useResource'
import ResourceState from '../components/ui/ResourceState'
import Logo from '../components/Logo'

export default function PortfolioLive() {
  const { username } = useParams()
  const resource = useResource(useCallback(() => http.get(username ? `/portfolio/${encodeURIComponent(username)}` : '/portfolio/me/portfolio').then(response => response.data), [username]))
  return <div className="min-h-screen bg-root-900">
    <header className="border-b border-line"><div className="container-page flex flex-wrap items-center justify-between gap-3 py-4"><Logo /><Link to="/dashboard">Mon espace</Link><Link to="/settings">Confidentialité</Link></div></header>
    <main className="container-page space-y-5 py-6">
      {resource.loading || resource.error ? <ResourceState resource={resource} /> : <>
        <section className="card space-y-3 p-6"><h1 className="text-2xl font-bold">{resource.data.displayName || resource.data.username}</h1><p>@{resource.data.username} · {resource.data.campus}</p><p className="whitespace-pre-wrap break-words">{resource.data.bio}</p><p>Niveau {resource.data.level} · {resource.data.xp} XP · {resource.data.projects.length} projets validés</p><p className="text-sm text-ink-dim">Données enregistrées sur ROOT404. Aucun statut d’identité ou compétence certifiée n’est déduit de ce portfolio.</p></section>
        <section className="card space-y-3 p-6"><h2 className="text-xl font-semibold">Projets validés</h2>{!resource.data.projects.length && <p>Aucun projet validé.</p>}<ul>{resource.data.projects.map(project => <li key={project.slug} className="border-b border-line py-3">{project.name} · {project.score}/100</li>)}</ul></section>
        <section className="card space-y-3 p-6"><h2 className="text-xl font-semibold">Compétences enregistrées</h2>{!resource.data.skills.length && <p>Aucune compétence enregistrée.</p>}{resource.data.skills.map(group => <div key={group.group}><h3 className="font-semibold">{group.group}</h3><ul className="flex flex-wrap gap-3">{group.details.map(skill => <li key={skill.name}>{skill.name} : {skill.value}/100</li>)}</ul></div>)}</section>
        <section className="card p-6"><h2 className="text-xl font-semibold">Badges obtenus</h2>{!resource.data.badges.length && <p>Aucun badge obtenu.</p>}<ul>{resource.data.badges.map(badge => <li key={badge.name}>{badge.name} · {badge.tier}</li>)}</ul></section>
      </>}
    </main>
  </div>
}
