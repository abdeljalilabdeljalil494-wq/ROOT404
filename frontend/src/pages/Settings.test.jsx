import { beforeEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import Settings from './Settings'
import { accountService } from '../services/api'
vi.mock('../hooks/usePageHeader', () => ({ default: () => {} }))
vi.mock('../components/RequireAuth', () => ({ useCurrentUser: () => ({ displayName: 'Learner', email: 'owner@example.com' }) }))
vi.mock('../services/api', () => ({ http: { get: vi.fn(), post: vi.fn() }, accountService: { privacy: vi.fn(), savePrivacy: vi.fn(), saveProfile: vi.fn(), exportData: vi.fn(), revokeAll: vi.fn(), deleteAccount: vi.fn() } }))
beforeEach(() => { cleanup(); vi.clearAllMocks(); accountService.privacy.mockResolvedValue({ public_profile: false, directory_visible: false }) })
describe('real account settings', () => {
  it('persists privacy choices and only acknowledges server success', async () => {
    accountService.savePrivacy.mockResolvedValue({ public_profile: true, directory_visible: false })
    render(<Settings />)
    fireEvent.click(await screen.findByLabelText('Portfolio public'))
    fireEvent.click(screen.getByText('Enregistrer la confidentialité'))
    expect(await screen.findByRole('status')).toHaveTextContent('Confidentialité enregistrée.')
    expect(accountService.savePrivacy).toHaveBeenCalledWith({ public_profile: true, directory_visible: false })
  })
  it('does not claim a failed deletion succeeded or remove local auth', async () => {
    accountService.deleteAccount.mockRejectedValue(new Error('offline'))
    localStorage.setItem('root404_token', 'token')
    render(<Settings />)
    const button = await screen.findByText('Supprimer définitivement')
    expect(button).toBeDisabled()
    fireEvent.change(screen.getByLabelText('Confirme ton email'), { target: { value: 'owner@example.com' } })
    fireEvent.click(button)
    expect(await screen.findByRole('alert')).toHaveTextContent('Aucune confirmation de réussite')
    expect(localStorage.getItem('root404_token')).toBe('token')
  })
  it('revokes sessions on the server before local logout', async () => {
    accountService.revokeAll.mockResolvedValue({ ok: true })
    localStorage.setItem('root404_token', 'token')
    render(<Settings />)
    fireEvent.click(await screen.findByText('Révoquer toutes les sessions'))
    expect(await screen.findByRole('status')).toHaveTextContent('Sessions révoquées.')
    expect(accountService.revokeAll).toHaveBeenCalledOnce()
    expect(localStorage.getItem('root404_token')).toBeNull()
  })
})
