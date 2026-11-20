import { useCallback, useEffect, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import Editor from '@monaco-editor/react'
import '../services/editor'
import Logo from '../components/Logo'
import Icon from '../components/ui/Icon'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import Avatar from '../components/ui/Avatar'
import ProgressBar from '../components/ui/ProgressBar'
import { aiService, judgeService, projectService } from '../services/api'
import { useCurrentUser } from '../components/RequireAuth'
const STARTERS = {
  c: '#include <stdio.h>\nint main(void) { puts("Hello ROOT404"); return 0; }\n',
  cpp: '#include <iostream>\nint main() { std::cout << "Hello ROOT404\\n"; }\n',
  python: 'print("Hello ROOT404")\n',
  javascript: 'console.log("Hello ROOT404");\n',
}
const EXTENSIONS = { c: 'c', cpp: 'cpp', python: 'py', javascript: 'js' }


/* ------------------------------------------------------------------ */
/* Monaco theme matching the ROOT 404 palette                          */
/* ------------------------------------------------------------------ */
const ROOT_THEME = {
  base: 'vs-dark',
  inherit: true,
  rules: [
    { token: 'comment', foreground: '5A6675', fontStyle: 'italic' },
    { token: 'keyword', foreground: 'F8851F' },
    { token: 'string', foreground: '7FD88F' },
    { token: 'number', foreground: 'FFAD57' },
    { token: 'type', foreground: '6FB7FF' },
    { token: 'identifier', foreground: 'D7DEE6' },
    { token: 'delimiter', foreground: '8A97A5' },
  ],
  colors: {
    'editor.background': '#0A0F15',
    'editor.foreground': '#D7DEE6',
    'editorLineNumber.foreground': '#3A4553',
    'editorLineNumber.activeForeground': '#F8851F',
    'editor.selectionBackground': '#F8851F26',
    'editor.lineHighlightBackground': '#FFFFFF07',
    'editorCursor.foreground': '#F8851F',
    'editorIndentGuide.background1': '#18212B',
    'editorGutter.background': '#0A0F15',
    'scrollbarSlider.background': '#1B242E88',
  },
}

/* ------------------------------------------------------------------ */
/* File explorer                                                       */
/* ------------------------------------------------------------------ */
const FILE_ICON = { c: 'FileCode2', h: 'FileType2', make: 'Wrench', md: 'FileText' }

function TreeNode({ node, depth = 0, activeFile, onOpen }) {
  const [open, setOpen] = useState(node.open ?? false)

  if (node.type === 'folder') {
    return (
      <li>
        <button
          onClick={() => setOpen((o) => !o)}
          className="flex w-full items-center gap-1.5 rounded px-2 py-[5px] text-[12px] text-ink-soft transition-colors hover:bg-white/[0.05]"
          style={{ paddingLeft: 8 + depth * 12 }}
        >
          <Icon name={open ? 'ChevronDown' : 'ChevronRight'} size={12} className="shrink-0 text-ink-faint" />
          <Icon name={open ? 'FolderOpen' : 'Folder'} size={13} className="shrink-0 text-brand-500/80" />
          <span className="truncate">{node.name}</span>
        </button>
        {open && (
          <ul>
            {node.children.map((c) => (
              <TreeNode key={c.name} node={c} depth={depth + 1} activeFile={activeFile} onOpen={onOpen} />
            ))}
          </ul>
        )}
      </li>
    )
  }

  const on = activeFile === node.name
  return (
    <li>
      <button
        onClick={() => onOpen(node)}
        className={`flex w-full items-center gap-1.5 rounded px-2 py-[5px] text-[12px] transition-colors ${
          on ? 'bg-brand-500/12 text-brand-400' : 'text-ink-soft hover:bg-white/[0.05]'
        }`}
        style={{ paddingLeft: 20 + depth * 12 }}
      >
        <Icon name={FILE_ICON[node.lang] || 'File'} size={13} className="shrink-0 text-ink-dim" />
        <span className="truncate">{node.name}</span>
      </button>
    </li>
  )
}

/* ------------------------------------------------------------------ */
/* Page                                                                */
/* ------------------------------------------------------------------ */
export default function Workspace() {
  const { slug = 'minishell' } = useParams()

  const currentUser = useCurrentUser()
  const [language, setLanguage] = useState('c')
  const [review, setReview] = useState(null)
  const [reviewBusy, setReviewBusy] = useState(false)
  const [reviewError, setReviewError] = useState('')
  const drafts = useRef({})
  const fileTree = [{ name: `main.${EXTENSIONS[language]}`, type: 'file', lang: language }]
  const [evaluation, setEvaluation] = useState(null)
  const moulinetteTests = evaluation?.tests || []
  const [tabs, setTabs] = useState([{ name: 'main.c', lang: 'c' }])
  const [activeFile, setActiveFile] = useState('main.c')
  const [code, setCode] = useState('#include <stdio.h>\n\nint main(void) {\n    puts("Hello ROOT404");\n    return 0;\n}\n')
  const [lines, setLines] = useState([{ t: 'info', v: 'Aucune exécution effectuée.' }])
  const [running, setRunning] = useState(false)
  const [moulinetteOpen, setMoulinetteOpen] = useState(true)
  const [explorerOpen, setExplorerOpen] = useState(false)
  const [panelTab, setPanelTab] = useState('moulinette')
  const [cursor, setCursor] = useState({ line: 1, column: 1 })
  const termRef = useRef(null)

  useEffect(() => {
    document.title = `${slug} — Workspace · ROOT 404`
  }, [slug])

  useEffect(() => {
    termRef.current?.scrollTo({ top: termRef.current.scrollHeight })
  }, [lines])

  const openFile = useCallback((node) => {
    setTabs((t) => (t.some((x) => x.name === node.name) ? t : [...t, node]))
    setActiveFile(node.name)
    setExplorerOpen(false)
  }, [])

  const closeTab = (name, e) => {
    e.stopPropagation()
    setTabs((t) => {
      const next = t.filter((x) => x.name !== name)
      if (activeFile === name && next.length) setActiveFile(next[next.length - 1].name)
      return next
    })
  }

  const run = async (submit = false) => {
    setRunning(true)
    setMoulinetteOpen(true)
    setPanelTab('moulinette')
    setLines([{ t: 'cmd', v: submit ? 'Soumission au juge…' : 'Exécution…' }])
    try {
      const result = submit
        ? await projectService.submit(slug, { [`main.${EXTENSIONS[language]}`]: code }, language)
        : await judgeService.run({ code, language })
      if (submit) setEvaluation(result)
      setLines([result.status, result.output, result.error, result.logs].filter(Boolean).map(v => ({ t: 'info', v })))
    } catch (error) {
      setLines([{ t: 'error', v: typeof error.response?.data?.detail === 'string' ? error.response.data.detail : 'Exécution indisponible. Aucun résultat créé.' }])
    } finally { setRunning(false) }
  }

  const reviewCode = async () => {
    setReviewBusy(true); setReviewError(''); setReview(null)
    try { setReview(await aiService.review(code, language, slug)) }
    catch { setReviewError('Analyse IA indisponible. Aucun avis généré.') }
    finally { setReviewBusy(false) }
  }

  const passed = moulinetteTests.filter((t) => t.status === 'pass').length
  const score = evaluation?.score ?? 0

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-root-900">
      {/* ---------------- Top bar ---------------- */}
      <header className="flex h-[52px] shrink-0 items-center gap-3 border-b border-line bg-root-950 px-3 sm:px-4">
        <Logo size={26} compact />
        <nav className="hidden items-center gap-1.5 text-[12.5px] sm:flex" aria-label="Fil d'Ariane">
          <Link to="/projects" className="text-ink-dim hover:text-ink">Mes projets</Link>
          <Icon name="ChevronRight" size={12} className="text-ink-faint" />
          <span className="font-mono font-semibold text-ink">{slug}</span>
        </nav>

        <button
          onClick={() => setExplorerOpen((o) => !o)}
          className="grid h-8 w-8 place-items-center rounded-md text-ink-soft hover:bg-white/[0.06] lg:hidden"
          aria-label="Explorateur"
        >
          <Icon name="PanelLeft" size={16} />
        </button>

        <div className="ml-auto flex items-center gap-1">
          <Badge tone="neutral" className="mr-2 hidden sm:inline-flex">Exécution distante sous réserve de disponibilité</Badge>
          {['Search', 'GitBranch', 'History', 'Bell'].map((i) => (
            <button
              key={i}
              aria-label={i}
              disabled title="Fonction non disponible"
              className="grid h-8 w-8 place-items-center rounded-md text-ink-soft transition-colors hover:bg-white/[0.06] hover:text-ink"
            >
              <Icon name={i} size={15} />
            </button>
          ))}
          <Link to="/profile" className="ml-1">
            <Avatar src={currentUser.avatar} name={currentUser.displayName} size="xs" status="online" />
          </Link>
        </div>
      </header>

      {/* ---------------- Body ---------------- */}
      <div className="flex min-h-0 flex-1">
        {/* Explorer */}
        <aside
          className={`absolute inset-y-[52px] left-0 z-30 flex w-[220px] shrink-0 flex-col border-r border-line bg-root-950 transition-transform lg:static lg:inset-auto lg:translate-x-0 ${
            explorerOpen ? 'translate-x-0' : '-translate-x-full'
          }`}
        >
          <div className="flex h-9 shrink-0 items-center justify-between border-b border-line px-3">
            <span className="text-[10.5px] font-bold uppercase tracking-[0.13em] text-ink-dim">
              Explorateur
            </span>
            <div className="flex gap-0.5">
              {['FilePlus2', 'FolderPlus', 'RefreshCw'].map((i) => (
                <button key={i} aria-label={i} disabled title="Fonction non disponible" className="grid h-6 w-6 place-items-center rounded text-ink-faint hover:bg-white/[0.06] hover:text-ink">
                  <Icon name={i} size={12} />
                </button>
              ))}
            </div>
          </div>
          <ul className="flex-1 overflow-y-auto py-2">
            {fileTree.map((n) => (
              <TreeNode key={n.name} node={n} activeFile={activeFile} onOpen={openFile} />
            ))}
          </ul>
          <div className="shrink-0 border-t border-line p-2.5">
            <div className="rounded-md bg-root-800 p-2.5">
              <p className="text-[10px] font-semibold uppercase tracking-wider text-ink-faint">
                Conteneur
              </p>
              <p className="mt-1 flex items-center gap-1.5 font-mono text-[11px] text-ink-soft">
                <Icon name="Container" size={12} className="text-info" /> Métriques indisponibles
              </p>
              <div className="mt-2 space-y-1.5">
                {[
                  { l: 'CPU', v: 0 },
                  { l: 'RAM', v: 0 },
                ].map((m) => (
                  <div key={m.l} className="flex items-center gap-2">
                    <span className="w-7 text-[9.5px] text-ink-faint">{m.l}</span>
                    <ProgressBar value={m.v} height={3} className="flex-1" />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </aside>

        {/* Editor column */}
        <div className="flex min-w-0 flex-1 flex-col">
          {/* Tab strip + actions */}
          <div className="flex h-10 shrink-0 items-center gap-2 border-b border-line bg-root-950 pr-2">
            <div className="no-scrollbar flex h-full min-w-0 flex-1 overflow-x-auto">
              {tabs.map((t) => {
                const on = t.name === activeFile
                return (
                  <button
                    key={t.name}
                    onClick={() => setActiveFile(t.name)}
                    className={`group relative flex h-full shrink-0 items-center gap-2 border-r border-line px-3.5 font-mono text-[12px] transition-colors ${
                      on ? 'bg-[#0A0F15] text-ink' : 'text-ink-dim hover:bg-white/[0.03]'
                    }`}
                  >
                    {on && <span className="absolute inset-x-0 top-0 h-[2px] bg-brand-500" />}
                    <Icon name={FILE_ICON[t.lang] || 'File'} size={12} className="text-ink-faint" />
                    {t.name}
                    <span
                      onClick={(e) => closeTab(t.name, e)}
                      className="grid h-4 w-4 place-items-center rounded opacity-0 transition-opacity hover:bg-white/10 group-hover:opacity-100"
                    >
                      <Icon name="X" size={11} />
                    </span>
                  </button>
                )
              })}
              <button disabled title="Éditeur mono-fichier" className="grid h-full w-9 shrink-0 place-items-center text-ink-faint hover:text-ink" aria-label="Nouvel onglet">
                <Icon name="Plus" size={14} />
              </button>
            </div>

            <div className="flex shrink-0 items-center gap-2">
              <select aria-label="Langage de programmation" value={language} disabled={running} className="input w-auto" onChange={(event) => {
                const next = event.target.value
                drafts.current[language] = code
                setLanguage(next)
                setCode(drafts.current[next] ?? STARTERS[next])
                const name = `main.${EXTENSIONS[next]}`
                setTabs([{ name, lang: next }]); setActiveFile(name); setEvaluation(null)
              }}>
                <option value="c">C</option><option value="cpp">C++</option><option value="python">Python</option><option value="javascript">JavaScript</option>
              </select>
              <Button aria-label="Exécuter le code" size="sm" variant="outline" icon="Play" onClick={() => run(false)} loading={running}>
                <span className="hidden sm:inline">Exécuter</span>
              </Button>
              <Button aria-label="Soumettre au Judge" size="sm" icon="Cpu" onClick={() => run(true)} loading={running}>
                <span className="hidden sm:inline">Passer la Moulinette</span>
                <span className="sm:hidden">Moulinette</span>
              </Button>
            </div>
          </div>

          {/* Monaco */}
          <div className="min-h-0 flex-1 bg-[#0A0F15]">
            <Editor
              height="100%"
              language={language === 'cpp' ? 'cpp' : language}
              value={code}
              onChange={(v) => setCode(v ?? '')}
              theme="root404"
              beforeMount={(monaco) => monaco.editor.defineTheme('root404', ROOT_THEME)}
              onMount={(editor) => {
                editor.onDidChangeCursorPosition((e) =>
                  setCursor({ line: e.position.lineNumber, column: e.position.column }),
                )
              }}
              loading={
                <div className="flex h-full items-center justify-center gap-2 text-[12px] text-ink-dim">
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-line border-t-brand-500" />
                  Chargement de l'éditeur…
                </div>
              }
              options={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 13,
                lineHeight: 21,
                minimap: { enabled: false },
                scrollBeyondLastLine: false,
                padding: { top: 14, bottom: 14 },
                smoothScrolling: true,
                cursorBlinking: 'smooth',
                renderLineHighlight: 'all',
                tabSize: 4,
                insertSpaces: false,
                automaticLayout: true,
                scrollbar: { verticalScrollbarSize: 9, horizontalScrollbarSize: 9 },
              }}
            />
          </div>

          {/* Status bar */}
          <div className="flex h-[26px] shrink-0 items-center gap-4 border-t border-line bg-root-950 px-3 font-mono text-[10.5px] text-ink-dim">
            <span className="flex items-center gap-1.5 text-ok">
              <Icon name="CircleCheck" size={11} /> Norme non vérifiée
            </span>
            <span className="flex items-center gap-1.5">
              <Icon name="GitBranch" size={11} /> main
            </span>
            <span className="ml-auto hidden sm:inline">Ln {cursor.line}, Col {cursor.column}</span>
            <span className="hidden md:inline">Tabs: 4</span>
            <span className="hidden md:inline">UTF-8</span>
            <span className="hidden lg:inline">LF</span>
            <span className="text-brand-500">{language}</span>
          </div>
        </div>

        {/* Right panel */}
        <aside
          className={`hidden shrink-0 flex-col border-l border-line bg-root-950 transition-all xl:flex ${
            moulinetteOpen ? 'w-[330px]' : 'w-0'
          }`}
        >
          {moulinetteOpen && (
            <>
              {/* --- Terminal (top half, like the reference layout) --- */}
              <div className="flex h-9 shrink-0 items-center border-b border-line px-3.5">
                <span className="text-[10.5px] font-bold uppercase tracking-[0.13em] text-ink-dim">
                  Terminal
                </span>
                <span className="ml-2 h-1.5 w-1.5 rounded-full bg-ok" />
                <button
                  onClick={() => setMoulinetteOpen(false)}
                  aria-label="Fermer le panneau"
                  className="ml-auto grid h-6 w-6 place-items-center rounded text-ink-faint hover:bg-white/[0.06] hover:text-ink"
                >
                  <Icon name="X" size={12} />
                </button>
              </div>

              <div
                ref={termRef}
                className="min-h-[180px] flex-1 space-y-1 overflow-y-auto bg-[#080D12] p-3 font-mono text-[11px] leading-relaxed"
              >
                {lines.map((l, i) => (
                  <div
                    key={i}
                    className={l.t === 'cmd' ? 'text-brand-400' : l.t === 'ok' ? 'text-ok' : 'text-ink-soft'}
                  >
                    {l.v}
                  </div>
                ))}
                {running && <span className="inline-block h-3 w-1.5 animate-blink bg-brand-500" />}
              </div>

              {/* --- Moulinette / AI Review (bottom half) --- */}
              <div className="flex h-9 shrink-0 items-center border-y border-line">
                {[
                  { k: 'moulinette', l: 'Moulinette' },
                  { k: 'ai', l: 'AI Review' },
                ].map((t) => (
                  <button
                    key={t.k}
                    onClick={() => setPanelTab(t.k)}
                    className={`relative h-full px-3.5 text-[10.5px] font-bold uppercase tracking-[0.1em] transition-colors ${
                      panelTab === t.k ? 'text-brand-500' : 'text-ink-dim hover:text-ink'
                    }`}
                  >
                    {t.l}
                    {panelTab === t.k && <span className="absolute inset-x-2.5 bottom-0 h-[2px] bg-brand-500" />}
                  </button>
                ))}
                <span
                  className={`ml-auto mr-3.5 font-mono text-[12px] font-bold ${
                    score >= 80 ? 'text-ok' : 'text-warn'
                  }`}
                >
                  {evaluation ? `${score}/100` : 'Non évalué'}
                </span>
              </div>

              <div className="h-[46%] min-h-[240px] overflow-y-auto p-3.5">
                {panelTab === 'moulinette' ? (
                  <>
                    <ProgressBar
                      value={score}
                      color={score >= 80 ? '#2ECC71' : '#F5B942'}
                      height={5}
                      className="mb-3.5"
                    />
                    <ul className="space-y-1.5">
                      {moulinetteTests.map((t) => (
                        <li
                          key={t.name}
                          className="flex items-center gap-2 rounded-md border border-line/60 bg-root-850 px-2.5 py-2 text-[11px]"
                        >
                          <Icon
                            name={t.status === 'pass' ? 'CheckCircle2' : t.status === 'warn' ? 'AlertTriangle' : 'XCircle'}
                            size={13}
                            className={t.status === 'pass' ? 'text-ok' : t.status === 'warn' ? 'text-warn' : 'text-danger'}
                          />
                          <span className="min-w-0 flex-1 truncate text-ink-soft">{t.name}</span>
                          <span
                            className={`shrink-0 font-mono text-[10px] ${
                              t.status === 'pass' ? 'text-ok' : t.status === 'warn' ? 'text-warn' : 'text-danger'
                            }`}
                          >
                            {t.detail}
                          </span>
                        </li>
                      ))}
                    </ul>
                    <Button to="/peer-review" size="sm" full className="mt-3.5" iconRight="ArrowRight">
                      Envoyer en Peer Review
                    </Button>
                  </>
                ) : (
                  <>
                    <Button onClick={reviewCode} loading={reviewBusy} disabled={!code.trim()} size="sm">Analyser le code avec l’IA</Button>
                    <p className="mt-2 text-xs text-ink-dim">Envoie le fichier au fournisseur configuré. Son avis n’est pas une exécution ni une note.</p>
                    {reviewError && <p role="alert">{reviewError}</p>}
                    {review && <p className="mt-3 whitespace-pre-wrap break-words text-sm">{review.text}</p>}
                    <p className="mt-4 text-[10.5px] leading-relaxed text-ink-faint">
                      L'AI Review ne remplace pas le Peer Review et ne valide jamais un projet seule.
                    </p>
                  </>
                )}
              </div>
            </>
          )}
        </aside>

        {!moulinetteOpen && (
          <button
            onClick={() => setMoulinetteOpen(true)}
            className="hidden w-9 shrink-0 items-center justify-center border-l border-line bg-root-950 text-ink-dim hover:text-brand-500 xl:flex"
            aria-label="Ouvrir le panneau"
          >
            <Icon name="PanelRight" size={16} />
          </button>
        )}
      </div>
    </div>
  )
}
