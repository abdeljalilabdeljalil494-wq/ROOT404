import { beforeEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import Mentor from './Mentor'
import { aiService } from '../services/api'

vi.mock('../hooks/usePageHeader', () => ({ default: () => {} }))
vi.mock('../components/RequireAuth', () => ({ useCurrentUser: () => ({ displayName: 'Real learner', avatar: null }) }))
vi.mock('../services/api', () => ({ aiService: { history: vi.fn(), levels: vi.fn(), gaps: vi.fn(), ask: vi.fn() } }))
beforeEach(() => {
  cleanup(); vi.clearAllMocks()
  // jsdom does not implement the browser Element scrolling API.
  Element.prototype.scrollTo = vi.fn()
  aiService.history.mockResolvedValue([])
  aiService.levels.mockResolvedValue([{ n: 2, label: 'Question socratique' }])
  aiService.gaps.mockResolvedValue({ gaps: [] })
})
describe('provider-backed mentor screen', () => {
  it('loads actual history and displays only the service answer', async () => {
    aiService.ask.mockResolvedValue({ role: 'ai', text: 'A provider-backed answer' })
    render(<Mentor />)
    await screen.findByText('Aucun échange enregistré. Pose une question pour commencer.')
    fireEvent.change(screen.getByLabelText('Question au mentor'), { target: { value: 'Explain this pointer' } })
    fireEvent.click(screen.getByLabelText('Envoyer'))
    expect(await screen.findByText('A provider-backed answer')).toBeInTheDocument()
    expect(aiService.ask).toHaveBeenCalledWith('Explain this pointer', 2)
  })
  it('reports provider failure without a canned response or fake successful message', async () => {
    aiService.ask.mockRejectedValue({ response: { status: 503, data: { detail: 'AI provider unavailable' } } })
    render(<Mentor />)
    await screen.findByLabelText('Question au mentor')
    fireEvent.change(screen.getByLabelText('Question au mentor'), { target: { value: 'Help' } })
    fireEvent.click(screen.getByLabelText('Envoyer'))
    expect(await screen.findByRole('alert')).toHaveTextContent('AI provider unavailable')
    expect(screen.getByLabelText('Question au mentor')).toHaveValue('Help')
    expect(screen.getByText('Aucun échange enregistré. Pose une question pour commencer.')).toBeInTheDocument()
  })
  it('does not substitute fixtures if history cannot load', async () => {
    aiService.history.mockRejectedValue(new Error('offline'))
    render(<Mentor />)
    expect(await screen.findByRole('alert')).toHaveTextContent('Données indisponibles')
    expect(screen.queryByLabelText('Question au mentor')).not.toBeInTheDocument()
  })
})
