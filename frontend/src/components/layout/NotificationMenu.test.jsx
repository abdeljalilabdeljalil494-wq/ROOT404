import { beforeEach, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import NotificationMenu from './NotificationMenu'
import { notificationService } from '../../services/api'
vi.mock('../../services/api', () => ({ notificationService: { list: vi.fn(), read: vi.fn(), readAll: vi.fn() } }))
beforeEach(() => { cleanup(); vi.clearAllMocks() })
it('loads persisted alerts, records read-all and closes on Escape', async () => {
  notificationService.list.mockResolvedValue({ unread_count: 1, items: [{ id: 'n1', text: 'Actual review', path: '/peer-review', created_at: '2026-11-18T12:00:00Z', read_at: null }] })
  notificationService.readAll.mockResolvedValue({ ok: true })
  render(<MemoryRouter><NotificationMenu /></MemoryRouter>)
  await waitFor(() => expect(notificationService.list).toHaveBeenCalled())
  fireEvent.click(screen.getByRole('button', { name: 'Notifications' }))
  expect(await screen.findByText('Actual review')).toBeVisible()
  notificationService.list.mockResolvedValue({ unread_count: 0, items: [] })
  fireEvent.click(screen.getByText('Tout marquer lu'))
  await waitFor(() => expect(notificationService.readAll).toHaveBeenCalledOnce())
  expect(await screen.findByText('Aucune notification.')).toBeVisible()
  fireEvent.keyDown(document, { key: 'Escape' })
  expect(screen.queryByLabelText('Centre de notifications')).not.toBeInTheDocument()
})
it('shows service failure without invented empty or read-success state', async () => {
  notificationService.list.mockRejectedValue(new Error('offline'))
  render(<MemoryRouter><NotificationMenu /></MemoryRouter>)
  fireEvent.click(screen.getByRole('button', { name: 'Notifications' }))
  expect(await screen.findByRole('alert')).toHaveTextContent('Impossible')
  expect(screen.queryByText('Aucune notification.')).not.toBeInTheDocument()
})
