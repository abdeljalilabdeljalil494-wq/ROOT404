import { Outlet } from 'react-router-dom'
import Navbar from '../components/layout/Navbar'
import Footer from '../components/layout/Footer'

export default function PublicLayout() {
  return (
    <div className="flex min-h-screen flex-col bg-root-900">
      <Navbar />
      <div role="note" className="border-b border-line bg-root-950 p-3 text-center text-xs text-ink-dim">Version de développement. Les parcours et chiffres de présentation illustrent la vision ROOT404, pas des statistiques d’utilisation vérifiées.</div>
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  )
}
