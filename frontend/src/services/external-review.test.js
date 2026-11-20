import { afterEach, beforeEach, expect, it, vi } from 'vitest'
import { http, projectService } from './api'

beforeEach(() => vi.spyOn(http, 'post').mockResolvedValue({ data: { ok: true } }))
afterEach(() => vi.restoreAllMocks())

it.each(['a//b.py', 'a/./b.py', 'a/.hidden.py', 'a name.py', '-main.py', '%2e%2e/main.py', '../main.py', '/main.py', 'a\\b.py', 'a\0b.py'])(
  'rejects dispatcher-invalid filename %s before sending', (name) => {
    expect(() => projectService.submit('test', { [name]: 'print(0)' }, 'python')).toThrow(/filename/i)
  },
)
it.each(['main.py', 'src/main.py', 'a..b.py'])('accepts dispatcher-valid filename %s', async (name) => {
  const spy = http.post
  await projectService.submit('test', { [name]: 'print(0)' }, 'python')
  expect(spy).toHaveBeenCalledOnce()
})

it('renders untrusted text as inert React text rather than HTML', async () => {
  const React = await import('react')
  const { renderToStaticMarkup } = await import('react-dom/server')
  const payload = '<img src=x onerror="alert(1)"><script>alert(1)</script>'
  const result = renderToStaticMarkup(React.createElement('p', null, payload))
  expect(result).toContain('&lt;img')
  expect(result).not.toContain('<script>')
  expect(result).not.toContain('<img')
})

it('emits the server retry budget on 429 without replacing the error', async () => {
  let detail
  const listener = event => { detail = event.detail }
  window.addEventListener('api:rate-limited', listener)
  const old = http.defaults.adapter
  http.defaults.adapter = async config => { throw { config, response: { status: 429, data: {}, headers: { 'retry-after': '23' } } } }
  try {
    await expect(http.get('/health')).rejects.toBeDefined()
    expect(detail.retryAfter).toBe('23')
  } finally {
    http.defaults.adapter = old
    window.removeEventListener('api:rate-limited', listener)
  }
})
