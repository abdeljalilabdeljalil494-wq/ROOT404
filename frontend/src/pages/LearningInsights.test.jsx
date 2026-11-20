import { beforeEach, expect, it, vi } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import LearningInsights from './LearningInsights'
import { analyticsService, projectService } from '../services/api'
vi.mock('../hooks/usePageHeader', () => ({ default: () => {} }))
vi.mock('../services/api', () => ({ analyticsService: { overview: vi.fn(), skills: vi.fn(), velocity: vi.fn() }, projectService: { list: vi.fn() } }))
beforeEach(() => { cleanup(); vi.clearAllMocks() })
it('shows real prerequisite and progress in journey links', async () => {
  projectService.list.mockResolvedValue([{ id: 'p1', slug: 'webserv', name: 'Webserv', requires: 'minishell', status: 'locked', progress: 0 }])
  render(<MemoryRouter><LearningInsights mode="journey" /></MemoryRouter>)
  expect(await screen.findByRole('link', { name: 'Webserv' })).toHaveAttribute('href', '/projects/webserv')
  expect(screen.getByRole('link', { name: 'minishell' })).toHaveAttribute('href', '/projects/minishell')
  expect(screen.getByText(/locked/)).toBeVisible()
})
it('uses measured analytics, including a real zero rather than fake activity', async () => {
  analyticsService.overview.mockResolvedValue({ velocity: 0, consistency: 0, insight: 'Recorded UTC submissions' })
  analyticsService.velocity.mockResolvedValue({ history: [{ week: 'W1', value: 0 }] })
  render(<LearningInsights mode="analytics" />)
  expect(await screen.findByText('Recorded UTC submissions')).toBeVisible()
  expect(screen.getByText('W1 : 0')).toBeVisible()
})
