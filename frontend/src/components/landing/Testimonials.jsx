import Avatar from '../ui/Avatar'
import Icon from '../ui/Icon'
import SectionHeading from '../ui/SectionHeading'
import { testimonials } from '../../data/mock'

export default function Testimonials() {
  return (
    <section className="border-t border-line bg-root-950 py-20 sm:py-24">
      <div className="container-page">
        <SectionHeading
          eyebrow="Communauté"
          title="Ils sont passés par"
          highlight="la Piscine"
          text="12 487 codeurs actifs, 42 coalitions, trois campus. Voici ce qu'ils en disent."
        />

        <div className="mt-14 grid gap-5 md:grid-cols-3">
          {testimonials.map((t) => (
            <figure
              key={t.name}
              className="card relative flex flex-col p-6 transition-all duration-300 hover:-translate-y-1 hover:border-brand-500/25"
            >
              <Icon name="Quote" size={26} className="text-brand-500/25" />
              <blockquote className="mt-3 flex-1 text-[13.5px] leading-relaxed text-ink-soft">
                {t.text}
              </blockquote>
              <figcaption className="mt-6 flex items-center gap-3 border-t border-line pt-5">
                <Avatar src={t.avatar} name={t.name} size="md" />
                <div>
                  <p className="text-[13px] font-semibold text-white">{t.name}</p>
                  <p className="text-[11.5px] text-ink-dim">{t.role}</p>
                </div>
              </figcaption>
            </figure>
          ))}
        </div>
      </div>
    </section>
  )
}
