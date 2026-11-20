import { useState } from 'react'
import { http } from '../services/api'
import Button from './ui/Button'

export default function OAuthButtons({ linking = false }) {
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const begin = async (provider) => {
    setBusy(true); setError('')
    try {
      const path = `/auth/oauth/${provider}/${linking ? 'link' : 'start'}`
      const response = linking ? await http.post(path) : await http.get(path)
      const target = new URL(response.data.url)
      if (target.protocol !== 'https:' || !['accounts.google.com', 'github.com'].includes(target.hostname)) throw new Error('Invalid authorization URL')
      window.location.assign(target.href)
    } catch {
      setError('Connexion externe indisponible. Vérifiez la configuration ou reconnectez-vous par email avant de lier un compte.')
      setBusy(false)
    }
  }
  return <section className="space-y-3" aria-label={linking ? 'Lier un compte externe' : 'Connexion externe'}>
    <p className="text-sm text-ink-dim">Google / GitHub : intégration non vérifiée avec des applications réelles. Aucun compte existant ne sera lié automatiquement par email.</p>
    <div className="flex flex-wrap gap-3">{['google', 'github'].map(provider => <Button key={provider} disabled={busy} onClick={() => begin(provider)}>
      {linking ? 'Lier' : 'Continuer avec'} {provider === 'google' ? 'Google' : 'GitHub'}
    </Button>)}</div>
    {error && <p role="alert">{error}</p>}
  </section>
}
