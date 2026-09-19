import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'

import App from '../App'

function renderAt(path) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>,
  )
}

describe('protected routes', () => {
  it('redirects anonymous visitors from /dashboard to /login', async () => {
    renderAt('/dashboard')
    expect(await screen.findByLabelText(/adresse e-mail/i)).toBeInTheDocument()
    expect(screen.queryByText(/tableau de bord/i)).not.toBeInTheDocument()
  })

  it('redirects anonymous visitors from /projects to /login', async () => {
    renderAt('/projects')
    expect(await screen.findByLabelText(/adresse e-mail/i)).toBeInTheDocument()
  })

  it('allows authenticated users into the app shell', async () => {
    localStorage.setItem('root404_token', 'test.jwt.token')
    renderAt('/dashboard')
    await waitFor(
      () => {
        expect(screen.getAllByText(/tableau de bord/i).length).toBeGreaterThan(0)
      },
      { timeout: 3000 },
    )
    expect(screen.queryByLabelText(/adresse e-mail/i)).not.toBeInTheDocument()
  })
})
