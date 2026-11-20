import { beforeEach, it, expect, vi } from 'vitest'
import { cleanup, render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import BetaProgress from './BetaProgress'
import { http } from '../services/api'
vi.mock('../hooks/usePageHeader', () => ({ default: () => {} }))
vi.mock('../services/api', () => ({ http: { get: vi.fn(), post: vi.fn() } }))
const snapshot = status => ({ mission: { day: '2026-11-18', title: 'Stream Sum', project_slug: 'foundations-sum-python', reward_xp: 25, status }, achievements: { reputation: 50, streak: 0, badges: [{ id: 'first', name: 'Premier projet', tier: 'bronze', earned: false }] } })
beforeEach(() => { cleanup(); vi.clearAllMocks() })
it('does not permit client completion of an unverified mission', async () => {
  http.get.mockResolvedValue({ data: snapshot('available') })
  render(<MemoryRouter><BetaProgress /></MemoryRouter>)
  expect(await screen.findByText('Réclamer la récompense')).toBeDisabled()
  expect(screen.getByText('Ouvrir la mission dans l’éditeur')).toHaveAttribute('href', '/workspace/foundations-sum-python')
  expect(http.post).not.toHaveBeenCalled()
})
it('claims only after server eligibility and reloads confirmed state', async () => {
  http.get.mockResolvedValueOnce({ data: snapshot('ready') }).mockResolvedValue({ data: snapshot('claimed') })
  http.post.mockResolvedValue({ data: { xp_earned: 25 } })
  render(<MemoryRouter><BetaProgress /></MemoryRouter>)
  fireEvent.click(await screen.findByText('Réclamer la récompense'))
  expect(await screen.findByText(/claimed/)).toBeVisible()
  expect(http.post).toHaveBeenCalledWith('/progress/mission/claim')
  expect(screen.getByText('Réclamer la récompense')).toBeDisabled()
})
it('shows error rather than granting reward offline', async () => {
  http.get.mockResolvedValue({ data: snapshot('ready') }); http.post.mockRejectedValue(new Error('offline'))
  render(<MemoryRouter><BetaProgress /></MemoryRouter>)
  fireEvent.click(await screen.findByText('Réclamer la récompense'))
  expect(await screen.findByRole('alert')).toHaveTextContent('non confirmée')
})
