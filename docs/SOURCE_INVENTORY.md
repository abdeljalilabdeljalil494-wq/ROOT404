# Source inventory

Static scan of every listed source/test/model/schema/service/page; flags are contextual, not proof of defects or runtime verification.

| File | Lines | Flags |
|---|---:|---|
| `backend/README.md` | 208 | simulat, random |
| `backend/app/__init__.py` | 0 |  |
| `backend/app/api/__init__.py` | 0 |  |
| `backend/app/api/ai.py` | 83 |  |
| `backend/app/api/analytics.py` | 68 |  |
| `backend/app/api/arena.py` | 97 | random |
| `backend/app/api/auth.py` | 330 |  |
| `backend/app/api/coalitions.py` | 57 |  |
| `backend/app/api/dashboard.py` | 96 |  |
| `backend/app/api/exam.py` | 83 | random |
| `backend/app/api/hiring.py` | 89 | mock, random |
| `backend/app/api/judge.py` | 127 |  |
| `backend/app/api/leaderboard.py` | 80 |  |
| `backend/app/api/mentorship.py` | 100 | mock |
| `backend/app/api/peer_review.py` | 222 |  |
| `backend/app/api/piscine.py` | 73 |  |
| `backend/app/api/portfolio.py` | 99 |  |
| `backend/app/api/projects.py` | 440 |  |
| `backend/app/api/rooms.py` | 144 |  |
| `backend/app/api/router.py` | 109 |  |
| `backend/app/core/__init__.py` | 0 |  |
| `backend/app/core/cache.py` | 14 |  |
| `backend/app/core/config.py` | 151 | random |
| `backend/app/core/database.py` | 116 |  |
| `backend/app/core/dependencies.py` | 203 |  |
| `backend/app/core/security.py` | 251 | random |
| `backend/app/main.py` | 301 | random |
| `backend/app/manage.py` | 26 |  |
| `backend/app/models/__init__.py` | 122 |  |
| `backend/app/models/auth_state.py` | 24 |  |
| `backend/app/models/coalition.py` | 59 |  |
| `backend/app/models/correction.py` | 62 |  |
| `backend/app/models/project.py` | 79 |  |
| `backend/app/models/room.py` | 71 |  |
| `backend/app/models/submission.py` | 43 |  |
| `backend/app/models/user.py` | 111 |  |
| `backend/app/schemas/__init__.py` | 4 |  |
| `backend/app/schemas/auth.py` | 35 |  |
| `backend/app/schemas/judge.py` | 36 |  |
| `backend/app/schemas/project.py` | 56 |  |
| `backend/app/schemas/room.py` | 40 |  |
| `backend/app/services/__init__.py` | 0 |  |
| `backend/app/services/activity.py` | 11 |  |
| `backend/app/services/ai_helper.py` | 220 | random, TODO |
| `backend/app/services/ai_provider.py` | 29 |  |
| `backend/app/services/blackhole.py` | 106 |  |
| `backend/app/services/coalition.py` | 124 |  |
| `backend/app/services/correction.py` | 178 | random |
| `backend/app/services/email.py` | 32 |  |
| `backend/app/services/gamification.py` | 211 | random |
| `backend/app/services/integrity.py` | 173 | mock, simulat, random |
| `backend/app/services/judge.py` | 233 | simulat |
| `backend/app/services/room_service.py` | 171 |  |
| `backend/app/services/skill_graph.py` | 111 |  |
| `backend/migrations/env.py` | 22 |  |
| `backend/migrations/versions/0001_initial.py` | 570 |  |
| `backend/migrations/versions/0002_auth_state.py` | 40 |  |
| `backend/tests/conftest.py` | 82 |  |
| `backend/tests/test_api.py` | 144 |  |
| `backend/tests/test_configuration.py` | 15 |  |
| `backend/tests/test_edgecases.py` | 275 |  |
| `backend/tests/test_migrations.py` | 27 |  |
| `backend/tests/test_regressions.py` | 191 | mock |
| `backend/tests/test_runners.py` | 44 |  |
| `backend/tests/test_security.py` | 357 | mock |
| `frontend/src/App.jsx` | 128 |  |
| `frontend/src/components/Logo.jsx` | 111 |  |
| `frontend/src/components/PrototypeFeature.jsx` | 12 | mock |
| `frontend/src/components/RequireAuth.jsx` | 29 |  |
| `frontend/src/components/RequireAuth.test.jsx` | 34 | mock |
| `frontend/src/components/landing/CtaBanner.jsx` | 39 |  |
| `frontend/src/components/landing/Faq.jsx` | 57 | mock |
| `frontend/src/components/landing/FeatureStrip.jsx` | 56 | mock |
| `frontend/src/components/landing/Hero.jsx` | 122 | mock |
| `frontend/src/components/landing/HowItWorks.jsx` | 42 | mock |
| `frontend/src/components/landing/Pathways.jsx` | 65 | mock |
| `frontend/src/components/landing/SystemsShowcase.jsx` | 106 | mock |
| `frontend/src/components/landing/Testimonials.jsx` | 40 | mock |
| `frontend/src/components/layout/AppTopbar.jsx` | 140 |  |
| `frontend/src/components/layout/Footer.jsx` | 118 |  |
| `frontend/src/components/layout/Navbar.jsx` | 144 | mock |
| `frontend/src/components/layout/Sidebar.jsx` | 184 |  |
| `frontend/src/components/ui/Avatar.jsx` | 32 |  |
| `frontend/src/components/ui/Badge.jsx` | 20 |  |
| `frontend/src/components/ui/BarChart.jsx` | 31 |  |
| `frontend/src/components/ui/Button.jsx` | 54 |  |
| `frontend/src/components/ui/EmptyState.jsx` | 14 |  |
| `frontend/src/components/ui/ErrorBoundary.jsx` | 104 |  |
| `frontend/src/components/ui/Heatmap.jsx` | 65 | mock |
| `frontend/src/components/ui/Icon.jsx` | 320 | mock |
| `frontend/src/components/ui/LevelRing.jsx` | 39 |  |
| `frontend/src/components/ui/ProgressBar.jsx` | 41 |  |
| `frontend/src/components/ui/ResourceState.jsx` | 5 |  |
| `frontend/src/components/ui/SectionHeading.jsx` | 23 |  |
| `frontend/src/components/ui/StatCard.jsx` | 31 |  |
| `frontend/src/components/ui/Tabs.jsx` | 40 | mock |
| `frontend/src/components/ui/ThemeToggle.jsx` | 16 |  |
| `frontend/src/data/mock.js` | 673 | mock |
| `frontend/src/hooks/usePageHeader.js` | 16 |  |
| `frontend/src/hooks/useResource.js` | 18 |  |
| `frontend/src/hooks/useTheme.jsx` | 20 |  |
| `frontend/src/layouts/AppLayout.jsx` | 33 |  |
| `frontend/src/layouts/PublicLayout.jsx` | 16 |  |
| `frontend/src/main.jsx` | 16 |  |
| `frontend/src/pages/About.jsx` | 157 | mock |
| `frontend/src/pages/Analytics.jsx` | 210 | mock |
| `frontend/src/pages/Arena.jsx` | 149 | mock |
| `frontend/src/pages/Blog.jsx` | 120 | mock |
| `frontend/src/pages/Coalitions.jsx` | 151 | mock |
| `frontend/src/pages/Community.jsx` | 160 | mock |
| `frontend/src/pages/Dashboard.jsx` | 268 |  |
| `frontend/src/pages/Exam.jsx` | 167 |  |
| `frontend/src/pages/Hiring.jsx` | 147 |  |
| `frontend/src/pages/Home.jsx` | 28 |  |
| `frontend/src/pages/Journey.jsx` | 142 | mock |
| `frontend/src/pages/Leaderboard.jsx` | 206 | mock |
| `frontend/src/pages/Mentor.jsx` | 270 | mock |
| `frontend/src/pages/NotFound.jsx` | 76 |  |
| `frontend/src/pages/Parcours.jsx` | 157 | mock |
| `frontend/src/pages/PeerReview.jsx` | 167 | mock |
| `frontend/src/pages/Piscine.jsx` | 155 | mock |
| `frontend/src/pages/Portfolio.jsx` | 187 | mock |
| `frontend/src/pages/Profile.jsx` | 264 | mock |
| `frontend/src/pages/ProjectDetail.jsx` | 308 |  |
| `frontend/src/pages/Projects.jsx` | 290 |  |
| `frontend/src/pages/RoomView.jsx` | 266 | mock |
| `frontend/src/pages/Rooms.jsx` | 118 | mock |
| `frontend/src/pages/Settings.jsx` | 263 | mock |
| `frontend/src/pages/SkillGraph.jsx` | 193 | mock |
| `frontend/src/pages/Workspace.jsx` | 509 |  |
| `frontend/src/pages/auth/AuthLayout.jsx` | 90 |  |
| `frontend/src/pages/auth/Login.jsx` | 167 |  |
| `frontend/src/pages/auth/Login.test.jsx` | 37 | mock |
| `frontend/src/pages/auth/Register.jsx` | 182 |  |
| `frontend/src/services/api.js` | 578 | mock, random |
| `frontend/src/services/api.test.js` | 235 | mock, simulat |
| `frontend/src/services/integration.test.js` | 41 | mock |
| `frontend/src/test/setup.js` | 71 | mock |
| `judge_sandbox/runner.py` | 58 |  |
| `judge_sandbox/runners/common.py` | 80 |  |
| `judge_sandbox/runners/runner_c.py` | 15 |  |
| `judge_sandbox/runners/runner_cpp.py` | 15 |  |
| `judge_sandbox/runners/runner_js.py` | 15 |  |
| `judge_sandbox/runners/runner_python.py` | 15 |  |
