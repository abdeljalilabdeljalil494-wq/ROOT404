import { describe, expect, it, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, cleanup } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import RequireAuth from './RequireAuth'
import { authService } from '../services/api'

vi.mock('../services/api', () => ({ authService: { meSimple: vi.fn() } }))
beforeEach(() => { cleanup(); localStorage.clear(); vi.clearAllMocks() })
function renderRoute() {
  return render(<MemoryRouter initialEntries={['/private']}><Routes>
    <Route element={<RequireAuth />}><Route path="/private" element={<h1>Private account</h1>} /></Route>
    <Route path="/login" element={<h1>Sign in</h1>} />
  </Routes></MemoryRouter>)
}
describe('protected navigation', () => {
  it('redirects visitors without a token', async () => {
    renderRoute()
    expect(await screen.findByText('Sign in')).toBeInTheDocument()
    expect(authService.meSimple).not.toHaveBeenCalled()
  })
  it('waits for backend token validation', async () => {
    localStorage.setItem('root404_token', 'a.b.c')
    authService.meSimple.mockResolvedValue({ id: 'learner' })
    renderRoute()
    expect(await screen.findByText('Private account')).toBeInTheDocument()
  })
  it('does not confuse a network failure with a valid session', async () => {
    localStorage.setItem('root404_token', 'a.b.c')
    authService.meSimple.mockRejectedValue(new Error('offline'))
    renderRoute()
    await waitFor(() => expect(screen.getByRole('alert')).toBeInTheDocument())
    expect(screen.queryByText('Private account')).not.toBeInTheDocument()
  })
})
