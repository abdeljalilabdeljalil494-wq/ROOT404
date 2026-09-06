import axios from 'axios'
import * as mock from '../data/mock'

/**
 * Axios instance pointed at the FastAPI backend.
 * In dev, Vite proxies `/api` → http://localhost:8000 (see vite.config.js).
 */
export const http = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('root404_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

http.interceptors.response.use(
  (r) => r,
  (error) => {
    if (error.response?.status === 401) localStorage.removeItem('root404_token')
    return Promise.reject(error)
  },
)

/*
 * Per-service mock/real switching.
 *
 * `VITE_REAL_SERVICES` (comma list) names the services that hit the real
 * FastAPI backend. Everything else keeps resolving from `data/mock.js` until
 * its backend endpoints land (judge, rooms, AI, leaderboard, analytics…).
 *
 * Global overrides:
 *   VITE_USE_MOCK=true  → every service mocked (fully offline frontend)
 *   VITE_USE_MOCK=false → every service real
 *
 * When a real call fails (backend down, endpoint not built yet, 401 without a
 * session…) we warn and fall back to the mock value so the UI never breaks.
 */
const ALL_MOCK = import.meta.env.VITE_USE_MOCK === 'true'
const ALL_REAL = import.meta.env.VITE_USE_MOCK === 'false'
const REAL_SERVICES = new Set(
  (import.meta.env.VITE_REAL_SERVICES || 'auth,projects,dashboard')
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean),
)

const useMock = (service) =>
  ALL_MOCK || (ALL_REAL ? false : !REAL_SERVICES.has(service))

const delay = (ms = 220) => new Promise((r) => setTimeout(r, ms))

async function resolve(mockValue, request, service) {
  if (useMock(service)) {
    await delay()
    return mockValue
  }
  try {
    const { data } = await request()
    return data
  } catch (error) {
    if (error.response) {
      // Backend is up but rejected the call (401/404/409…) → surface the
      // real error to the UI; do NOT pretend it succeeded with mock data.
      throw error
    }
    // No response at all → backend offline / endpoint not built yet →
    // degrade to mock so the UI never breaks.
    console.warn(`[root404 api] ${service}: backend indisponible (${error.code || 'network'}) — fallback mock.`)
    return mockValue
  }
}

/* ---------------------------------- Auth --------------------------------- */
export const authService = {
  me: () => resolve(mock.currentUser, () => http.get('/auth/me'), 'auth'),
  requestOtp: (email) =>
    resolve({ sent: true, email }, () => http.post('/auth/otp', { email }), 'auth'),
  verifyOtp: (email, code) =>
    resolve(
      { token: 'mock.jwt.token', user: mock.currentUser },
      () => http.post('/auth/verify', { email, code }),
      'auth',
    ),
  register: (data) =>
    resolve(
      { token: 'mock.jwt.token', user: mock.currentUser, status: 'piscine' },
      () => http.post('/auth/register', data),
      'auth',
    ),
  logout: () => {
    localStorage.removeItem('root404_token')
    setAuthUser(null)
    return Promise.resolve(true)
  },
}

/* --------------------------- Auth user cache ------------------------------ */
/* `me` is shared by the sidebar, topbar and several pages — cache it at
   module level and dedupe concurrent fetches. */
let cachedUser = null
let inflightUser = null

export function setAuthUser(user) {
  cachedUser = user
}

export function getCachedUser() {
  return cachedUser
}

export function fetchCurrentUser(force = false) {
  if (cachedUser && !force) return Promise.resolve(cachedUser)
  if (!inflightUser) {
    inflightUser = authService
      .me()
      .then((user) => {
        cachedUser = user
        return user
      })
      .catch(() => null) // no session / bad token → caller keeps the mock user
      .finally(() => {
        inflightUser = null
      })
  }
  return inflightUser
}

/* -------------------------------- Projects ------------------------------- */
export const projectService = {
  list: () => resolve(mock.projects, () => http.get('/projects'), 'projects'),
  bySlug: (slug) =>
    resolve(
      mock.projects.find((p) => p.slug === slug) || null,
      () => http.get(`/projects/${slug}`),
      'projects',
    ),
  submit: (slug, files) =>
    resolve({ ok: true }, () => http.post(`/projects/${slug}/submit`, { files }), 'projects'),
}

/* -------------------------------- Dashboard ------------------------------ */
export const dashboardService = {
  stats: () => resolve(mock.dashboardStats, () => http.get('/dashboard/stats'), 'dashboard'),
  activity: () =>
    resolve(mock.recentActivity, () => http.get('/dashboard/activity'), 'dashboard'),
  weekly: () => resolve(mock.weeklyActivity, () => http.get('/dashboard/weekly'), 'dashboard'),
}

/* ------------------------------- Leaderboard ----------------------------- */
export const leaderboardService = {
  global: () => resolve(mock.leaderboard, () => http.get('/leaderboard'), 'leaderboard'),
  coalitions: () => resolve(mock.coalitions, () => http.get('/leaderboard/coalitions'), 'leaderboard'),
}

/* ---------------------------------- Rooms -------------------------------- */
export const roomService = {
  list: () => resolve(mock.rooms, () => http.get('/rooms'), 'rooms'),
  messages: (id) =>
    resolve(mock.chatMessages, () => http.get(`/rooms/${id}/messages`), 'rooms'),
  join: (id) => resolve({ ok: true }, () => http.post(`/rooms/${id}/join`), 'rooms'),
}

/* ---------------------------------- Judge -------------------------------- */
export const judgeService = {
  run: (payload) => resolve({ lines: mock.terminalLines }, () => http.post('/judge/run', payload), 'judge'),
  moulinette: (slug) =>
    resolve({ tests: mock.moulinetteTests, score: 98 }, () => http.post(`/judge/moulinette/${slug}`), 'judge'),
}

/* ------------------------------- AI Mentor ------------------------------- */
export const aiService = {
  history: () => resolve(mock.aiConversation, () => http.get('/ai/history'), 'ai'),
  ask: (message) =>
    resolve(
      {
        role: 'ai',
        text: "Bonne question. Avant de te répondre, reformule-moi le problème avec tes propres mots — qu'attends-tu exactement en sortie ?",
      },
      () => http.post('/ai/ask', { message }),
      'ai',
    ),
  review: () => resolve(mock.aiCodeReview, () => http.get('/ai/review'), 'ai'),
}

/* ------------------------------- Analytics ------------------------------- */
export const analyticsService = {
  overview: () => resolve(mock.analytics, () => http.get('/analytics/overview'), 'analytics'),
  skills: () => resolve(mock.skillGraph, () => http.get('/analytics/skills'), 'analytics'),
  journey: () => resolve(mock.journeyStages, () => http.get('/analytics/journey'), 'analytics'),
  heatmap: () => resolve(mock.heatmap, () => http.get('/analytics/heatmap'), 'analytics'),
}

export default {
  authService,
  projectService,
  dashboardService,
  leaderboardService,
  roomService,
  judgeService,
  aiService,
  analyticsService,
}
