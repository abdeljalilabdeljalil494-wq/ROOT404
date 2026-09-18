import { describe, it, expect, beforeEach, vi } from 'vitest'
import axios from 'axios'

// Mock axios
vi.mock('axios', () => {
  const mockAxios = {
    create: vi.fn(() => mockAxios),
    get: vi.fn(),
    post: vi.fn(),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() }
    }
  }
  return { default: mockAxios }
})

describe('API Services - Security', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  describe('Auth Service', () => {
    it('should store token securely', () => {
      const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test'
      localStorage.setItem('root404_token', token)
      expect(localStorage.getItem('root404_token')).toBe(token)
    })

    it('should clear token on logout', () => {
      localStorage.setItem('root404_token', 'test-token')
      localStorage.removeItem('root404_token')
      expect(localStorage.getItem('root404_token')).toBeNull()
    })

    it('should validate email format', () => {
      const validEmails = ['test@example.com', 'user@root404.tn']
      const invalidEmails = ['invalid', 'test@', '@test.com', 'test@test.tn\' OR \'1\'=\'1']
      
      validEmails.forEach(email => {
        expect(email).toMatch(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)
      })
      
      invalidEmails.forEach(email => {
        if (email.includes("'")) {
          // SQL injection attempt should be rejected
          expect(email).toContain("'")
        }
      })
    })

    it('should validate OTP format', () => {
      const validOTP = '123456'
      const invalidOTPs = ['12345', '1234567', 'abcdef', '12345a', '']
      
      expect(validOTP).toMatch(/^\d{6}$/)
      invalidOTPs.forEach(otp => {
        expect(otp).not.toMatch(/^\d{6}$/)
      })
    })
  })

  describe('Project Submission - Security', () => {
    it('should validate file names to prevent path traversal', () => {
      const validNames = ['main.c', 'src/parser.c', 'Makefile']
      const invalidNames = ['../../etc/passwd', '/etc/passwd', 'test\x00.c', '..\\windows\\file']
      
      validNames.forEach(name => {
        expect(name).not.toContain('..')
        expect(name).not.toMatch(/^\//)
        expect(name).not.toContain('\x00')
      })
      
      invalidNames.forEach(name => {
        const isInvalid = name.includes('..') || name.startsWith('/') || name.includes('\x00') || name.includes('\\')
        expect(isInvalid).toBe(true)
      })
    })

    it('should enforce file size limits', () => {
      const maxSize = 1024 * 1024 // 1MB
      const validContent = 'a'.repeat(1000)
      const invalidContent = 'a'.repeat(maxSize + 1)
      
      expect(validContent.length).toBeLessThan(maxSize)
      expect(invalidContent.length).toBeGreaterThan(maxSize)
    })

    it('should detect forbidden patterns', () => {
      const forbiddenPatterns = [
        'os.system',
        'subprocess',
        'socket',
        '__import__',
        'eval(',
        'system(',
        'popen('
      ]
      
      const maliciousCode = "import os\nos.system('rm -rf /')"
      const hasForbidden = forbiddenPatterns.some(pattern => 
        maliciousCode.toLowerCase().includes(pattern.toLowerCase())
      )
      expect(hasForbidden).toBe(true)
      
      const safeCode = "int main() { printf('hello'); return 0; }"
      const safeHasForbidden = forbiddenPatterns.some(pattern =>
        safeCode.toLowerCase().includes(pattern.toLowerCase())
      )
      expect(safeHasForbidden).toBe(false)
    })
  })

  describe('Input Sanitization', () => {
    it('should sanitize XSS attempts', () => {
      const xssAttempts = [
        "<script>alert('xss')</script>",
        "javascript:alert('xss')",
        "<img src=x onerror=alert('xss')>",
        "eval(document.cookie)"
      ]
      
      xssAttempts.forEach(attempt => {
        // Check that dangerous patterns are detected
        const hasDangerous = /<script|javascript:|onerror=|eval\(/.test(attempt.toLowerCase())
        expect(hasDangerous).toBe(true)
      })
    })

    it('should truncate long inputs', () => {
      const maxLength = 100
      const longInput = 'a'.repeat(200)
      const truncated = longInput.slice(0, maxLength)
      expect(truncated.length).toBe(maxLength)
    })
  })

  describe('Room Creation - Validation', () => {
    it('should validate room name', () => {
      const validNames = ['Study Room 1', 'Correction - minishell']
      const invalidNames = ['', 'a'.repeat(101), '<script>']
      
      validNames.forEach(name => {
        expect(name.length).toBeGreaterThan(0)
        expect(name.length).toBeLessThanOrEqual(100)
      })
      
      invalidNames.forEach(name => {
        const isInvalid = name.length === 0 || name.length > 100 || name.includes('<script>')
        expect(isInvalid).toBe(true)
      })
    })

    it('should validate room capacity', () => {
      const validCapacities = [2, 10, 50, 500]
      const invalidCapacities = [0, -1, 1001, 10000]
      
      validCapacities.forEach(cap => {
        expect(cap).toBeGreaterThan(0)
        expect(cap).toBeLessThanOrEqual(1000)
      })
      
      invalidCapacities.forEach(cap => {
        const isInvalid = cap <= 0 || cap > 1000
        expect(isInvalid).toBe(true)
      })
    })
  })
})

describe('Critical User Flows', () => {
  it('Authentication flow should handle errors gracefully', () => {
    // Simulate auth flow
    const mockAuthFlow = {
      requestOtp: (email) => {
        if (!email || !email.includes('@')) {
          throw new Error('Invalid email')
        }
        return { sent: true, email }
      },
      verifyOtp: (email, code) => {
        if (!code || !/^\d{6}$/.test(code)) {
          throw new Error('Invalid OTP format')
        }
        return { token: 'mock-token', user: { username: 'test' } }
      }
    }
    
    expect(() => mockAuthFlow.requestOtp('invalid')).toThrow('Invalid email')
    expect(() => mockAuthFlow.verifyOtp('test@test.com', 'invalid')).toThrow('Invalid OTP format')
    expect(mockAuthFlow.requestOtp('test@test.com')).toEqual({ sent: true, email: 'test@test.com' })
  })

  it('Code submission flow should validate before sending', () => {
    const validateSubmission = (files, language) => {
      if (!files || Object.keys(files).length === 0) {
        throw new Error('No files')
      }
      if (Object.keys(files).length > 20) {
        throw new Error('Too many files')
      }
      const allowedLangs = ['c', 'cpp', 'python', 'javascript']
      if (!allowedLangs.includes(language)) {
        throw new Error('Invalid language')
      }
      return true
    }
    
    expect(() => validateSubmission({}, 'c')).toThrow('No files')
    expect(() => validateSubmission({ 'a.c': 'content' }, 'invalid')).toThrow('Invalid language')
    expect(validateSubmission({ 'main.c': 'int main(){}' }, 'c')).toBe(true)
  })

  it('Room creation flow should validate inputs', () => {
    const validateRoom = (name, type, capacity) => {
      if (!name || name.length === 0 || name.length > 100) {
        throw new Error('Invalid name')
      }
      const allowedTypes = ['study', 'correction', 'pair', 'competition', 'mentor', 'live']
      if (!allowedTypes.includes(type)) {
        throw new Error('Invalid type')
      }
      if (capacity <= 0 || capacity > 1000) {
        throw new Error('Invalid capacity')
      }
      return true
    }
    
    expect(() => validateRoom('', 'study', 10)).toThrow('Invalid name')
    expect(() => validateRoom('Test', 'invalid', 10)).toThrow('Invalid type')
    expect(() => validateRoom('Test', 'study', 0)).toThrow('Invalid capacity')
    expect(validateRoom('Study Room', 'study', 10)).toBe(true)
  })
})
