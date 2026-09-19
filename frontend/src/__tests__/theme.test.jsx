import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'

import { ThemeProvider, useTheme } from '../hooks/useTheme'
import ThemeToggle from '../components/ui/ThemeToggle'

function ThemeProbe() {
  const { theme } = useTheme()
  return <span data-testid="current">{theme}</span>
}

describe('theme provider', () => {
  it('defaults to dark, persists the choice, and toggles correctly', async () => {
    const user = userEvent.setup()
    render(
      <ThemeProvider>
        <ThemeProbe />
        <ThemeToggle />
      </ThemeProvider>,
    )

    expect(screen.getByTestId('current')).toHaveTextContent('dark')
    expect(document.documentElement.classList.contains('dark')).toBe(true)
    expect(localStorage.getItem('root404_theme')).toBe('dark')

    await user.click(screen.getByRole('button', { name: /activer le thème clair/i }))

    expect(screen.getByTestId('current')).toHaveTextContent('light')
    expect(document.documentElement.classList.contains('dark')).toBe(false)
    expect(localStorage.getItem('root404_theme')).toBe('light')

    // And back to dark
    await user.click(screen.getByRole('button', { name: /activer le thème sombre/i }))
    expect(screen.getByTestId('current')).toHaveTextContent('dark')
  })
})
