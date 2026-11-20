import { beforeEach, describe, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import Login from './Login'
import { authService } from '../../services/api'

vi.mock('../../services/api', () => ({ authService: { requestOtp: vi.fn(), verifyOtp: vi.fn() } }))
beforeEach(() => { cleanup(); localStorage.clear(); vi.clearAllMocks() })
function open() {
  render(<MemoryRouter initialEntries={['/login']}><Routes>
    <Route path="/login" element={<Login />} />
    <Route path="/dashboard" element={<h1>Real dashboard</h1>} />
  </Routes></MemoryRouter>)
}
describe('login form integration', () => {
  it('does not claim an OTP was sent when delivery fails', async () => {
    authService.requestOtp.mockRejectedValue(new Error('unavailable'))
    open()
    fireEvent.change(screen.getByLabelText('Adresse e-mail'), { target: { value: 'learner@example.com' } })
    fireEvent.submit(screen.getByLabelText('Adresse e-mail').closest('form'))
    expect(await screen.findByRole('alert')).toBeInTheDocument()
    expect(screen.queryByLabelText('Chiffre 1')).not.toBeInTheDocument()
  })
  it('requests and verifies the real code, storing only returned bearer', async () => {
    authService.requestOtp.mockResolvedValue({ sent: true })
    authService.verifyOtp.mockResolvedValue({ access_token: 'server.signed.token' })
    open()
    fireEvent.change(screen.getByLabelText('Adresse e-mail'), { target: { value: 'learner@example.com' } })
    fireEvent.submit(screen.getByLabelText('Adresse e-mail').closest('form'))
    await screen.findByLabelText('Chiffre 1')
    '192837'.split('').forEach((digit, i) => fireEvent.change(screen.getByLabelText(`Chiffre ${i + 1}`), { target: { value: digit } }))
    fireEvent.submit(screen.getByLabelText('Chiffre 1').closest('form'))
    expect(await screen.findByText('Real dashboard')).toBeInTheDocument()
    expect(authService.verifyOtp).toHaveBeenCalledWith('learner@example.com', '192837')
    expect(localStorage.getItem('root404_token')).toBe('server.signed.token')
  })
})
