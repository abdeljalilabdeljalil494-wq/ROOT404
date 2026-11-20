import { beforeEach, describe, expect, it } from 'vitest'
import { accountService, authService, dashboardService, http, USE_MOCK } from './api'

beforeEach(() => { localStorage.clear() })

describe('real API service contract', () => {
  it('uses real API unless development demo is explicitly selected', () => {
    expect(USE_MOCK).toBe(false)
  })
  it('unwraps the full user exactly once', async () => {
    http.defaults.adapter = async config => ({ config, status: 200, headers: {}, data: { id: 'real-user', xp: 0 } })
    expect(await authService.me()).toEqual({ id: 'real-user', xp: 0 })
  })
  it('does not replace network failures with demo statistics', async () => {
    http.defaults.adapter = async () => { throw new Error('offline') }
    await expect(dashboardService.stats()).rejects.toThrow()
  })
  it('clears an expired token and emits logout', async () => {
    localStorage.setItem('root404_token', 'a.b.c')
    let called = false
    const listener = () => { called = true }
    window.addEventListener('auth:logout', listener)
    http.defaults.adapter = async config => { throw { config, response: { status: 401, data: {}, headers: {} } } }
    await expect(authService.meSimple()).rejects.toBeDefined()
    expect(localStorage.getItem('root404_token')).toBeNull()
    expect(called).toBe(true)
    window.removeEventListener('auth:logout', listener)
  })
  it('contacts logout before deleting the bearer token', async () => {
    localStorage.setItem('root404_token', 'a.b.c')
    let authorization
    http.defaults.adapter = async config => {
      authorization = config.headers.Authorization
      expect(config.url).toBe('/auth/logout')
      return { config, status: 200, headers: {}, data: { ok: true } }
    }
    await authService.logout()
    expect(authorization).toBe('Bearer a.b.c')
    expect(localStorage.getItem('root404_token')).toBeNull()
  })
})


describe('account service wire format regression', () => {
  it('unwraps privacy payload without forwarding Axios metadata back to API', async () => {
    const preferences = { public_profile: false, directory_visible: false }
    const requests = []
    http.defaults.adapter = async config => {
      requests.push(config)
      return { config, status: 200, headers: {}, data: preferences }
    }
    const loaded = await accountService.privacy()
    expect(loaded).toEqual(preferences)
    await accountService.savePrivacy({ ...loaded, public_profile: true })
    expect(JSON.parse(requests[1].data)).toEqual({ public_profile: true, directory_visible: false })
  })
})
