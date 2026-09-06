import Icon from '../ui/Icon'
import { heroFeatures, heroStats } from '../../data/mock'

/**
 * The two bordered bands sitting directly under the hero:
 * 5 feature tiles, then the 5-up stats strip with vertical dividers.
 */
export default function FeatureStrip() {
  return (
    <section className="relative z-10 bg-root-950 pb-14">
      <div className="container-page -mt-6 space-y-4 sm:-mt-8">
        {/* Feature tiles */}
        <div className="rounded-2xl border border-line bg-root-950/70 p-3 backdrop-blur-md sm:p-4">
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-5">
            {heroFeatures.map((f) => (
              <article
                key={f.title}
                className="group rounded-xl border border-line bg-root-800/80 px-4 py-6 text-center transition-all duration-300 hover:-translate-y-0.5 hover:border-brand-500/35 hover:bg-root-800"
              >
                <span className="mx-auto grid h-11 w-11 place-items-center rounded-lg text-brand-500 transition-transform duration-300 group-hover:scale-110">
                  <Icon name={f.icon} size={26} strokeWidth={1.6} />
                </span>
                <h3 className="mt-3 text-[13px] font-bold text-white">{f.title}</h3>
                <p className="mx-auto mt-2 max-w-[210px] text-[11.5px] leading-relaxed text-ink-dim">
                  {f.text}
                </p>
              </article>
            ))}
          </div>
        </div>

        {/* Stats strip */}
        <div className="rounded-2xl border border-line bg-root-850 px-2 py-6 sm:px-4">
          <dl className="grid grid-cols-2 gap-y-7 sm:grid-cols-3 lg:grid-cols-5">
            {heroStats.map((s, i) => (
              <div
                key={s.label}
                className={`flex flex-col items-center px-3 text-center ${
                  i > 0 ? 'lg:border-l lg:border-line' : ''
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <Icon name={s.icon} size={21} className="text-brand-500" strokeWidth={1.7} />
                  <dd className="text-[22px] font-extrabold tracking-tight text-brand-500 sm:text-[25px]">
                    {s.value}
                  </dd>
                </div>
                <dt className="mt-1.5 text-[11.5px] text-ink-dim">{s.label}</dt>
              </div>
            ))}
          </dl>
        </div>
      </div>
    </section>
  )
}
