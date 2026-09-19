import { useCallback, useEffect, useRef, useState } from 'react'

/**
 * Minimal data-fetching hook for service calls (`services/api.js`).
 *
 * Returns `{ data, loading, error, refetch }`. Errors are never swallowed —
 * callers are expected to render an error state when `error` is set.
 */
export default function useApi(fetcher, deps = []) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [tick, setTick] = useState(0)
  const fetcherRef = useRef(fetcher)
  fetcherRef.current = fetcher

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    fetcherRef
      .current()
      .then((result) => {
        if (!cancelled) {
          setData(result)
          setLoading(false)
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setData(null)
          setError(err)
          setLoading(false)
        }
      })
    return () => {
      cancelled = true
    }
    // `deps` is a caller-controlled passthrough, same contract as useEffect.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, tick])

  const refetch = useCallback(() => setTick((t) => t + 1), [])

  return { data, loading, error, refetch }
}
