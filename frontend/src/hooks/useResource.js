import { useEffect, useState } from 'react'

/** Explicit failure/retry, cancellation guard and optional non-overlapping polling. */
export default function useResource(loader, refreshMs = 0) {
  const [state, setState] = useState({ data: null, loading: true, error: null })
  const [attempt, setAttempt] = useState(0)
  useEffect(() => {
    let active = true
    let timer
    const poll = () => {
      if (!active) return
      if (document.visibilityState === 'hidden') { timer = setTimeout(poll, refreshMs); return }
      load()
    }
    const load = () => {
      setState(previous => ({ ...previous, loading: previous.data === null, error: null }))
      Promise.resolve().then(loader).then(data => {
        if (active) setState({ data, loading: false, error: null })
      }).catch(error => {
        if (active) setState({ data: null, loading: false, error })
      }).finally(() => {
        if (active && refreshMs) timer = setTimeout(poll, refreshMs)
      })
    }
    load()
    return () => { active = false; clearTimeout(timer) }
  }, [loader, attempt, refreshMs])
  return { ...state, retry: () => setAttempt(n => n + 1) }
}
