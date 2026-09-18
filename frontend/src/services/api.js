import axios from 'axios'
import * as mock from '../data/mock'

/**
 * Security utilities for frontend
 */
const SECURITY = {
  MAX_FILE_SIZE: 1024 * 1024, // 1MB
  MAX_FILES: 20,
  MAX_TOTAL_SIZE: 5 * 1024 * 1024, // 5MB
  ALLOWED_LANGUAGES: ['c', 'cpp', 'c++', 'python', 'py', 'javascript', 'js'],
  MAX_INPUT_LENGTH: 10000,
}

function sanitizeInput(input, maxLength = SECURITY.MAX_INPUT_LENGTH) {
  if (typeof input !== 'string') return input
  // Remove null bytes
  let sanitized = input.replace(/\x00/g, '')
  // Truncate
  if (sanitized.length > maxLength) {
    sanitized = sanitized.slice(0, maxLength)
  }
  return sanitized
}

function validateFileName(filename) {
  if (!filename || typeof filename !== 'string') {
    throw new Error('Invalid filename')
  }
  if (filename.length > 100) {
    throw new Error('Filename too long')
  }
  if (filename.includes('..') || filename.startsWith('/') || filename.includes('\\') || filename.includes('\x00')) {
    throw new Error('Invalid filename: path traversal detected')
  }
  return true
}

function validateFiles(files) {
  if (!files || typeof files !== 'object') {
    throw new Error('Files must be an object')
  }
  const fileCount = Object.keys(files).length
  if (fileCount === 0) {
    throw new Error('At least one file required')
  }
  if (fileCount > SECURITY.MAX_FILES) {
    throw new Error(`Too many files, max ${SECURITY.MAX_FILES}`)
  }
  
  let totalSize = 0
  for (const [fname, content] of Object.entries(files)) {
    validateFileName(fname)
    if (typeof content !== 'string') {
      throw new Error(`Invalid content for ${fname}`)
    }
    const size = new Blob([content]).size
    if (size > SECURITY.MAX_FILE_SIZE) {
      throw new Error(`File ${fname} too large: ${size} bytes`)
    }
    totalSize += size
  }
  
  if (totalSize > SECURITY.MAX_TOTAL_SIZE) {
    throw new Error(`Total size too large: ${totalSize} bytes`)
  }
  
  return true
}

function validateLanguage(lang) {
  if (!SECURITY.ALLOWED_LANGUAGES.includes(lang.toLowerCase())) {
    throw new Error(`Language ${lang} not supported`)
  }
  return lang.toLowerCase()
}

/**
 * Axios instance pointed at the FastAPI backend.
 * In dev, Vite proxies `/api` → http://localhost:8000 (see vite.config.js).
 */
export const http = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 15000,
  headers: { 
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest', // CSRF protection
  },
  // Security: prevent sending credentials to wrong origin
  withCredentials: false,
})

// Request interceptor with security checks
http.interceptors.request.use((config) => {
  // Token validation
  const token = localStorage.getItem('root404_token')
  if (token) {
    // Basic JWT format validation
    if (token.split('.').length !== 3) {
      console.warn('[Security] Invalid token format, clearing')
      localStorage.removeItem('root404_token')
    } else {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  
  // Sanitize request data
  if (config.data) {
    if (config.data.message) {
      config.data.message = sanitizeInput(config.data.message, 5000)
    }
    if (config.data.code) {
      config.data.code = sanitizeInput(config.data.code, 100000)
    }
  }
  
  // Add request ID for tracing
  config.headers['X-Request-ID'] = `fe_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`
  
  return config
}, (error) => {
  console.error('[API] Request interceptor error:', error)
  return Promise.reject(error)
})

// Response interceptor with error handling
http.interceptors.response.use(
  (response) => {
    // Check for security headers
    if (import.meta.env.DEV) {
      const securityHeaders = ['x-content-type-options', 'x-frame-options', 'x-xss-protection']
      const missing = securityHeaders.filter(h => !response.headers[h])
      if (missing.length > 0) {
        console.warn(`[Security] Missing security headers: ${missing.join(', ')}`)
      }
    }
    return response
  },
  (error) => {
    // Handle 401 - token expired or invalid
    if (error.response?.status === 401) {
      console.warn('[Auth] Unauthorized, clearing token')
      localStorage.removeItem('root404_token')
      // Don't redirect if already on login page
      if (!window.location.pathname.includes('/login')) {
        // Could trigger logout event
        window.dispatchEvent(new CustomEvent('auth:logout', { detail: { reason: 'unauthorized' } }))
      }
    }
    
    // Handle 429 - rate limited
    if (error.response?.status === 429) {
      const retryAfter = error.response.headers['retry-after'] || error.response.data?.retry_after || 60
      console.warn(`[RateLimit] Rate limited, retry after ${retryAfter}s`)
      // Could show user notification
      window.dispatchEvent(new CustomEvent('api:rate-limited', { detail: { retryAfter } }))
    }
    
    // Handle 413 - payload too large
    if (error.response?.status === 413) {
      console.error('[API] Payload too large')
      error.message = 'Fichier trop volumineux'
    }
    
    // Handle network errors
    if (!error.response) {
      console.error('[API] Network error:', error.message)
      error.message = 'Erreur réseau - vérifiez votre connexion'
    }
    
    // Log errors in dev
    if (import.meta.env.DEV) {
      console.error(`[API] ${error.config?.method?.toUpperCase()} ${error.config?.url} failed:`, error.response?.data || error.message)
    }
    
    return Promise.reject(error)
  }
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
  requestOtp: (email) => {
    email = sanitizeInput(email, 254)
    if (!email || !email.includes('@')) {
      throw new Error('Invalid email')
    }
    return resolve({ sent: true, email, dev_otp: '123456' }, () => http.post('/auth/otp', { email }))
  },
  verifyOtp: (email, code) => {
    email = sanitizeInput(email, 254)
    code = sanitizeInput(code, 6)
    if (!/^\d{6}$/.test(code)) {
      throw new Error('Invalid OTP format')
    }
    return resolve({ access_token: 'mock.jwt.token', token: 'mock.jwt.token', user: mock.currentUser }, () =>
      http.post('/auth/verify', { email, code }),
    )
  },
  register: (payload) => {
    // Validate payload
    if (!payload.username || payload.username.length < 3 || payload.username.length > 30) {
      throw new Error('Invalid username')
    }
    if (!payload.email || !payload.email.includes('@')) {
      throw new Error('Invalid email')
    }
    if (!payload.display_name || payload.display_name.length < 2) {
      throw new Error('Invalid display name')
    }
    payload.username = sanitizeInput(payload.username, 30).toLowerCase()
    payload.email = sanitizeInput(payload.email, 254).toLowerCase()
    payload.display_name = sanitizeInput(payload.display_name, 50)
    if (payload.full_name) {
      payload.full_name = sanitizeInput(payload.full_name, 100)
    }
    return resolve({ user: mock.currentUser, dev_otp: '123456' }, () => http.post('/auth/register', payload))
  },
  logout: () => {
    localStorage.removeItem('root404_token')
    localStorage.removeItem('root404_user')
    return Promise.resolve(true)
  },
}

/* -------------------------------- Projects ------------------------------- */
export const projectService = {
  list: (filters = {}) => {
    // Sanitize filters
    const sanitized = {}
    if (filters.status) sanitized.status = sanitizeInput(filters.status, 20)
    if (filters.lang) sanitized.lang = sanitizeInput(filters.lang, 20)
    if (filters.q) sanitized.q = sanitizeInput(filters.q, 100)
    const params = new URLSearchParams(sanitized).toString()
    return resolve(mock.projects, () => http.get(`/projects/${params ? `?${params}` : ''}`))
  },
  bySlug: (slug) => {
    slug = sanitizeInput(slug, 100)
    if (!/^[a-zA-Z0-9_-]+$/.test(slug)) {
      throw new Error('Invalid project slug')
    }
    return resolve(
      mock.projects.find((p) => p.slug === slug) || null,
      () => http.get(`/projects/${slug}`),
    )
  },
  submit: (slug, files, language = 'c') => {
    slug = sanitizeInput(slug, 100)
    validateFiles(files)
    language = validateLanguage(language)
    return resolve({ ok: true, score: 92 }, () => http.post(`/projects/${slug}/submit`, { files, language }))
  },
  submissions: (slug) => {
    slug = sanitizeInput(slug, 100)
    return resolve([], () => http.get(`/projects/${slug}/submissions`))
  },
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
    const sanitized = {}
    if (params.limit) sanitized.limit = Math.min(parseInt(params.limit) || 50, 100)
    if (params.campus) sanitized.campus = sanitizeInput(params.campus, 50)
    const qs = new URLSearchParams(sanitized).toString()
    return resolve(mock.leaderboard, () => http.get(`/leaderboard/${qs ? `?${qs}` : ''}`))
  },
  coalitions: () => resolve(mock.coalitions, () => http.get('/leaderboard/coalitions')),
  campus: () => resolve([], () => http.get('/leaderboard/campus')),
  arena: () => resolve([], () => http.get('/leaderboard/arena')),
}

/* ---------------------------------- Rooms -------------------------------- */
export const roomService = {
  list: (type) => {
    const allowed = ['study', 'correction', 'pair', 'competition', 'mentor', 'live']
    if (type && !allowed.includes(type)) {
      throw new Error('Invalid room type')
    }
    return resolve(mock.rooms, () => http.get(`/rooms/${type ? `?type=${type}` : ''}`))
  },
  get: (id) => {
    id = sanitizeInput(id, 32)
    return resolve({ id, name: 'Room', members: [], messages: mock.chatMessages }, () => http.get(`/rooms/${id}`))
  },
  create: (payload) => {
    if (!payload.name || payload.name.length === 0 || payload.name.length > 100) {
      throw new Error('Invalid room name')
    }
    const allowedTypes = ['study', 'correction', 'pair', 'competition', 'mentor', 'live']
    if (payload.type && !allowedTypes.includes(payload.type)) {
      throw new Error('Invalid room type')
    }
    if (payload.capacity && (payload.capacity <= 0 || payload.capacity > 1000)) {
      throw new Error('Invalid capacity')
    }
    payload.name = sanitizeInput(payload.name, 100)
    return resolve({ ok: true, id: 'r_new' }, () => http.post('/rooms/', payload))
  },
  messages: (id) => {
    id = sanitizeInput(id, 32)
    return resolve(mock.chatMessages, () => http.get(`/rooms/${id}/messages`))
  },
  sendMessage: (id, content) => {
    id = sanitizeInput(id, 32)
    content = sanitizeInput(content, 2000)
    if (!content || content.trim().length === 0) {
      throw new Error('Message cannot be empty')
    }
    return resolve({ ok: true }, () => http.post(`/rooms/${id}/messages`, { content }))
  },
  join: (id) => {
    id = sanitizeInput(id, 32)
    return resolve({ ok: true }, () => http.post(`/rooms/${id}/join`))
  },
  leave: (id) => {
    id = sanitizeInput(id, 32)
    return resolve({ ok: true }, () => http.post(`/rooms/${id}/leave`))
  },
  members: (id) => {
    id = sanitizeInput(id, 32)
    return resolve(mock.roomMembers, () => http.get(`/rooms/${id}/members`))
  },
}

/* ---------------------------------- Judge -------------------------------- */
export const judgeService = {
  run: (payload) => {
    if (!payload.code || typeof payload.code !== 'string') {
      throw new Error('Code required')
    }
    if (payload.code.length > 100000) {
      throw new Error('Code too large')
    }
    if (payload.language) {
      validateLanguage(payload.language)
    }
    return resolve({ lines: mock.terminalLines }, () => http.post('/judge/run', payload))
  },
  moulinette: (slug, files, language = 'c') => {
    slug = sanitizeInput(slug, 100)
    validateFiles(files)
    language = validateLanguage(language)
    return resolve({ tests: mock.moulinetteTests, score: 98, passed: 5, total: 7 }, () => http.post(`/judge/moulinette/${slug}`, { project_slug: slug, files, language }))
  },
  review: (code, language = 'c') => {
    if (!code || code.length > 100000) {
      throw new Error('Invalid code')
    }
    language = validateLanguage(language)
    return resolve(mock.aiCodeReview, () => http.post('/judge/review', { code, language }))
  },
  runners: () => resolve({ runners: [] }, () => http.get('/judge/runners')),
}

/* ------------------------------- AI Mentor ------------------------------- */
export const aiService = {
  history: () => resolve(mock.aiConversation, () => http.get('/ai/history')),
  ask: (message, level = 2, project_slug = null, code = null) => {
    message = sanitizeInput(message, 5000)
    if (!message || message.trim().length === 0) {
      throw new Error('Message cannot be empty')
    }
    if (level < 1 || level > 5) {
      throw new Error('Invalid level')
    }
    const payload = { message, level }
    if (project_slug) payload.project_slug = sanitizeInput(project_slug, 100)
    if (code) payload.code = sanitizeInput(code, 100000)
    return resolve(
      {
        role: 'ai',
        text: "Bonne question. Avant de te répondre, reformule-moi le problème avec tes propres mots — qu'attends-tu exactement en sortie ?",
      },
      () => http.post('/ai/ask', payload),
    )
  },
  review: (code) => {
    if (!code || code.length > 100000) {
      throw new Error('Invalid code')
    }
    return resolve(mock.aiCodeReview, () => http.post('/ai/review', { code }))
  },
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
  list: (role = 'all') => {
    const allowed = ['all', 'corrector', 'author', 'pending']
    if (!allowed.includes(role)) role = 'all'
    return resolve({ as_corrector: [], as_author: [], pending: 0 }, () => http.get(`/peer-review/?role=${role}`))
  },
  request: (submission_id) => {
    submission_id = sanitizeInput(submission_id, 32)
    return resolve({ ok: true }, () => http.post('/peer-review/request', { submission_id }))
  },
  get: (id) => {
    id = sanitizeInput(id, 32)
    return resolve({}, () => http.get(`/peer-review/${id}`))
  },
  review: (id, payload) => {
    id = sanitizeInput(id, 32)
    if (payload.comment) {
      payload.comment = sanitizeInput(payload.comment, 5000)
    }
    return resolve({ ok: true }, () => http.post(`/peer-review/${id}/review`, payload))
  },
  slots: () => resolve([], () => http.get('/peer-review/slots/available')),
  createSlot: (payload) => resolve({ ok: true }, () => http.post('/peer-review/slots', payload)),
  bookSlot: (id) => {
    id = sanitizeInput(id, 32)
    return resolve({ ok: true }, () => http.post(`/peer-review/slots/${id}/book`))
  },
}

/* ------------------------------- Coalitions ----------------------------- */
export const coalitionService = {
  list: () => resolve(mock.coalitions, () => http.get('/coalitions/')),
  join: (coalition_id) => {
    coalition_id = sanitizeInput(coalition_id, 32)
    return resolve({ ok: true }, () => http.post('/coalitions/join', { coalition_id }))
  },
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
  createMatch: (payload) => {
    if (payload.mode) {
      const allowed = ['1v1', '2v2', 'battle_royale', 'ctf']
      if (!allowed.includes(payload.mode)) {
        throw new Error('Invalid arena mode')
      }
    }
    return resolve({ ok: true, id: 'match_1' }, () => http.post('/arena/match', payload))
  },
  joinMatch: (id) => {
    id = sanitizeInput(id, 32)
    return resolve({ ok: true }, () => http.post(`/arena/match/${id}/join`))
  },
  leaderboard: () => resolve(mock.leaderboard, () => http.get('/arena/leaderboard')),
}

/* ------------------------------- Portfolio ----------------------------- */
export const portfolioService = {
  get: (username) => {
    username = sanitizeInput(username, 30)
    if (!/^[a-zA-Z0-9_-]+$/.test(username)) {
      throw new Error('Invalid username')
    }
    return resolve({}, () => http.get(`/portfolio/${username}`))
  },
  me: () => resolve({}, () => http.get('/portfolio/me/portfolio')),
  widget: (username) => {
    username = sanitizeInput(username, 30)
    return resolve({}, () => http.get(`/portfolio/public/${username}/widget`))
  },
}

/* ------------------------------- Hiring ----------------------------- */
export const hiringService = {
  companies: () => resolve([], () => http.get('/hiring/companies')),
  challenges: () => resolve([], () => http.get('/hiring/challenges')),
  apply: (challenge_id, payload) => {
    challenge_id = sanitizeInput(challenge_id, 32)
    return resolve({ ok: true }, () => http.post(`/hiring/challenges/${challenge_id}/apply`, payload))
  },
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
  mentors: (skill) => {
    if (skill) skill = sanitizeInput(skill, 50)
    return resolve([], () => http.get(`/mentorship/mentors${skill ? `?skill=${skill}` : ''}`))
  },
  request: (payload) => {
    if (payload.message) {
      payload.message = sanitizeInput(payload.message, 2000)
    }
    return resolve({ ok: true }, () => http.post('/mentorship/request', payload))
  },
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
  SECURITY, // Export for testing
}
