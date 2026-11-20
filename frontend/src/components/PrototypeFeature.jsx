import { Link } from 'react-router-dom'
import { USE_MOCK } from '../services/api'

/** Keep unfinished legacy screens available only in explicitly selected demos. */
export default function PrototypeFeature({ children }) {
  if (USE_MOCK) return <><div role="status" className="border-b border-warn p-3 text-warn">MODE DÉMONSTRATION — données fictives, actions non garanties.</div>{children}</>
  return <section className="container-page py-12">
    <h1 className="text-xl font-bold">Fonctionnalité en cours d’intégration</h1>
    <p className="my-4 text-ink-dim">Cette interface de démonstration n’est pas encore connectée aux données réelles. Aucun résultat fictif ne sera affiché.</p>
    <Link className="text-brand-500" to="/projects">Consulter les projets</Link>
  </section>
}
