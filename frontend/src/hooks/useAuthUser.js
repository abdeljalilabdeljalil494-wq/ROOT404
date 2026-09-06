import { useEffect, useState } from 'react'
import { fetchCurrentUser, getCachedUser } from '../services/api'
import { currentUser as mockUser } from '../data/mock'

/**
 * Current authenticated user, shared by Sidebar / Topbar / pages.
 *
 * Real value comes from `GET /api/auth/me` (JWT in localStorage). Without a
 * session — or when the backend is offline — it degrades to the mock student
 * so the app always renders (dev/demo mode).
 */
export default function useAuthUser() {
  const [user, setUser] = useState(() => getCachedUser() || mockUser)

  useEffect(() => {
    let alive = true
    fetchCurrentUser().then((u) => {
      if (alive && u) setUser(u)
    })
    return () => {
      alive = false
    }
  }, [])

  return user
}
