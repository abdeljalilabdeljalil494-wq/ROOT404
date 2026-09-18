import { Suspense, lazy, useEffect } from 'react'
import { Route, Routes, useLocation } from 'react-router-dom'

import PublicLayout from './layouts/PublicLayout'
import AppLayout from './layouts/AppLayout'
import Home from './pages/Home'

/* Code-split every non-landing route */
const About = lazy(() => import('./pages/About'))
const Parcours = lazy(() => import('./pages/Parcours'))
const Blog = lazy(() => import('./pages/Blog'))
const Community = lazy(() => import('./pages/Community'))
const Login = lazy(() => import('./pages/auth/Login'))
const Register = lazy(() => import('./pages/auth/Register'))

const Dashboard = lazy(() => import('./pages/Dashboard'))
const Projects = lazy(() => import('./pages/Projects'))
const ProjectDetail = lazy(() => import('./pages/ProjectDetail'))
const Workspace = lazy(() => import('./pages/Workspace'))
const Rooms = lazy(() => import('./pages/Rooms'))
const RoomView = lazy(() => import('./pages/RoomView'))
const PeerReview = lazy(() => import('./pages/PeerReview'))
const Leaderboard = lazy(() => import('./pages/Leaderboard'))
const Coalitions = lazy(() => import('./pages/Coalitions'))
const Piscine = lazy(() => import('./pages/Piscine'))
const Journey = lazy(() => import('./pages/Journey'))
const SkillGraph = lazy(() => import('./pages/SkillGraph'))
const Analytics = lazy(() => import('./pages/Analytics'))
const Arena = lazy(() => import('./pages/Arena'))
const Mentor = lazy(() => import('./pages/Mentor'))
const Profile = lazy(() => import('./pages/Profile'))
const Portfolio = lazy(() => import('./pages/Portfolio'))
const Settings = lazy(() => import('./pages/Settings'))
const Hiring = lazy(() => import('./pages/Hiring'))
const Exam = lazy(() => import('./pages/Exam'))
const NotFound = lazy(() => import('./pages/NotFound'))

function ScrollToTop() {
  const { pathname } = useLocation()
  useEffect(() => {
    window.scrollTo(0, 0)
  }, [pathname])
  return null
}

function RouteFallback() {
  return (
    <div className="grid min-h-[60vh] place-items-center">
      <div className="flex flex-col items-center gap-3">
        <span className="h-8 w-8 animate-spin rounded-full border-2 border-line border-t-brand-500" />
        <span className="text-[12px] text-ink-dim">Chargement…</span>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <>
      <ScrollToTop />
      <Suspense fallback={<RouteFallback />}>
        <Routes>
          {/* Public marketing site */}
          <Route element={<PublicLayout />}>
            <Route index element={<Home />} />
            <Route path="/about" element={<About />} />
            <Route path="/parcours" element={<Parcours />} />
            <Route path="/blog" element={<Blog />} />
            <Route path="/communaute" element={<Community />} />
          </Route>

          {/* Auth (no chrome) */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Public portfolio (no chrome) */}
          <Route path="/u/:username" element={<Portfolio />} />
          <Route path="/portfolio" element={<Portfolio />} />

          {/* Full-bleed IDE (own chrome) */}
          <Route path="/workspace" element={<Workspace />} />
          <Route path="/workspace/:slug" element={<Workspace />} />

          {/* Authenticated app */}
          <Route element={<AppLayout />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/projects" element={<Projects />} />
            <Route path="/projects/:slug" element={<ProjectDetail />} />
            <Route path="/rooms" element={<Rooms />} />
            <Route path="/rooms/:id" element={<RoomView />} />
            <Route path="/peer-review" element={<PeerReview />} />
            <Route path="/classement" element={<Leaderboard />} />
            <Route path="/coalitions" element={<Coalitions />} />
            <Route path="/piscine" element={<Piscine />} />
            <Route path="/journey" element={<Journey />} />
            <Route path="/skills" element={<SkillGraph />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/arena" element={<Arena />} />
            <Route path="/mentor" element={<Mentor />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/hiring" element={<Hiring />} />
            <Route path="/exam" element={<Exam />} />
          </Route>

          <Route path="*" element={<NotFound />} />
        </Routes>
      </Suspense>
    </>
  )
}
