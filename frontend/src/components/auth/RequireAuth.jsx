import { Navigate, Outlet, useLocation } from 'react-router-dom'

const TOKEN_KEY = 'root404_token'

/**
 * Blocks the authenticated app shell (/dashboard, /projects, …) for visitors
 * without a session token and redirects them to /login, remembering where
 * they were headed. The login flow sets `root404_token` on success.
 */
export default function RequireAuth() {
  const location = useLocation()
  const token = localStorage.getItem(TOKEN_KEY)

  if (!token) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }
  return <Outlet />
}
