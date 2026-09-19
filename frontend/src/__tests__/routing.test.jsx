import { render, screen } from '@testing-library/react'
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

describe('application routing', () => {
  it('renders the landing page at /', async () => {
    renderAt('/')
    expect(
      await screen.findByRole('heading', { name: /apprends\. code\. collabore\./i }),
    ).toBeInTheDocument()
  })

  it('renders the login page at /login', async () => {
    renderAt('/login')
    expect(await screen.findByLabelText(/adresse e-mail/i)).toBeInTheDocument()
  })

  it('renders the register page at /register', async () => {
    renderAt('/register')
    expect(await screen.findByText(/rejoins la prochaine piscine/i)).toBeInTheDocument()
  })

  it('renders the 404 page for unknown routes', async () => {
    renderAt('/this/path/does/not/exist')
    expect(await screen.findByText(/cd \/page\/introuvable/i)).toBeInTheDocument()
  })
})
