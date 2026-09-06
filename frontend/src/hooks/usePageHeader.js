import { useEffect } from 'react'
import { useAppHeader } from '../layouts/AppLayout'

/**
 * Lets any page inside <AppLayout> drive the topbar title / breadcrumb / actions.
 */
export default function usePageHeader(header, deps = []) {
  const ctx = useAppHeader?.() || {}
  const setHeader = ctx.setHeader

  useEffect(() => {
    setHeader?.(header)
    document.title = `${header.title || 'ROOT 404'} — ROOT 404`
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)
}
