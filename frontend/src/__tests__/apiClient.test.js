import axios from 'axios'
import { afterEach, describe, expect, it } from 'vitest'

import { http } from '../services/api'

/**
 * Fake axios adapter. Axios custom adapters own status handling: they must
 * reject with an AxiosError for non-2xx statuses (exactly what the real
 * xhr/http adapters do), which keeps the instance's real interceptors in the
 * code path under test.
 */
function respondWith(status, body = {}) {
  return async function adapter(config) {
    const response = {
      data: body,
      status,
      statusText: String(status),
      headers: {},
      config,
    }
    if (status >= 400) {
      throw new axios.AxiosError(`HTTP ${status}`, String(status), config, {}, response)
    }
    return response
  }
}

describe('API client (axios instance)', () => {
  afterEach(() => {
    localStorage.clear()
  })

  it('attaches the stored JWT as a Bearer header', async () => {
    localStorage.setItem('root404_token', 'abc.def.ghi')
    let seenAuth = null
    await http({
      url: '/anything',
      adapter: async (config) => {
        seenAuth = config.headers?.Authorization
        return { data: {}, status: 200, statusText: 'OK', headers: {}, config }
      },
    })
    expect(seenAuth).toBe('Bearer abc.def.ghi')
  })

  it('does not attach an Authorization header when logged out', async () => {
    let seenAuth
    await http({
      url: '/anything',
      adapter: async (config) => {
        seenAuth = config.headers?.Authorization
        return { data: {}, status: 200, statusText: 'OK', headers: {}, config }
      },
    })
    expect(seenAuth).toBeUndefined()
  })

  it('clears the stored token when the API answers 401 (logout-on-expiry)', async () => {
    localStorage.setItem('root404_token', 'expired.token')
    await expect(
      http({ url: '/secure', adapter: respondWith(401, { detail: 'Not authenticated' }) }),
    ).rejects.toMatchObject({ response: { status: 401 } })
    expect(localStorage.getItem('root404_token')).toBeNull()
  })

  it('propagates API error states to callers and keeps the token for non-401 errors', async () => {
    localStorage.setItem('root404_token', 'still.valid')
    await expect(
      http({ url: '/boom', adapter: respondWith(500, { detail: 'boom' }) }),
    ).rejects.toMatchObject({ response: { status: 500 } })
    expect(localStorage.getItem('root404_token')).toBe('still.valid')
  })

  it('uses the /api base URL with a sane timeout', () => {
    expect(typeof http.get).toBe('function')
    expect(http.defaults.baseURL).toBe('/api')
    expect(http.defaults.timeout).toBe(15000)
  })
})
