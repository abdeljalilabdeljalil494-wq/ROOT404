import { useEffect, useState } from 'react'
import Icon from '../components/ui/Icon'
import Badge from '../components/ui/Badge'
import Button from '../components/ui/Button'
import SectionHeading from '../components/ui/SectionHeading'
import { blogPosts } from '../data/mock'

const CATS = ['Tous', 'Pédagogie', 'Ingénierie', 'Produit', 'Communauté']

const MORE = [
  { id: 4, title: 'Ce que 4 000 peer reviews nous ont appris', cat: 'Communauté', date: '09 juillet 2026', read: '7 min', excerpt: 'Les corrections les plus sévères viennent des étudiants, pas des machines. Analyse de nos données.' },
  { id: 5, title: 'Sandboxer du code hostile sans y laisser sa peau', cat: 'Ingénierie', date: '28 juin 2026', read: '13 min', excerpt: 'seccomp, cgroups, réseau coupé : la recette complète de notre runner isolé.' },
  { id: 6, title: 'Black Hole : pourquoi la pression fonctionne', cat: 'Pédagogie', date: '14 juin 2026', read: '9 min', excerpt: 'Une contrainte de temps bien calibrée multiplie par 2,3 le taux de complétion. Voici comment nous l’avons réglée.' },
]

export default function Blog() {
  useEffect(() => { document.title = 'Blog — ROOT 404' }, [])
  const [cat, setCat] = useState('Tous')
  const all = [...blogPosts, ...MORE]
  const list = cat === 'Tous' ? all : all.filter((p) => p.cat === cat)
  const [featured, ...rest] = list

  return (
    <>
      <section className="border-b border-line bg-root-950 py-16">
        <div className="container-page">
          <SectionHeading align="left" eyebrow="Blog" title="Notes de la salle" highlight="machine" text="Pédagogie, ingénierie et coulisses de la plateforme, écrites par l'équipe et la communauté." />
          <div className="no-scrollbar mt-8 flex gap-2 overflow-x-auto">
            {CATS.map((c) => (
              <button
                key={c}
                onClick={() => setCat(c)}
                className={`shrink-0 rounded-lg border px-3.5 py-2 text-[12.5px] font-semibold transition-colors ${
                  cat === c ? 'border-brand-500/50 bg-brand-500/12 text-brand-500' : 'border-line text-ink-dim hover:text-ink'
                }`}
              >
                {c}
              </button>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-root-900 py-16">
        <div className="container-page space-y-10">
          {featured && (
            <article className="card group grid overflow-hidden lg:grid-cols-2">
              <div
                className="relative min-h-[220px] bg-root-850"
                style={{ background: featured.img || 'linear-gradient(135deg,#F8851F22,#04090E)' }}
              >
                <div aria-hidden className="absolute inset-0 bg-grid opacity-40" />
                <span className="absolute left-5 top-5"><Badge tone="brand">À la une</Badge></span>
                <Icon name="Newspaper" size={44} className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-brand-500/40" />
              </div>
              <div className="flex flex-col justify-center p-7">
                <div className="flex items-center gap-3 text-[11.5px] text-ink-dim">
                  <Badge tone="muted">{featured.cat}</Badge>
                  <span>{featured.date}</span>
                  <span className="flex items-center gap-1"><Icon name="Clock" size={11} /> {featured.read}</span>
                </div>
                <h2 className="mt-3.5 text-[22px] font-extrabold leading-tight tracking-tight text-white transition-colors group-hover:text-brand-500">
                  {featured.title}
                </h2>
                <p className="mt-3 text-[13.5px] leading-relaxed text-ink-dim">{featured.excerpt}</p>
                <div className="mt-6">
                  <Button variant="outline" size="sm" iconRight="ArrowRight">Lire l'article</Button>
                </div>
              </div>
            </article>
          )}

          <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
            {rest.map((p) => (
              <article key={p.id} className="card group flex flex-col overflow-hidden transition-all hover:-translate-y-1 hover:border-brand-500/25">
                <div
                  className="relative h-36"
                  style={{ background: p.img || 'linear-gradient(135deg,#3B9EFF1A,#04090E)' }}
                >
                  <div aria-hidden className="absolute inset-0 bg-grid opacity-40" />
                  <Icon name="FileText" size={26} className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-white/20" />
                </div>
                <div className="flex flex-1 flex-col p-5">
                  <div className="flex items-center gap-2.5 text-[11px] text-ink-dim">
                    <Badge tone="muted">{p.cat}</Badge>
                    <span>{p.date}</span>
                  </div>
                  <h3 className="mt-3 text-[15px] font-bold leading-snug text-white transition-colors group-hover:text-brand-500">
                    {p.title}
                  </h3>
                  <p className="mt-2 line-clamp-3 flex-1 text-[12.5px] leading-relaxed text-ink-dim">{p.excerpt}</p>
                  <div className="mt-4 flex items-center justify-between border-t border-line pt-3.5 text-[11.5px] text-ink-dim">
                    <span className="flex items-center gap-1.5"><Icon name="Clock" size={11} /> {p.read}</span>
                    <span className="flex items-center gap-1 font-medium text-brand-500">
                      Lire <Icon name="ArrowRight" size={12} />
                    </span>
                  </div>
                </div>
              </article>
            ))}
          </div>

          {/* Newsletter */}
          <div className="card flex flex-col items-center gap-5 p-8 text-center sm:flex-row sm:justify-between sm:text-left">
            <div>
              <h3 className="text-[16px] font-bold text-white">Une note technique par mois</h3>
              <p className="mt-1.5 text-[13px] text-ink-dim">
                Pas de spam, pas de growth hacking. Juste ce que nous cassons et réparons.
              </p>
            </div>
            <form className="flex w-full max-w-sm gap-2" onSubmit={(e) => e.preventDefault()}>
              <input type="email" placeholder="ton.nom@exemple.tn" className="input" />
              <Button type="submit" className="shrink-0">S'abonner</Button>
            </form>
          </div>
        </div>
      </section>
    </>
  )
}
