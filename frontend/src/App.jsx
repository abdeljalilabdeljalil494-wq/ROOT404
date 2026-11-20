import { Suspense, lazy, useEffect } from 'react'
import { Route, Routes, useLocation } from 'react-router-dom'

import PrototypeFeature from './components/PrototypeFeature'
import RequireAuth from './components/RequireAuth'
import PublicLayout from './layouts/PublicLayout'
import AppLayout from './layouts/AppLayout'
import Home from './pages/Home'
import ErrorBoundary from './components/ui/ErrorBoundary'

/* Code-split every non-landing route */
const About = lazy(() => import('./pages/About'))
const Parcours = lazy(() => import('./pages/Parcours'))
const Blog = lazy(() => import('./pages/Blog'))
const Community = lazy(() => import('./pages/Community'))
const OAuthCallback = lazy(() => import('./pages/auth/OAuthCallback'))
const Login = lazy(() => import('./pages/auth/Login'))
const Register = lazy(() => import('./pages/auth/Register'))

const BetaProgress = lazy(() => import('./pages/BetaProgress'))
const Moderation = lazy(() => import('./pages/Moderation'))
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Projects = lazy(() => import('./pages/Projects'))
const ProjectDetail = lazy(() => import('./pages/ProjectDetail'))
const Workspace = lazy(() => import('./pages/Workspace'))
const Rooms = lazy(() => import('./pages/Rooms'))
const RoomView = lazy(() => import('./pages/RoomView'))
const PeerReview = lazy(() => import('./pages/PeerReviewLive'))
const Leaderboard = lazy(() => import('./pages/LeaderboardLive'))
const Coalitions = lazy(() => import('./pages/CoalitionsLive'))
const Piscine = lazy(() => import('./pages/Piscine'))
const LearningInsights = lazy(() => import('./pages/LearningInsights'))
const Arena = lazy(() => import('./pages/Arena'))
const Mentor = lazy(() => import('./pages/Mentor'))
const Profile = lazy(() => import('./pages/ProfileLive'))
const Portfolio = lazy(() => import('./pages/PortfolioLive'))
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
    <ErrorBoundary
      fallbackTitle="Erreur critique de l'application"
      fallbackMessage="Une erreur inattendue a bloqué l'application. Veuillez recharger la page."
    >
      <ScrollToTop />
      <Suspense fallback={<RouteFallback />}>
        <Routes>
          {/* Public marketing site */}
          <Route element={<PublicLayout />}>
            <Route index element={<Home />} />
            <Route path="/about" element={<About />} />
            <Route path="/parcours" element={<Parcours />} />
            <Route path="/blog" element={<Blog />} />
            <Route path="/communaute" element={<PrototypeFeature><Community /></PrototypeFeature>} />
          </Route>

          {/* Auth (no chrome) */}
          <Route path="/oauth/callback/:provider" element={<OAuthCallback />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Public portfolio (no chrome) */}
          <Route path="/u/:username" element={<Portfolio />} />
          <Route path="/portfolio" element={<Portfolio />} />

          <Route element={<RequireAuth />}>
          {/* Full-bleed IDE (own chrome) */}
          <Route path="/workspace" element={<Workspace />} />
          <Route path="/workspace/:slug" element={<Workspace />} />

          {/* Authenticated app with error boundary */}
          <Route
            element={
              <ErrorBoundary
                fallbackTitle="Erreur dans l'espace étudiant"
                fallbackMessage="Impossible de charger cette section. Réessayez ou retournez au tableau de bord."
              >
                <AppLayout />
              </ErrorBoundary>
            }
          >
            <Route path="/progress" element={<BetaProgress />} />
            <Route path="/moderation" element={<Moderation />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/projects" element={<Projects />} />
            <Route path="/projects/:slug" element={<ProjectDetail />} />
            <Route path="/rooms" element={<Rooms />} />
            <Route path="/rooms/:id" element={<RoomView />} />
            <Route path="/peer-review" element={<PeerReview />} />
            <Route path="/classement" element={<Leaderboard />} />
            <Route path="/coalitions" element={<Coalitions />} />
            <Route path="/piscine" element={<PrototypeFeature><Piscine /></PrototypeFeature>} />
            <Route path="/journey" element={<LearningInsights mode="journey" />} />
            <Route path="/skills" element={<LearningInsights mode="skills" />} />
            <Route path="/analytics" element={<LearningInsights mode="analytics" />} />
            <Route path="/arena" element={<PrototypeFeature><Arena /></PrototypeFeature>} />
            <Route path="/mentor" element={<Mentor />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/hiring" element={<PrototypeFeature><Hiring /></PrototypeFeature>} />
            <Route path="/exam" element={<PrototypeFeature><Exam /></PrototypeFeature>} />
          </Route>

          </Route>
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Suspense>
    </ErrorBoundary>
  )
}
