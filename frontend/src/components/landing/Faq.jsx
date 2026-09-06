import { useState } from 'react'
import Icon from '../ui/Icon'
import SectionHeading from '../ui/SectionHeading'
import { faqs } from '../../data/mock'

export default function Faq() {
  const [open, setOpen] = useState(0)

  return (
    <section className="border-t border-line bg-root-900 py-20 sm:py-24">
      <div className="container-page grid gap-12 lg:grid-cols-[0.85fr_1.15fr] lg:gap-16">
        <SectionHeading
          align="left"
          eyebrow="FAQ"
          title="Les questions"
          highlight="qui reviennent"
          text="Une réponse manque ? Le salon #général du Discord répond en général en moins de dix minutes."
        />

        <div className="divide-y divide-line overflow-hidden rounded-xl border border-line bg-root-800">
          {faqs.map((f, i) => {
            const on = open === i
            return (
              <div key={f.q}>
                <button
                  onClick={() => setOpen(on ? -1 : i)}
                  aria-expanded={on}
                  className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left transition-colors hover:bg-white/[0.02]"
                >
                  <span className={`text-[13.5px] font-semibold ${on ? 'text-brand-500' : 'text-ink'}`}>
                    {f.q}
                  </span>
                  <Icon
                    name="Plus"
                    size={17}
                    className={`shrink-0 transition-transform duration-300 ${
                      on ? 'rotate-45 text-brand-500' : 'text-ink-dim'
                    }`}
                  />
                </button>
                <div
                  className={`grid transition-all duration-300 ${
                    on ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'
                  }`}
                >
                  <div className="overflow-hidden">
                    <p className="px-5 pb-5 text-[13px] leading-relaxed text-ink-dim">{f.a}</p>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
