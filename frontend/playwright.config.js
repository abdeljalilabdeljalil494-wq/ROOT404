import { defineConfig } from '@playwright/test'
import chromium, { inflate } from '@sparticuz/chromium'
const linux = process.platform === 'linux'
const libs = linux ? await inflate(new URL('./node_modules/@sparticuz/chromium/bin/al2023.tar.br', import.meta.url).pathname) : ''
const executablePath = process.env.ROOT404_CHROMIUM_EXECUTABLE || (linux ? await chromium.executablePath() : undefined)
const python = process.env.ROOT404_TEST_PYTHON || '../.cache/verification-venv/bin/python'
export default defineConfig({
  testDir: './e2e', fullyParallel: false, workers: 1, retries: 0,
  timeout: 60000,
  reporter: [['list'], ['json', { outputFile: '../.cache/browser-results/results.json' }]],
  outputDir: '../.cache/browser-results/artifacts',
  use: { baseURL: 'http://127.0.0.1:5181', headless: true,
    screenshot: 'only-on-failure', trace: 'retain-on-failure',
    launchOptions: { executablePath, args: ['--no-sandbox', '--disable-dev-shm-usage', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'], env: linux ? { ...process.env, LD_LIBRARY_PATH: `${libs}/lib:/tmp:${process.env.LD_LIBRARY_PATH || ''}` } : { ...process.env } } },
  projects: [
    { name: 'desktop', use: { viewport: { width: 1440, height: 1000 } } },
    { name: 'tablet', use: { viewport: { width: 820, height: 1180 } } },
    { name: 'mobile', use: { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true } },
  ],
  webServer: [
    { command: `${python} ../scripts/browser_server.py`, url: 'http://127.0.0.1:8011/health', reuseExistingServer: false, timeout: 30000 },
    { command: 'npm run dev -- --port 5181', url: 'http://127.0.0.1:5181/login', reuseExistingServer: false,
      env: { VITE_API_TARGET: 'http://127.0.0.1:8011', VITE_USE_MOCK: 'false' }, timeout: 30000 },
  ],
})
