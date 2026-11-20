// Importing Node config directly never reads a developer .env file.
// The child checks the real process.env proxy contract before config import.
// This is a config test, not a claim about production Nginx routing.
import process from 'node:process'
import { execFileSync } from 'node:child_process'
import { expect, it } from 'vitest'

it('uses an explicitly exported server proxy target', () => {
  const result = execFileSync(process.execPath, ['--input-type=module', '-e',
    "const {default: c}=await import('./vite.config.js'); console.log(c.server.proxy['/api'].target)"], {
    cwd: process.cwd(), env: { ...process.env, VITE_API_TARGET: 'http://backend.example:8001' }, encoding: 'utf8',
  })
  expect(result.trim()).toBe('http://backend.example:8001')
})
