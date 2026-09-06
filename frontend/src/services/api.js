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

/**
 * While the backend is not wired up, every endpoint resolves from `data/mock.js`.
 * Flip VITE_USE_MOCK=false once FastAPI is running to hit the real API.
 */
const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false'

const delay = (ms = 220) => new Promise((r) => setTimeout(r, ms))

async function resolve(mockValue, request) {
  if (USE_MOCK) {
    await delay()
    return mockValue
  }
  const { data } = await request()
  return data
}

/* ---------------------------------- Auth --------------------------------- */
export const authService = {
  me: () => resolve(mock.currentUser, () => http.get('/auth/me')),
  requestOtp: (email) => resolve({ sent: true, email }, () => http.post('/auth/otp', { email })),
  verifyOtp: (email, code) =>
    resolve({ token: 'mock.jwt.token', user: mock.currentUser }, () =>
      http.post('/auth/verify', { email, code }),
    ),
  logout: () => {
    localStorage.removeItem('root404_token')
    return Promise.resolve(true)
  },
}

/* -------------------------------- Projects ------------------------------- */
export const projectService = {
  list: () => resolve(mock.projects, () => http.get('/projects')),
  bySlug: (slug) =>
    resolve(
      mock.projects.find((p) => p.slug === slug) || null,
      () => http.get(`/projects/${slug}`),
    ),
  submit: (slug, files) => resolve({ ok: true }, () => http.post(`/projects/${slug}/submit`, { files })),
}

/* -------------------------------- Dashboard ------------------------------ */
export const dashboardService = {
  stats: () => resolve(mock.dashboardStats, () => http.get('/dashboard/stats')),
  activity: () => resolve(mock.recentActivity, () => http.get('/dashboard/activity')),
  weekly: () => resolve(mock.weeklyActivity, () => http.get('/dashboard/weekly')),
}

/* ------------------------------- Leaderboard ----------------------------- */
export const leaderboardService = {
  global: () => resolve(mock.leaderboard, () => http.get('/leaderboard')),
  coalitions: () => resolve(mock.coalitions, () => http.get('/leaderboard/coalitions')),
}

/* ---------------------------------- Rooms -------------------------------- */
export const roomService = {
  list: () => resolve(mock.rooms, () => http.get('/rooms')),
  messages: (id) => resolve(mock.chatMessages, () => http.get(`/rooms/${id}/messages`)),
  join: (id) => resolve({ ok: true }, () => http.post(`/rooms/${id}/join`)),
}

/* ---------------------------------- Judge -------------------------------- */
export const judgeService = {
  run: (payload) => resolve({ lines: mock.terminalLines }, () => http.post('/judge/run', payload)),
  moulinette: (slug) =>
    resolve({ tests: mock.moulinetteTests, score: 98 }, () => http.post(`/judge/moulinette/${slug}`)),
}

/* ------------------------------- AI Mentor ------------------------------- */
export const aiService = {
  history: () => resolve(mock.aiConversation, () => http.get('/ai/history')),
  ask: (message) =>
    resolve(
      {
        role: 'ai',
        text: "Bonne question. Avant de te répondre, reformule-moi le problème avec tes propres mots — qu'attends-tu exactement en sortie ?",
      },
      () => http.post('/ai/ask', { message }),
    ),
  review: () => resolve(mock.aiCodeReview, () => http.get('/ai/review')),
}

/* ------------------------------- Analytics ------------------------------- */
export const analyticsService = {
  overview: () => resolve(mock.analytics, () => http.get('/analytics/overview')),
  skills: () => resolve(mock.skillGraph, () => http.get('/analytics/skills')),
  journey: () => resolve(mock.journeyStages, () => http.get('/analytics/journey')),
  heatmap: () => resolve(mock.heatmap, () => http.get('/analytics/heatmap')),
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
