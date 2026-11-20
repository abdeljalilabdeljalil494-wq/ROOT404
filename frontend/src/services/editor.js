// Self-host Monaco and its worker: no CDN request or third-party source disclosure.
import { loader } from '@monaco-editor/react'
import * as monaco from 'monaco-editor/editor/editor.api.js'
import EditorWorker from 'monaco-editor/editor/editor.worker.js?worker'
import 'monaco-editor/languages/definitions/cpp/register.js'
import 'monaco-editor/languages/definitions/python/register.js'
import 'monaco-editor/languages/definitions/javascript/register.js'

self.MonacoEnvironment = { getWorker: () => new EditorWorker() }
loader.config({ monaco })
