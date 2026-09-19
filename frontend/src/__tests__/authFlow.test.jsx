import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'

import Login from '../pages/auth/Login'
import Register from '../pages/auth/Register'

describe('login flow (OTP two-step)', () => {
  function renderLogin() {
    return render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>,
    )
  }

  it('marks the e-mail field required and type=email (client-side validation)', () => {
    renderLogin()
    const email = screen.getByLabelText(/adresse e-mail/i)
    expect(email).toBeRequired()
    expect(email).toHaveAttribute('type', 'email')
  })

  it('advances to the OTP step after submitting a valid e-mail', async () => {
    const user = userEvent.setup()
    renderLogin()
    await user.type(screen.getByLabelText(/adresse e-mail/i), 'etudiant@exemple.tn')
    await user.click(screen.getByRole('button', { name: /recevoir mon code/i }))

    // The mock request resolves after ~800ms; the OTP inputs then appear.
    expect(await screen.findByText(/code de vérification/i, {}, { timeout: 2500 })).toBeInTheDocument()
    expect(screen.getByLabelText(/chiffre 1/i)).toBeInTheDocument()
    expect(screen.getByText(/etudiant@exemple.tn/i)).toBeInTheDocument()
  })

  it('shows a loading state on the submit button while requesting', async () => {
    const user = userEvent.setup()
    renderLogin()
    await user.type(screen.getByLabelText(/adresse e-mail/i), 'etudiant@exemple.tn')
    await user.click(screen.getByRole('button', { name: /recevoir mon code/i }))
    // The Button renders a spinner (animate-spin) and disables itself.
    await waitFor(() => expect(screen.getByRole('button', { name: /recevoir mon code/i })).toBeDisabled())
  })
})

describe('registration wizard validation', () => {
  function renderRegister() {
    return render(
      <MemoryRouter>
        <Register />
      </MemoryRouter>,
    )
  }

  it('requires full name and e-mail on step 1', () => {
    renderRegister()
    expect(screen.getByLabelText(/nom complet/i)).toBeRequired()
    expect(screen.getByLabelText(/adresse e-mail/i)).toBeRequired()
    expect(screen.getByText(/étape 1 sur 3/i)).toBeInTheDocument()
  })

  it('advances through all three steps and reaches the final step', async () => {
    const user = userEvent.setup()
    renderRegister()

    await user.type(screen.getByLabelText(/nom complet/i), 'Yasmine Ben Salah')
    await user.type(screen.getByLabelText(/adresse e-mail/i), 'yasmine@exemple.tn')
    await user.click(screen.getByRole('button', { name: /tunis/i }))
    await user.click(screen.getByRole('button', { name: /continuer/i }))

    expect(await screen.findByText(/où en es-tu aujourd'hui/i)).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: /continuer/i }))
    expect(await screen.findByText(/étape 3 sur 3/i)).toBeInTheDocument()
  })

  it('lets the applicant pick a campus and reflects the selection', async () => {
    const user = userEvent.setup()
    renderRegister()
    const sfax = screen.getByRole('button', { name: 'Sfax' })
    await user.click(sfax)
    // Selected campus gets the active border class
    expect(sfax.className).toMatch(/border-brand-500/)
  })
})
