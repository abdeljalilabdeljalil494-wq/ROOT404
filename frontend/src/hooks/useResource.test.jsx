import { it, expect, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import useResource from './useResource'

it('does not overlap slow polls and stops after unmount', async () => {
  vi.useFakeTimers()
  let resolve
  const loader = vi.fn(() => new Promise(done => { resolve = done }))
  const { result, unmount } = renderHook(() => useResource(loader, 5000))
  await act(async () => {})
  await act(async () => { vi.advanceTimersByTime(15000) })
  expect(loader).toHaveBeenCalledTimes(1)
  await act(async () => { resolve(['measured']) })
  expect(result.current.data).toEqual(['measured'])
  await act(async () => { vi.advanceTimersByTime(5000) })
  expect(loader).toHaveBeenCalledTimes(2)
  unmount()
  await act(async () => { resolve([]); vi.advanceTimersByTime(15000) })
  expect(loader).toHaveBeenCalledTimes(2)
  vi.useRealTimers()
})
