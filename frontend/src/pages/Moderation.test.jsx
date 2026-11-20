import { beforeEach, it, expect, vi } from 'vitest'
import { cleanup, render, screen, fireEvent } from '@testing-library/react'
import Moderation from './Moderation'
import { http } from '../services/api'
import { useCurrentUser } from '../components/RequireAuth'
vi.mock('../hooks/usePageHeader', () => ({ default: () => {} }))
vi.mock('../components/RequireAuth', () => ({ useCurrentUser: vi.fn() }))
vi.mock('../services/api', () => ({ http: { get: vi.fn(), post: vi.fn() } }))
beforeEach(() => { cleanup(); vi.clearAllMocks() })
it('shows private status without staff actions for ordinary users', async () => {
  useCurrentUser.mockReturnValue({ isAdmin: false })
  http.get.mockResolvedValue({ data: [{ id: 'r', reason: 'Reason text', status: 'open' }] })
  render(<Moderation />)
  expect(await screen.findByText('Reason text')).toBeVisible()
  expect(screen.queryByText('Retirer le message')).not.toBeInTheDocument()
})
it('requires server confirmation for administrator decisions', async () => {
  useCurrentUser.mockReturnValue({ isAdmin: true })
  http.get.mockResolvedValue({ data: [{ id: 'r', reason: 'Reason text', status: 'open', message: '<script>not executed</script>' }] })
  http.post.mockRejectedValue(new Error('conflict'))
  render(<Moderation />)
  fireEvent.click(await screen.findByText('Retirer le message'))
  expect(await screen.findByRole('alert')).toHaveTextContent('Décision non confirmée')
  expect(http.post).toHaveBeenCalledWith('/moderation/reports/r/resolve', { action: 'remove' })
})
