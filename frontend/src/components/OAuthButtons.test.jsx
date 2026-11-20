import { beforeEach, it, expect, vi } from 'vitest'
import { cleanup, render, screen, fireEvent } from '@testing-library/react'
import OAuthButtons from './OAuthButtons'
import { http } from '../services/api'
vi.mock('../services/api', () => ({ http: { get: vi.fn(), post: vi.fn() } }))
beforeEach(() => { cleanup(); vi.clearAllMocks() })
it('shows honest unconfigured-provider failure', async () => {
  http.get.mockRejectedValue(new Error('not configured'))
  render(<OAuthButtons />)
  fireEvent.click(screen.getByText('Continuer avec Google'))
  expect(await screen.findByRole('alert')).toHaveTextContent('Connexion externe indisponible')
  expect(http.get).toHaveBeenCalledWith('/auth/oauth/google/start')
})
it('linking uses authenticated POST and refuses arbitrary redirect host', async () => {
  http.post.mockResolvedValue({ data: { url: 'https://evil.example/steal' } })
  render(<OAuthButtons linking />)
  fireEvent.click(screen.getByText('Lier GitHub'))
  expect(await screen.findByRole('alert')).toBeVisible()
  expect(http.post).toHaveBeenCalledWith('/auth/oauth/github/link')
})
