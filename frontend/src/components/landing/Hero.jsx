import { LogoMark } from '../Logo'
import Button from '../ui/Button'
import Icon from '../ui/Icon'
import { heroPerks } from '../../data/mock'

/** Faint scrolling binary columns layered over the hero photo. */
function BinaryRain() {
  const cols = [
    { left: '6%', top: '8%', delay: '0s', text: '010101' },
    { left: '18%', top: '26%', delay: '.6s', text: '010101' },
    { left: '3%', top: '44%', delay: '1.2s', text: '010101' },
    { left: '26%', top: '58%', delay: '.3s', text: '010101' },
    { left: '11%', top: '74%', delay: '.9s', text: '010101' },
    { left: '68%', top: '14%', delay: '.45s', text: '010101' },
    { left: '84%', top: '36%', delay: '1.4s', text: '01011' },
    { left: '73%', top: '66%', delay: '.15s', text: '010101' },
    { left: '90%', top: '80%', delay: '1s', text: '01010' },
  ]
  return (
    <div aria-hidden className="pointer-events-none absolute inset-0 hidden overflow-hidden sm:block">
      {cols.map((c, i) => (
        <span
          key={i}
          className="absolute animate-pulse-glow font-mono text-[11px] font-medium tracking-[0.2em] text-brand-500/45 sm:text-[13px]"
          style={{ left: c.left, top: c.top, animationDelay: c.delay }}
        >
          {c.text}
        </span>
      ))}
    </div>
  )
}

export default function Hero() {
  return (
    <section className="relative isolate overflow-hidden bg-root-950">
      {/* Background photo — anchored right, dissolving into the dark on the left */}
      <div className="absolute inset-0">
        <img
          src="/hero-medina.jpg"
          alt=""
          aria-hidden
          className="h-full w-full object-cover object-[70%_center] opacity-[0.85]"
        />
        {/* Left-to-right darkening so the copy always sits on near-black */}
        <div className="absolute inset-0 bg-gradient-to-r from-root-950 via-root-950/95 to-root-950/5 lg:from-root-950 lg:via-root-950/60 lg:to-transparent" />
        <div
          aria-hidden
          className="absolute inset-0 hidden lg:block"
          style={{
            background:
              'linear-gradient(90deg, #04090E 0%, #04090E 26%, rgba(4,9,14,.92) 36%, rgba(4,9,14,.45) 50%, rgba(4,9,14,.15) 66%, rgba(4,9,14,.35) 100%)',
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-root-950 via-transparent to-root-950/70" />
        <div className="absolute inset-0 bg-root-950/55 lg:bg-transparent" />
      </div>

      <BinaryRain />

      {/* Glowing brand mark, centred over the alley like the reference */}
      <div
        aria-hidden
        className="pointer-events-none absolute right-[6%] top-1/2 hidden -translate-y-1/2 lg:block xl:right-[16%]"
      >
        <div className="relative">
          <div className="absolute inset-0 -z-10 scale-150 rounded-full bg-brand-500/20 blur-[70px]" />
          <LogoMark size={230} className="drop-shadow-[0_0_28px_rgba(248,133,31,.75)]" />
        </div>
      </div>

      <div className="container-page relative py-20 sm:py-24 lg:py-[104px]">
        <div className="max-w-xl lg:max-w-[760px]">
          {/* Eyebrow pill */}
          <span className="inline-flex items-center gap-2 rounded-full border border-brand-500/40 bg-brand-500/[0.07] px-3 py-1.5 text-[9.5px] font-bold uppercase tracking-[0.11em] text-brand-400 backdrop-blur-sm sm:px-3.5 sm:text-[10.5px] sm:tracking-[0.13em]">
            <Icon name="Code2" size={12} />
            Built for coders, powered by community.
          </span>

          <h1 className="mt-6 text-[32px] font-extrabold leading-[1.1] tracking-[-0.02em] text-white sm:text-[42px] lg:text-[46px] xl:text-[52px]">
            Apprends. Code. Collabore.
            <br />
            <span className="text-brand-500">Deviens Meilleur.</span>
          </h1>

          {/* Arabic subtitle — RTL script, left-aligned block like the mockup */}
          <p
            dir="rtl"
            lang="ar"
            className="font-ar mt-6 max-w-[520px] text-left text-[13.5px] leading-[2.05] text-ink-soft sm:text-[14.5px]"
          >
            منصة تعليمية وتنافسية متكاملة مستوحاة من فلسفة 42، مصمّمة خصيصًا لطلاب ومبرمجي تونس
          </p>

          <div className="mt-8 flex flex-wrap items-center gap-3">
            <Button to="/register" size="lg" iconRight="ArrowRight">
              Commencer maintenant
            </Button>
            <Button to="/parcours" variant="outline" size="lg" iconRight="Play">
              Découvrir la plateforme
            </Button>
          </div>

          {/* Perks row */}
          <ul className="mt-9 flex flex-wrap items-center gap-x-1 gap-y-3 text-[12px] text-ink-soft">
            {heroPerks.map((p, i) => (
              <li key={p.label} className="flex items-center">
                <span className="flex items-center gap-2 pr-3">
                  <Icon name={p.icon} size={14} className="text-brand-500" />
                  {p.label}
                </span>
                {i < heroPerks.length - 1 && (
                  <span className="pr-3 text-ink-faint" aria-hidden>•</span>
                )}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  )
}
