import OAuthButtons from '../components/OAuthButtons'
import { useCallback, useState } from 'react'
import usePageHeader from '../hooks/usePageHeader'
import { useCurrentUser } from '../components/RequireAuth'
import { accountService } from '../services/api'
import useResource from '../hooks/useResource'
import ResourceState from '../components/ui/ResourceState'
import Button from '../components/ui/Button'

export default function Settings() {
  usePageHeader({ title: 'Paramètres' })
  const user = useCurrentUser()
  const resource = useResource(useCallback(() => accountService.privacy(), []))
  const [profile, setProfile] = useState({ display_name: user.displayName, bio: user.bio || '' })
  const [busy, setBusy] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [confirmation, setConfirmation] = useState('')
  const [preferences, setPreferences] = useState(null)
  const logoutLocal = () => {
    localStorage.removeItem('root404_token')
    window.dispatchEvent(new Event('auth:logout'))
  }
  const action = async (operation, success) => {
    setBusy(true); setError(''); setMessage('')
    try {
      await operation()
      setMessage(success)
    } catch (failure) {
      setError(typeof failure.response?.data?.detail === 'string' ? failure.response.data.detail : 'Action indisponible. Aucune confirmation de réussite reçue.')
    } finally { setBusy(false) }
  }
  const download = async () => {
    const data = await accountService.exportData()
    const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' }))
    const link = document.createElement('a')
    link.href = url; link.download = 'root404-export.json'
    link.click(); URL.revokeObjectURL(url)
  }
  if (resource.loading || resource.error) return <ResourceState resource={resource} />
  const privacy = preferences || resource.data
  return <div className="container-page space-y-5 py-6">
    <h1 className="text-2xl font-bold text-white">Paramètres du compte</h1>
    <section className="card p-5"><OAuthButtons linking /></section>
    {error && <p role="alert" className="text-danger">{error}</p>}
    {message && <p role="status" className="text-brand-400">{message}</p>}
    <section className="card space-y-4 p-5">
      <h2 className="font-bold">Profil</h2>
      <label className="block">Nom affiché<input className="input mt-2 w-full" maxLength={50} value={profile.display_name}
        onChange={e => setProfile({ ...profile, display_name: e.target.value })} /></label>
      <label className="block">Bio<textarea className="input mt-2 w-full" maxLength={1000} value={profile.bio}
        onChange={e => setProfile({ ...profile, bio: e.target.value })} /></label>
      <Button disabled={busy || !profile.display_name.trim()} onClick={() => action(() => accountService.saveProfile(profile), 'Profil enregistré. Le nouveau nom sera visible après rechargement.')}>Enregistrer le profil</Button>
    </section>
    <section className="card space-y-4 p-5">
      <h2 className="font-bold">Confidentialité</h2>
      <p className="text-sm text-ink-dim">Le profil et la présence dans les classements/recherches sont privés par défaut. Aucun email n’est affiché sur le portfolio public.</p>
      <label className="flex gap-3"><input type="checkbox" checked={privacy.public_profile} onChange={e => setPreferences({ ...privacy, public_profile: e.target.checked })} />Portfolio public</label>
      <label className="flex gap-3"><input type="checkbox" checked={privacy.directory_visible} onChange={e => setPreferences({ ...privacy, directory_visible: e.target.checked })} />Apparaître dans les classements et la recherche</label>
      <Button disabled={busy} onClick={() => action(() => accountService.savePrivacy(privacy), 'Confidentialité enregistrée.')}>Enregistrer la confidentialité</Button>
    </section>
    <section className="card space-y-4 p-5">
      <h2 className="font-bold">Données et sessions</h2>
      <p className="text-sm text-ink-dim">L’export et la suppression nécessitent une connexion de moins de dix minutes. L’export inclut uniquement tes données propres, pas les données privées des autres membres.</p>
      <div className="flex flex-wrap gap-3">
        <Button disabled={busy} variant="outline" onClick={() => action(download, 'Export préparé pour téléchargement.')}>Exporter mes données</Button>
        <Button disabled={busy} variant="outline" onClick={() => action(async () => { await accountService.revokeAll(); logoutLocal() }, 'Sessions révoquées.')}>Révoquer toutes les sessions</Button>
      </div>
    </section>
    <section className="card space-y-4 border-danger/40 p-5">
      <h2 className="font-bold text-danger">Supprimer le compte</h2>
      <p className="text-sm text-ink-dim">Irréversible : supprime le compte et ses données propres dans la base active. Les références partagées sont anonymisées. Les copies de sauvegarde expirent selon la politique de l’opérateur ; aucun effacement instantané des sauvegardes n’est promis.</p>
      <label className="block">Confirme ton email<input type="email" className="input mt-2 w-full" value={confirmation} onChange={e => setConfirmation(e.target.value)} /></label>
      <Button variant="outline" disabled={busy || confirmation !== user.email} onClick={() => action(async () => { await accountService.deleteAccount(confirmation); logoutLocal() }, 'Compte supprimé.')}>Supprimer définitivement</Button>
    </section>
  </div>
}
