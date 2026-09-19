import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import useApi from '../hooks/useApi'

function Probe({ fetcher }) {
  const { data, loading, error, refetch } = useApi(fetcher)
  return (
    <div>
      <span data-testid="loading">{loading ? 'loading' : 'idle'}</span>
      {error ? <span data-testid="error">{error.message}</span> : null}
      {data ? <span data-testid="data">{data}</span> : null}
      <button onClick={refetch}>refetch</button>
    </div>
  )
}

describe('useApi', () => {
  it('starts in a loading state, then exposes resolved data', async () => {
    const fetcher = vi.fn().mockResolvedValue('hello')
    render(<Probe fetcher={fetcher} />)
    expect(screen.getByTestId('loading')).toHaveTextContent('loading')
    await waitFor(() => expect(screen.getByTestId('data')).toHaveTextContent('hello'))
    expect(screen.getByTestId('loading')).toHaveTextContent('idle')
    expect(screen.queryByTestId('error')).not.toBeInTheDocument()
  })

  it('exposes errors instead of swallowing them', async () => {
    const fetcher = vi.fn().mockRejectedValue(new Error('network down'))
    render(<Probe fetcher={fetcher} />)
    await waitFor(() => expect(screen.getByTestId('error')).toHaveTextContent('network down'))
    expect(screen.getByTestId('loading')).toHaveTextContent('idle')
    expect(screen.queryByTestId('data')).not.toBeInTheDocument()
  })

  it('refetches on demand', async () => {
    const user = userEvent.setup()
    let value = 'first'
    const fetcher = vi.fn().mockImplementation(() => Promise.resolve(value))
    render(<Probe fetcher={fetcher} />)
    await waitFor(() => expect(screen.getByTestId('data')).toHaveTextContent('first'))

    value = 'second'
    await user.click(screen.getByRole('button', { name: /refetch/i }))
    await waitFor(() => expect(screen.getByTestId('data')).toHaveTextContent('second'))
    expect(fetcher).toHaveBeenCalledTimes(2)
  })
})
