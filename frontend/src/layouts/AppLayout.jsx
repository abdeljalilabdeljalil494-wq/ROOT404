import { useState } from 'react'
import { Outlet, useOutletContext } from 'react-router-dom'
import Sidebar from '../components/layout/Sidebar'
import AppTopbar from '../components/layout/AppTopbar'

/**
 * Authenticated shell: fixed sidebar (collapsible on < lg) + sticky topbar.
 * Pages set their own topbar title/breadcrumb via the outlet context.
 */
export default function AppLayout() {
  const [open, setOpen] = useState(false)
  const [header, setHeader] = useState({ title: 'ROOT 404', breadcrumb: [] })

  return (
    <div className="min-h-screen bg-root-900">
      <Sidebar open={open} onClose={() => setOpen(false)} />

      <div className="lg:pl-[258px]">
        <AppTopbar
          title={header.title}
          breadcrumb={header.breadcrumb}
          actions={header.actions}
          onMenu={() => setOpen(true)}
        />
        <main className="min-h-[calc(100vh-60px)]">
          <Outlet context={{ setHeader }} />
        </main>
      </div>
    </div>
  )
}

export const useAppHeader = () => useOutletContext()
