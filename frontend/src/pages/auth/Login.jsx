import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import AuthLayout from './AuthLayout'
import Button from '../../components/ui/Button'
import Icon from '../../components/ui/Icon'
import { authService, setAuthUser } from '../../services/api'

export default function Login() {
  const navigate = useNavigate()
  const [step, setStep] = useState('email')
  const [email, setEmail] = useState('')
  const [code, setCode] = useState(['', '', '', '', '', ''])
  const [loading, setLoading] = useState(false)
  const [seconds, setSeconds] = useState(60)
  const [devCode, setDevCode] = useState(null)
  const [error, setError] = useState(null)
  const refs = useRef([])

  useEffect(() => { document.title = 'Se connecter — ROOT 404' }, [])

  useEffect(() => {
    if (step !== 'otp') return
    refs.current[0]?.focus()
    const id = setInterval(() => setSeconds((s) => (s > 0 ? s - 1 : 0)), 1000)
    return () => clearInterval(id)
  }, [step])

  const sendOtp = async (e) => {
    e.preventDefault()
    if (!email) return
    setLoading(true)
    setError(null)
    try {
      const res = await authService.requestOtp(email)
      setDevCode(res?.dev_code || null)
      setLoading(false)
      setStep('otp')
      setSeconds(60)
    } catch (err) {
      // Backend online but rejected (e.g. 429 resend rate limit).
      setLoading(false)
      setError(err.response?.data?.detail || "Impossible d'envoyer le code — réessaie.")
    }
  }

  const onDigit = (i, v) => {
    const d = v.replace(/\D/g, '').slice(-1)
    setCode((c) => c.map((x, j) => (j === i ? d : x)))
    if (d && i < 5) refs.current[i + 1]?.focus()
  }

  const onKey = (i, e) => {
    if (e.key === 'Backspace' && !code[i] && i > 0) refs.current[i - 1]?.focus()
  }

  const fillDevCode = () => {
    if (!devCode) return
    setCode(devCode.split(''))
    refs.current[5]?.focus()
  }

  const verify = async (e) => {
    e.preventDefault()
    const full = code.join('')
    if (full.length !== 6) return
    setLoading(true)
    setError(null)
    try {
      const res = await authService.verifyOtp(email, full)
      if (res?.token) localStorage.setItem('root404_token', res.token)
      if (res?.user) setAuthUser(res.user)
      navigate('/dashboard')
    } catch (err) {
      if (err.response) {
        // Backend online: surface the real error (bad/expired code, …).
        setError(err.response.data?.detail || 'Code incorrect — réessaie.')
      } else {
        // Backend offline → demo session (mock contract) so the app stays usable.
        localStorage.setItem('root404_token', 'mock.jwt.token')
        navigate('/dashboard')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthLayout
      title={step === 'email' ? 'Content de te revoir' : 'Vérifie ton e-mail'}
      subtitle={
        step === 'email'
          ? 'Entre ton adresse e-mail — nous t’envoyons un code à usage unique. Pas de mot de passe à retenir.'
          : `Nous avons envoyé un code à 6 chiffres à ${email}. Il expire dans 10 minutes.`
      }
      footer={
        <>
          Pas encore de compte ?{' '}
          <Link to="/register" className="font-semibold text-brand-500 hover:underline">
            Postuler à la Piscine
          </Link>
        </>
      }
    >
      {step === 'email' ? (
        <form onSubmit={sendOtp} className="space-y-4">
          <div>
            <label htmlFor="email" className="mb-1.5 block text-[12.5px] font-semibold text-ink">
              Adresse e-mail
            </label>
            <div className="relative">
              <Icon name="Mail" size={15} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-ink-faint" />
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="ton.nom@exemple.tn"
                className="input h-11 pl-9"
              />
            </div>
          </div>

          <Button type="submit" size="lg" full loading={loading} iconRight="ArrowRight">
            Recevoir mon code
          </Button>

          <div className="flex items-center gap-3 py-1">
            <span className="h-px flex-1 bg-line" />
            <span className="text-[11px] uppercase tracking-wider text-ink-faint">ou</span>
            <span className="h-px flex-1 bg-line" />
          </div>

          <div className="grid gap-2.5 sm:grid-cols-2">
            <Button variant="outline" size="lg" icon="Github">GitHub</Button>
            <Button variant="outline" size="lg" icon="MessageCircle">Discord</Button>
          </div>

          <p className="flex items-start gap-2 pt-2 text-[11.5px] leading-relaxed text-ink-faint">
            <Icon name="ShieldCheck" size={13} className="mt-0.5 shrink-0 text-ok" />
            Authentification par OTP + JWT. Nous ne stockons aucun mot de passe.
          </p>
        </form>
      ) : (
        <form onSubmit={verify} className="space-y-5">
          {error && (
            <p className="flex items-start gap-2 rounded-lg border border-danger/30 bg-danger/[0.08] p-3 text-[12px] leading-relaxed text-danger">
              <Icon name="AlertTriangle" size={14} className="mt-0.5 shrink-0" /> {error}
            </p>
          )}
          {devCode && (
            <div className="flex items-center justify-between gap-3 rounded-lg border border-info/25 bg-info/[0.06] p-3">
              <p className="text-[11.5px] leading-relaxed text-ink-dim">
                <span className="font-semibold text-info">Mode dev</span> — pas d'e-mail envoyé.
                Ton code est <span className="font-mono text-[13px] font-bold tracking-widest text-ink">{devCode}</span>
              </p>
              <Button type="button" variant="outline" size="sm" onClick={fillDevCode}>
                Remplir
              </Button>
            </div>
          )}
          <div>
            <label className="mb-2.5 block text-[12.5px] font-semibold text-ink">Code de vérification</label>
            <div className="flex gap-2">
              {code.map((d, i) => (
                <input
                  key={i}
                  ref={(el) => (refs.current[i] = el)}
                  value={d}
                  onChange={(e) => onDigit(i, e.target.value)}
                  onKeyDown={(e) => onKey(i, e)}
                  inputMode="numeric"
                  maxLength={1}
                  aria-label={`Chiffre ${i + 1}`}
                  className="h-13 h-[52px] w-full rounded-lg border border-line bg-root-850 text-center font-mono text-[20px] font-bold text-ink focus:border-brand-500 focus:outline-none"
                />
              ))}
            </div>
          </div>

          <Button type="submit" size="lg" full loading={loading} iconRight="ArrowRight">
            Se connecter
          </Button>

          <div className="flex items-center justify-between text-[12px]">
            <button type="button" onClick={() => setStep('email')} className="flex items-center gap-1.5 text-ink-dim hover:text-ink">
              <Icon name="ArrowLeft" size={13} /> Changer d'e-mail
            </button>
            <button
              type="button"
              disabled={seconds > 0}
              onClick={() => setSeconds(60)}
              className="font-medium text-brand-500 disabled:text-ink-faint"
            >
              {seconds > 0 ? `Renvoyer dans ${seconds}s` : 'Renvoyer le code'}
            </button>
          </div>
        </form>
      )}
    </AuthLayout>
  )
}
