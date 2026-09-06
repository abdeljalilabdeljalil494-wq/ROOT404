# ROOT 404 — Frontend

> Elite Coder Platform · École 1337 / 42-inspired peer-learning platform for Tunisia.
> Complete React UI: public marketing site + authenticated student app + browser IDE.

---

## 1. Quick start

```bash
cd frontend
npm install
npm run dev          # → http://localhost:5173
```

Other scripts:

```bash
npm run build        # production bundle into dist/
npm run preview      # serve dist/ locally to sanity-check the build
```

**Requirements:** Node **18+** (developed on Node 20.20, npm 10.8).

### Environment variables

Create `frontend/.env.local` (all optional — the app runs fully without it):

| Variable          | Default                 | Purpose                                                              |
| ----------------- | ----------------------- | -------------------------------------------------------------------- |
| `VITE_API_URL`    | `/api`                  | Axios `baseURL`. Leave empty in dev so the Vite proxy handles it.      |
| `VITE_API_TARGET` | `http://localhost:8000` | Where the dev server proxies `/api` (your FastAPI instance).           |
| `VITE_USE_MOCK`   | `true`                  | Set to `false` to stop serving mock data and call the real backend.    |

---

## 2. Tech stack

Chosen to match the project README (`React` + `Monaco Editor`) and filled in with the
standard, boring, production-safe defaults where the README was silent:

| Concern      | Choice                    | Why                                                                 |
| ------------ | ------------------------- | ------------------------------------------------------------------- |
| Framework    | **React 18** (plain JSX)  | Required by the README. No TypeScript, matching the plain `src/` spec. |
| Build tool   | **Vite 5**                | Instant HMR, tiny config, first-class React plugin.                   |
| Styling      | **Tailwind CSS 3**        | Design-token-driven — the mockup palette lives in `tailwind.config.js`. |
| Routing      | **React Router 6**        | Nested layouts map 1:1 onto "public shell / app shell / chrome-less".  |
| Code editor  | **@monaco-editor/react**  | Explicitly named in the README (the VS Code engine).                   |
| Icons        | **lucide-react**          | Thin, consistent 1.9px stroke that matches the mockups.                |
| HTTP         | **axios**                 | Interceptors for the JWT bearer token + 401 handling.                  |

No state-management library: page-local `useState` plus one React context for the
theme is enough for a UI layer this size. Add TanStack Query when the real API lands.

---

## 3. Project structure

Follows the layout mandated by the main README (`components / pages / services / styles`),
with three additive folders (`layouts`, `hooks`, `data`) to keep files small.

```
frontend/
├── public/
│   ├── favicon.svg
│   └── hero-medina.jpg          # hero art (local, so there are zero external deps)
├── index.html
├── tailwind.config.js           # ← the design system (palette, fonts, shadows)
├── postcss.config.js
├── vite.config.js               # dev proxy + manual vendor chunks
└── src/
    ├── main.jsx                 # ReactDOM root + ThemeProvider + BrowserRouter
    ├── App.jsx                  # every route, lazy-loaded, in one place
    ├── styles/
    │   └── index.css            # Tailwind layers + .card/.chip/.input utilities
    ├── data/
    │   └── mock.js              # single source of demo content for every screen
    ├── services/
    │   └── api.js               # axios client + authService/projectService/...
    ├── hooks/
    │   ├── useTheme.jsx         # dark/light context, persisted in localStorage
    │   └── usePageHeader.js     # lets a page push its title into the app topbar
    ├── layouts/
    │   ├── PublicLayout.jsx     # Navbar + <Outlet> + Footer
    │   └── AppLayout.jsx        # Sidebar + AppTopbar + <Outlet>
    ├── components/
    │   ├── Logo.jsx             # <LogoMark> — the ROOT 404 "root system" glyph, inline SVG
    │   ├── ui/                  # 14 primitives, see below
    │   ├── layout/              # Navbar, Sidebar, AppTopbar, Footer
    │   └── landing/             # the 8 sections of the marketing page
    └── pages/                   # 27 screens (see the routing table)
```

### Reusable primitives (`src/components/ui/`)

`Icon` · `Button` · `Badge` · `ProgressBar` · `Avatar` · `StatCard` · `Tabs` ·
`EmptyState` · `ThemeToggle` · `BarChart` · `LevelRing` · `SectionHeading` · `Heatmap`

Every one is prop-driven and used in at least three places. Notable ones:

- **`Icon`** — renders a lucide icon *by string name* (`<Icon name="Trophy" />`) so icons
  can live in data files and config objects. Backed by an **explicit registry** of the 151
  icons actually used, not `import * as` — that keeps the icon chunk at 63 kB instead of 774 kB.
- **`BarChart` / `LevelRing` / `Heatmap`** — hand-rolled inline SVG/CSS. No charting
  library, so nothing to tree-shake and full control over the mockup's exact look.
- **`Button`** — `variant` (`primary|secondary|ghost|danger|outline`), `size`, `iconLeft`,
  `iconRight`, `full`, `loading`. Renders as `<Link>` automatically when given `to`.

---

## 4. Routing map (`src/App.jsx`)

All routes are `React.lazy` + one shared `<Suspense>` fallback, so each page is its own chunk.

| Shell            | Routes                                                                                                                                                                              |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **PublicLayout** | `/` `/about` `/parcours` `/blog` `/communaute`                                                                                                                                        |
| **AppLayout**    | `/dashboard` `/projects` `/projects/:slug` `/rooms` `/rooms/:id` `/peer-review` `/classement` `/coalitions` `/piscine` `/journey` `/skills` `/analytics` `/arena` `/mentor` `/profile` `/settings` |
| **Chrome-less**  | `/login` `/register` `/workspace` `/workspace/:slug` `/u/:username` `/portfolio`                                                                                                       |
| **Catch-all**    | `*` → terminal-styled 404 page                                                                                                                                                        |

`AppLayout` owns the topbar state and passes `setHeader` down through the Outlet context;
pages declare their own title/breadcrumb/actions with `usePageHeader({ title, breadcrumb, actions }, deps)`.

---

## 5. Design system

Colours were **sampled pixel-by-pixel from the supplied mockups**, not eyeballed, and are
exposed as Tailwind tokens in `tailwind.config.js`.

```
brand.500  #F8851F   primary CTA orange       root.950  #04090E   page background
brand.400  #FFAD57   hover / highlight        root.900  #060B10   deep surface
brand.600  #E0710F   pressed                  root.850  #080D12   sunken surface
                                              root.800  #0C1116   card surface
ok      #2ECC71      warn   #F5B942           root.750  #101720   raised / hover
danger  #E5484D      info   #3B9EFF           line      #161E27   default border

ink #E8EDF2 · ink-soft #9AA7B4 · ink-dim #6B7885 · ink-faint #495562
```

**Typography** — Inter (UI), JetBrains Mono (code, stats, terminal), Noto Kufi Arabic
(`font-ar`, used for the RTL hero subtitle). Loaded via `<link>` in `index.html`.

**Shared utilities** in `src/styles/index.css`: `.container-page`, `.card`, `.chip`,
`.input`, `.select`, `.no-scrollbar`, plus `bg-grid` / `bg-dots` backdrops and an
`animate-blink` caret keyframe.

**Dark by default.** `useTheme` toggles a `light` class on `<html>` and persists to
localStorage; the mockups are dark, so light mode is a courtesy variant.

---

## 6. Responsive strategy

Mobile-first, three real breakpoints — every screen was rendered and inspected at
390 px, 768 px and 1440 px.

- **Navbar** collapses into a slide-down sheet below `md`.
- **Sidebar** is a fixed 258 px rail at `lg+`; below that it becomes an off-canvas drawer
  with a scrim, opened from the topbar hamburger and auto-closing on navigation.
- **Data tables** (leaderboard, peer review) switch from a `<table>` to stacked cards on
  small screens instead of scrolling horizontally.
- **Workspace** hides the file explorer and the terminal rail under `lg` and exposes them
  as toggles, so the editor always gets the full width on a phone.
- Multi-column dashboards degrade `4 → 2 → 1` columns via plain CSS grid.

---

## 7. Connecting the FastAPI backend

`src/services/api.js` already contains the full client. Every call goes through one helper:

```js
async function resolve(mockValue, request) {
  if (USE_MOCK) { await delay(); return mockValue }   // ← demo mode
  const { data } = await request()                     // ← real FastAPI call
  return data
}
```

So switching from the demo to the real platform is a one-line change:

```bash
echo "VITE_USE_MOCK=false" >> .env.local
```

…and the exported services (`authService`, `projectService`, `roomService`,
`leaderboardService`, `aiService`, `sandboxService`) start hitting
`/api/...`, which Vite proxies to `VITE_API_TARGET` in dev. The JWT is read from
`localStorage.root404_token` by a request interceptor, and a 401 response clears it.

WebSocket / WebRTC hooks for the rooms are the natural next step — the UI in
`RoomView.jsx` is already structured around a `messages` array and a member list,
so it only needs the socket wired in place of the local state.

---

## 8. Build output

```
dist/assets/react-*.js     163.58 kB │ gzip: 53.37 kB   ← React + Router
dist/assets/index-*.js      76.08 kB │ gzip: 25.21 kB   ← shell, layouts, primitives
dist/assets/icons-*.js      63.19 kB │ gzip: 12.19 kB   ← 151 lucide icons
dist/assets/monaco-*.js     14.90 kB │ gzip:  5.13 kB   ← loader (Monaco itself is CDN-lazy)
+ one 3–14 kB chunk per page, fetched on navigation
```

~96 kB gzipped for first paint, zero build warnings. Vendor splitting is configured in
`vite.config.js` under `build.rollupOptions.output.manualChunks`.

---

## 9. Notes & assumptions

Where the mockups or the main README were ambiguous, these choices were made:

1. **Language.** The desktop mockup UI is in French, so the whole interface is French, with
   Arabic used exactly where the mockups use it (the hero subtitle, RTL, `font-ar`).
2. **Auth flow.** The README specifies "Email OTP + JWT", so login is a two-step
   email → 6-digit code flow with no password field anywhere. Registration is a 3-step
   wizard framed as "applying to the Piscine".
3. **Mock data.** All demo content lives in one file, `src/data/mock.js`, so it can be
   deleted wholesale once the API is live — no fixture is inlined in a component.
4. **Hero artwork.** Generated locally to `public/hero-medina.jpg` rather than linking a
   stock URL, so the app has no external image dependency and works offline.
5. **Sandbox / terminal / moulinette** are faithful *simulations* driven by timers — the
   real execution belongs to the Docker/Ubuntu backend described in the main README.
6. **AI Mentor** is deliberately socratic in its scripted answers, mirroring the README's
   anti-cheating stance that the assistant must never hand over a finished solution.
