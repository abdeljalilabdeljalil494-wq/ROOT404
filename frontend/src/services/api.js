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
  try {
    const { data } = await request()
    return data
  } catch (e) {
    // Fallback to mock on network error in dev
    if (import.meta.env.DEV) {
      console.warn('[API] Falling back to mock due to error:', e.message)
      await delay()
      return mockValue
    }
    throw e
  }
}

/* ---------------------------------- Auth --------------------------------- */
export const authService = {
  me: () => resolve(mock.currentUser, () => http.get('/auth/me/full').then(r => r.data).catch(() => http.get('/auth/me').then(r => r.data))),
  meSimple: () => resolve(mock.currentUser, () => http.get('/auth/me')),
  requestOtp: (email) => resolve({ sent: true, email, dev_otp: '123456' }, () => http.post('/auth/otp', { email })),
  verifyOtp: (email, code) =>
    resolve({ access_token: 'mock.jwt.token', token: 'mock.jwt.token', user: mock.currentUser }, () =>
      http.post('/auth/verify', { email, code }),
    ),
  register: (payload) => resolve({ user: mock.currentUser, dev_otp: '123456' }, () => http.post('/auth/register', payload)),
  logout: () => {
    localStorage.removeItem('root404_token')
    return Promise.resolve(true)
  },
}

/* -------------------------------- Projects ------------------------------- */
export const projectService = {
  list: (filters = {}) => {
    const params = new URLSearchParams(filters).toString()
    return resolve(mock.projects, () => http.get(`/projects/${params ? `?${params}` : ''}`))
  },
  bySlug: (slug) =>
    resolve(
      mock.projects.find((p) => p.slug === slug) || null,
      () => http.get(`/projects/${slug}`),
    ),
  submit: (slug, files, language = 'c') => resolve({ ok: true, score: 92 }, () => http.post(`/projects/${slug}/submit`, { files, language })),
  submissions: (slug) => resolve([], () => http.get(`/projects/${slug}/submissions`)),
  seed: () => http.post('/projects/seed'),
}

/* -------------------------------- Dashboard ------------------------------ */
export const dashboardService = {
  stats: () => resolve(mock.dashboardStats, () => http.get('/dashboard/stats')),
  activity: () => resolve(mock.recentActivity, () => http.get('/dashboard/activity')),
  weekly: () => resolve(mock.weeklyActivity, () => http.get('/dashboard/weekly')),
  overview: () => resolve({
    user: mock.currentUser,
    level: mock.currentUser.level,
    levelProgress: 42,
    xpToNext: mock.currentUser.xpToNext,
    stats: mock.dashboardStats,
    recentActivity: mock.recentActivity,
    weeklyActivity: mock.weeklyActivity,
    dailyMission: mock.dailyMission,
    blackHole: { daysLeft: 87, total: 120 }
  }, () => http.get('/dashboard/overview')),
  heatmap: () => resolve(mock.heatmap, () => http.get('/dashboard/heatmap')),
}

/* ------------------------------- Leaderboard ----------------------------- */
export const leaderboardService = {
  global: (params = {}) => {
    const qs = new URLSearchParams(params).toString()
    return resolve(mock.leaderboard, () => http.get(`/leaderboard/${qs ? `?${qs}` : ''}`))
  },
  coalitions: () => resolve(mock.coalitions, () => http.get('/leaderboard/coalitions')),
  campus: () => resolve([], () => http.get('/leaderboard/campus')),
  arena: () => resolve([], () => http.get('/leaderboard/arena')),
}

/* ---------------------------------- Rooms -------------------------------- */
export const roomService = {
  list: (type) => resolve(mock.rooms, () => http.get(`/rooms/${type ? `?type=${type}` : ''}`)),
  get: (id) => resolve({ id, name: 'Room', members: [], messages: mock.chatMessages }, () => http.get(`/rooms/${id}`)),
  create: (payload) => resolve({ ok: true, id: 'r_new' }, () => http.post('/rooms/', payload)),
  messages: (id) => resolve(mock.chatMessages, () => http.get(`/rooms/${id}/messages`)),
  sendMessage: (id, content) => resolve({ ok: true }, () => http.post(`/rooms/${id}/messages`, { content })),
  join: (id) => resolve({ ok: true }, () => http.post(`/rooms/${id}/join`)),
  leave: (id) => resolve({ ok: true }, () => http.post(`/rooms/${id}/leave`)),
  members: (id) => resolve(mock.roomMembers, () => http.get(`/rooms/${id}/members`)),
}

/* ---------------------------------- Judge -------------------------------- */
export const judgeService = {
  run: (payload) => resolve({ lines: mock.terminalLines }, () => http.post('/judge/run', payload)),
  moulinette: (slug, files, language = 'c') =>
    resolve({ tests: mock.moulinetteTests, score: 98, passed: 5, total: 7 }, () => http.post(`/judge/moulinette/${slug}`, { project_slug: slug, files, language })),
  review: (code, language = 'c') => resolve(mock.aiCodeReview, () => http.post('/judge/review', { code, language })),
  runners: () => resolve({ runners: [] }, () => http.get('/judge/runners')),
}

/* ------------------------------- AI Mentor ------------------------------- */
export const aiService = {
  history: () => resolve(mock.aiConversation, () => http.get('/ai/history')),
  ask: (message, level = 2, project_slug = null, code = null) =>
    resolve(
      {
        role: 'ai',
        text: "Bonne question. Avant de te répondre, reformule-moi le problème avec tes propres mots — qu'attends-tu exactement en sortie ?",
      },
      () => http.post('/ai/ask', { message, level, project_slug, code }),
    ),
  review: (code) => resolve(mock.aiCodeReview, () => http.post('/ai/review', { code })),
  levels: () => resolve(mock.aiLevels || [], () => http.get('/ai/levels')),
  gaps: () => resolve({ gaps: [], challenges: [] }, () => http.get('/ai/gaps')),
}

/* ------------------------------- Analytics ------------------------------- */
export const analyticsService = {
  overview: () => resolve(mock.analytics, () => http.get('/analytics/overview')),
  skills: () => resolve(mock.skillGraph, () => http.get('/analytics/skills')),
  journey: () => resolve(mock.journeyStages, () => http.get('/analytics/journey')),
  heatmap: () => resolve(mock.heatmap, () => http.get('/analytics/heatmap')),
  reputation: () => resolve(mock.reputation, () => http.get('/analytics/reputation')),
  integrity: () => resolve(mock.integrityScore, () => http.get('/analytics/integrity')),
  blackhole: () => resolve({ daysLeft: 87, total: 120 }, () => http.get('/analytics/blackhole')),
  velocity: () => resolve({ velocity: 78 }, () => http.get('/analytics/velocity')),
}

/* ------------------------------- Peer Review ----------------------------- */
export const peerReviewService = {
  list: (role = 'all') => resolve({ as_corrector: [], as_author: [], pending: 0 }, () => http.get(`/peer-review/?role=${role}`)),
  request: (submission_id) => resolve({ ok: true }, () => http.post('/peer-review/request', { submission_id })),
  get: (id) => resolve({}, () => http.get(`/peer-review/${id}`)),
  review: (id, payload) => resolve({ ok: true }, () => http.post(`/peer-review/${id}/review`, payload)),
  slots: () => resolve([], () => http.get('/peer-review/slots/available')),
  createSlot: (payload) => resolve({ ok: true }, () => http.post('/peer-review/slots', payload)),
  bookSlot: (id) => resolve({ ok: true }, () => http.post(`/peer-review/slots/${id}/book`)),
}

/* ------------------------------- Coalitions ----------------------------- */
export const coalitionService = {
  list: () => resolve(mock.coalitions, () => http.get('/coalitions/')),
  join: (coalition_id) => resolve({ ok: true }, () => http.post('/coalitions/join', { coalition_id })),
  wars: () => resolve([], () => http.get('/coalitions/wars')),
  me: () => resolve({ name: 'The Phoenix', color: '#F8851F' }, () => http.get('/coalitions/me')),
}

/* ------------------------------- Piscine ----------------------------- */
export const piscineService = {
  days: () => resolve(mock.piscineDays, () => http.get('/piscine/days')),
  stats: () => resolve(mock.piscineStats, () => http.get('/piscine/stats')),
}

/* ------------------------------- Arena ----------------------------- */
export const arenaService = {
  modes: () => resolve(mock.arenaModes, () => http.get('/arena/modes')),
  live: () => resolve(mock.arenaLive, () => http.get('/arena/live')),
  createMatch: (payload) => resolve({ ok: true, id: 'match_1' }, () => http.post('/arena/match', payload)),
  joinMatch: (id) => resolve({ ok: true }, () => http.post(`/arena/match/${id}/join`)),
  leaderboard: () => resolve(mock.leaderboard, () => http.get('/arena/leaderboard')),
}

/* ------------------------------- Portfolio ----------------------------- */
export const portfolioService = {
  get: (username) => resolve({}, () => http.get(`/portfolio/${username}`)),
  me: () => resolve({}, () => http.get('/portfolio/me/portfolio')),
  widget: (username) => resolve({}, () => http.get(`/portfolio/public/${username}/widget`)),
}

/* ------------------------------- Hiring ----------------------------- */
export const hiringService = {
  companies: () => resolve([], () => http.get('/hiring/companies')),
  challenges: () => resolve([], () => http.get('/hiring/challenges')),
  apply: (challenge_id, payload) => resolve({ ok: true }, () => http.post(`/hiring/challenges/${challenge_id}/apply`, payload)),
  fair: () => resolve({}, () => http.get('/hiring/fair')),
}

/* ------------------------------- Exam ----------------------------- */
export const examService = {
  tracks: () => resolve([], () => http.get('/exam/tracks')),
  start: (payload) => resolve({ exam_id: 'exam_123' }, () => http.post('/exam/start', payload)),
  submit: (payload) => resolve({ ok: true, score: 85 }, () => http.post('/exam/submit', payload)),
  history: () => resolve([], () => http.get('/exam/history')),
  gates: () => resolve([], () => http.get('/exam/gates')),
}

/* ------------------------------- Mentorship ----------------------------- */
export const mentorshipService = {
  mentors: (skill) => resolve([], () => http.get(`/mentorship/mentors${skill ? `?skill=${skill}` : ''}`)),
  request: (payload) => resolve({ ok: true }, () => http.post('/mentorship/request', payload)),
  schedule: (payload) => resolve({ ok: true }, () => http.post('/mentorship/schedule', payload)),
  sessions: () => resolve({ as_mentor: [], as_student: [] }, () => http.get('/mentorship/sessions')),
  becomeMentor: () => resolve({ ok: true }, () => http.post('/mentorship/become-mentor')),
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
  peerReviewService,
  coalitionService,
  piscineService,
  arenaService,
  portfolioService,
  hiringService,
  examService,
  mentorshipService,
  http,
}
