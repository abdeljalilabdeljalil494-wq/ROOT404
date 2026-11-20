import { useCallback } from 'react'
import { Link } from 'react-router-dom'
import usePageHeader from '../hooks/usePageHeader'
import useResource from '../hooks/useResource'
import ResourceState from '../components/ui/ResourceState'
import { analyticsService, projectService } from '../services/api'
import Button from '../components/ui/Button'

const TITLES = { journey: 'Learning Journey', skills: 'Skill Graph', analytics: 'Analytics' }

export default function LearningInsights({ mode }) {
  usePageHeader({ title: TITLES[mode] }, [mode])
  const resource = useResource(useCallback(async () => {
    if (mode === 'journey') return projectService.list()
    if (mode === 'skills') return analyticsService.skills()
    const [overview, velocity] = await Promise.all([analyticsService.overview(), analyticsService.velocity()])
    return { overview, velocity }
  }, [mode]))
  return <div className="container-page space-y-5 py-6">
    <h1 className="text-2xl font-bold">{TITLES[mode]}</h1>
    <Button variant="outline" onClick={resource.retry}>Actualiser les données</Button>
    {resource.loading || resource.error ? <ResourceState resource={resource} /> : <>
      {mode === 'journey' && <><p>Progression personnelle et prérequis du catalogue. Un projet verrouillé n’est pas considéré terminé.</p><ol className="space-y-3">{resource.data.map(project => <li key={project.id} className="card space-y-2 p-5"><h2 className="font-semibold"><Link to={`/projects/${project.slug}`}>{project.name}</Link></h2><p>{project.level} · {project.status} · {project.progress || 0}%</p>{project.requires && <p>Prérequis : <Link to={`/projects/${project.requires}`}>{project.requires}</Link></p>}</li>)}</ol>{!resource.data.length && <p>Catalogue vide.</p>}</>}
      {mode === 'skills' && <><p>Indicateurs internes enregistrés, mis à jour par les projets. Ce ne sont pas des certifications externes.</p>{resource.data.map(group => <section key={group.group} className="card p-5"><h2 className="mb-3 font-semibold">{group.group}</h2><ul className="space-y-3">{group.skills.map(skill => <li key={skill.name}><label className="flex items-center gap-3">{skill.name}<progress aria-label={skill.name} className="max-w-[45%]" value={skill.value} max="100" /><span>{skill.value}/100</span></label></li>)}</ul></section>)}{!resource.data.length && <p>Aucune compétence enregistrée.</p>}</>}
      {mode === 'analytics' && <><p>{resource.data.overview.insight}</p><dl className="grid gap-4 sm:grid-cols-2"><div className="card p-5"><dt>Soumissions sur 7 jours</dt><dd className="text-2xl font-bold">{resource.data.overview.velocity}</dd></div><div className="card p-5"><dt>Jours actifs sur 28 jours</dt><dd className="text-2xl font-bold">{resource.data.overview.consistency}%</dd></div></dl><section className="card space-y-3 p-5"><h2 className="font-semibold">Soumissions par semaine (UTC)</h2><ul>{resource.data.velocity.history.map(week => <li key={week.week}>{week.week} : {week.value}</li>)}</ul></section><p className="text-sm text-ink-dim">Aucune prévision, durée de résolution ou activité non mesurée n’est inventée.</p></>}
    </>}
  </div>
}
