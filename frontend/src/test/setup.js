import '@testing-library/jest-dom/vitest'
import { afterEach } from 'vitest'

// jsdom does not implement scrolling
window.scrollTo = () => {}

afterEach(() => {
  localStorage.clear()
})
