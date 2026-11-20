import { createContext, useContext, useEffect, useState } from 'react'
import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { authService } from '../services/api'

const UserContext = createContext(null)
export const useCurrentUser = () => useContext(UserContext)

export default function RequireAuth() {
  const location = useLocation()
  const [user, setUser] = useState(null)
  const [status, setStatus] = useState('loading')
  const [attempt, setAttempt] = useState(0)
  useEffect(() => {
    let alive = true
    const logout = () => { setUser(null); setStatus('unauthorized') }
    window.addEventListener('auth:logout', logout)
    if (!localStorage.getItem('root404_token')) setStatus('unauthorized')
    else authService.meSimple().then(value => {
      if (alive) { setUser(value); setStatus('ready') }
    }).catch(error => {
      if (alive) setStatus(error.response?.status === 401 ? 'unauthorized' : 'error')
    })
    return () => { alive = false; window.removeEventListener('auth:logout', logout) }
  }, [attempt])
  if (status === 'unauthorized') return <Navigate to="/login" replace state={{ from: location.pathname }} />
  if (status === 'loading') return <p role="status" className="p-8">Chargement du compte…</p>
  if (status === 'error') return <div role="alert" className="p-8">Compte indisponible. <button onClick={() => { setStatus('loading'); setAttempt(n => n + 1) }}>Réessayer</button></div>
  return <UserContext.Provider value={user}><Outlet /></UserContext.Provider>
}
