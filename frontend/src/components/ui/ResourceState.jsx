export default function ResourceState({ resource }) {
  if (resource.loading) return <p role="status" className="p-8">Chargement…</p>
  if (resource.error) return <div role="alert" className="p-8">Données indisponibles. <button onClick={resource.retry}>Réessayer</button></div>
  return null
}
