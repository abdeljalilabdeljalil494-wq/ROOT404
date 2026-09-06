import { Link } from 'react-router-dom'
import Icon from '../ui/Icon'
import SectionHeading from '../ui/SectionHeading'
import { pathways } from '../../data/mock'

export default function Pathways() {
  return (
    <section className="border-t border-line bg-root-950 py-20 sm:py-24">
      <div className="container-page">
        <div className="flex flex-col items-start justify-between gap-6 md:flex-row md:items-end">
          <SectionHeading
            align="left"
            eyebrow="Parcours"
            title="Six routes,"
            highlight="un seul niveau"
            text="Le tronc commun d'abord, puis une spécialisation recommandée par l'Adaptive Path Engine selon ton Skill Graph."
          />
          <Link
            to="/parcours"
            className="group inline-flex shrink-0 items-center gap-2 text-[13px] font-semibold text-brand-500 hover:underline"
          >
            Voir tous les parcours
            <Icon name="ArrowRight" size={15} className="transition-transform group-hover:translate-x-0.5" />
          </Link>
        </div>

        <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {pathways.map((p) => (
            <article
              key={p.name}
              className="card group relative overflow-hidden p-5 transition-all duration-300 hover:-translate-y-1 hover:border-line-strong"
            >
              <div
                aria-hidden
                className="absolute -right-16 -top-16 h-40 w-40 rounded-full opacity-0 blur-3xl transition-opacity duration-500 group-hover:opacity-25"
                style={{ background: p.color }}
              />
              <div className="relative">
                <span
                  className="grid h-11 w-11 place-items-center rounded-lg"
                  style={{ background: `${p.color}18`, color: p.color }}
                >
                  <Icon name={p.icon} size={21} />
                </span>
                <h3 className="mt-4 text-[15px] font-bold text-white">{p.name}</h3>
                <p className="mt-1 font-mono text-[11px] font-semibold" style={{ color: p.color }}>
                  {p.level}
                </p>
                <p className="mt-3 text-[12.5px] leading-relaxed text-ink-dim">{p.desc}</p>
                <div className="mt-5 flex items-center gap-4 border-t border-line pt-4 text-[11.5px] text-ink-soft">
                  <span className="flex items-center gap-1.5">
                    <Icon name="FolderKanban" size={13} className="text-ink-faint" /> {p.projects} projets
                  </span>
                  <span className="flex items-center gap-1.5">
                    <Icon name="Clock" size={13} className="text-ink-faint" /> {p.weeks} semaines
                  </span>
                </div>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  )
}
