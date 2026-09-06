import Button from '../ui/Button'
import Icon from '../ui/Icon'
import { LogoMark } from '../Logo'

export default function CtaBanner() {
  return (
    <section className="border-t border-line bg-root-950 py-20 sm:py-24">
      <div className="container-page">
        <div className="relative isolate overflow-hidden rounded-2xl border border-brand-500/25 bg-gradient-to-br from-brand-500/[0.13] via-root-850 to-root-950 px-6 py-14 text-center sm:px-12">
          <div aria-hidden className="absolute inset-0 -z-10 bg-grid opacity-40" />
          <div
            aria-hidden
            className="absolute left-1/2 top-0 -z-10 h-64 w-64 -translate-x-1/2 -translate-y-1/2 rounded-full bg-brand-500/25 blur-[90px]"
          />

          <LogoMark size={54} className="mx-auto drop-shadow-[0_0_18px_rgba(248,133,31,.6)]" />

          <h2 className="mt-6 text-[26px] font-extrabold leading-tight tracking-tight text-white sm:text-[36px]">
            La prochaine Piscine ouvre en <span className="text-brand-500">octobre 2026</span>
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-[14px] leading-relaxed text-ink-soft">
            Quatre semaines, aucun prérequis, aucun frais. Il ne reste que la volonté d'apprendre —
            et un peu de résistance au manque de sommeil.
          </p>

          <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
            <Button to="/register" size="lg" iconRight="ArrowRight">Postuler à la Piscine</Button>
            <Button to="/piscine" variant="outline" size="lg" icon="Waves">Comment ça marche</Button>
          </div>

          <p className="mt-6 flex items-center justify-center gap-2 text-[11.5px] text-ink-dim">
            <Icon name="ShieldCheck" size={13} className="text-ok" />
            Sans carte bancaire · Sans engagement · 100 % gratuit
          </p>
        </div>
      </div>
    </section>
  )
}
