import Icon from '../ui/Icon'
import SectionHeading from '../ui/SectionHeading'
import { howItWorks } from '../../data/mock'

export default function HowItWorks() {
  return (
    <section className="border-t border-line bg-root-900 py-20 sm:py-24">
      <div className="container-page">
        <SectionHeading
          eyebrow="Le cycle"
          title="Du sujet au"
          highlight="niveau supérieur"
          text="Chaque projet suit le même Project Lifecycle Engine : rien n'est validé sans passer la Moulinette, le peer review et l'analyse IA."
        />

        <div className="relative mt-14">
          {/* connector line on desktop */}
          <div
            aria-hidden
            className="absolute inset-x-0 top-[38px] hidden h-px bg-gradient-to-r from-transparent via-line-strong to-transparent lg:block"
          />
          <ol className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
            {howItWorks.map((s) => (
              <li key={s.step} className="relative">
                <div className="flex flex-col items-center text-center">
                  <span className="relative grid h-[76px] w-[76px] place-items-center rounded-2xl border border-line bg-root-800 text-brand-500 transition-all duration-300 hover:border-brand-500/40 hover:shadow-glow">
                    <Icon name={s.icon} size={26} strokeWidth={1.6} />
                    <span className="absolute -right-1.5 -top-1.5 grid h-6 w-6 place-items-center rounded-full bg-brand-500 font-mono text-[10px] font-bold text-[#160A00]">
                      {s.step}
                    </span>
                  </span>
                  <h3 className="mt-4 text-[13.5px] font-bold text-white">{s.title}</h3>
                  <p className="mt-1.5 text-[12px] leading-relaxed text-ink-dim">{s.text}</p>
                </div>
              </li>
            ))}
          </ol>
        </div>
      </div>
    </section>
  )
}
