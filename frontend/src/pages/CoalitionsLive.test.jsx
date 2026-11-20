import { beforeEach, it, expect, vi } from 'vitest'
import { cleanup, render, screen, fireEvent } from '@testing-library/react'
import Coalitions from './CoalitionsLive'
import { coalitionService } from '../services/api'
vi.mock('../hooks/usePageHeader', () => ({ default: () => {} }))
vi.mock('../services/api', () => ({ coalitionService: { list: vi.fn(), me: vi.fn(), join: vi.fn() } }))
beforeEach(() => { cleanup(); vi.clearAllMocks() })
it('shows only real totals and confirms membership after server reload', async () => {
  coalitionService.list.mockResolvedValue([{ id: 'c1', rank: 1, name: 'Actual', points: 17, members: 1 }])
  coalitionService.me.mockResolvedValueOnce({ coalition: null }).mockResolvedValue({ id: 'c1' })
  coalitionService.join.mockResolvedValue({ ok: true })
  render(<Coalitions />)
  fireEvent.click(await screen.findByText('Rejoindre Actual'))
  expect(await screen.findByText('Votre coalition')).toBeVisible()
  expect(screen.getByText('1 membres · 17 XP')).toBeVisible()
  expect(coalitionService.join).toHaveBeenCalledWith('c1')
})
it('shows load failure, not demo rankings', async () => {
  coalitionService.list.mockRejectedValue(new Error('offline'))
  coalitionService.me.mockResolvedValue({ coalition: null })
  render(<Coalitions />)
  expect(await screen.findByRole('alert')).toHaveTextContent('Données indisponibles')
  expect(screen.queryByText('The Phoenix')).not.toBeInTheDocument()
})
