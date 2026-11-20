import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { http } from '../../services/api'

export default function OAuthCallback() {
  const { provider } = useParams()
  const navigate = useNavigate()
  const started = useRef(false)
  const [error, setError] = useState('')
  useEffect(() => {
    if (started.current) return
    started.current = true
    const params = new URLSearchParams(window.location.search)
    // Remove authorization code/state from address/history immediately.
    window.history.replaceState(null, '', window.location.pathname)
    if (!['google', 'github'].includes(provider)) { setError('Fournisseur inconnu.'); return }
    http.post(`/auth/oauth/${provider}/complete`, { state: params.get('state') || '', code: params.get('code') || '', error: params.get('error') || '' })
      .then(response => {
        localStorage.setItem('root404_token', response.data.access_token)
        navigate(response.data.linked ? '/settings' : '/dashboard', { replace: true })
      }).catch(failure => setError(typeof failure.response?.data?.detail === 'string' ? failure.response.data.detail : 'Connexion refusée. Recommencez depuis la page de connexion.'))
  }, [provider, navigate])
  return <main className="container-page space-y-4 py-10">
    <h1 className="text-xl">Connexion externe</h1>
    {error ? <><p role="alert">{error}</p><Link to="/login">Retour à la connexion</Link></> : <p role="status">Vérification en cours…</p>}
  </main>
}
