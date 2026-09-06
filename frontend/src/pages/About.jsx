import { useEffect } from 'react'
import Icon from '../components/ui/Icon'
import Button from '../components/ui/Button'
import SectionHeading from '../components/ui/SectionHeading'
import Avatar from '../components/ui/Avatar'
import { values, timeline, heroStats } from '../data/mock'

const TEAM = [
  { name: 'Yosr Mansouri', role: 'Co-fondatrice & Pédagogie', avatar: 'https://i.pravatar.cc/128?img=44' },
  { name: 'Karim Jelassi', role: 'Co-fondateur & Infrastructure', avatar: 'https://i.pravatar.cc/128?img=15' },
  { name: 'Salma Ferchichi', role: 'Lead Moulinette & Sécurité', avatar: 'https://i.pravatar.cc/128?img=49' },
  { name: 'Anis Bouzid', role: 'Communauté & Partenariats', avatar: 'https://i.pravatar.cc/128?img=59' },
]

const PARTNERS = ['Instadeep', 'Talan', 'Vermeg', 'Sofrecom', 'Actia', 'Focus Corp', 'Wevioo', 'Proxym']

export default function About() {
  useEffect(() => { document.title = 'À propos — ROOT 404' }, [])

  return (
    <>
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-line bg-root-950 py-20 sm:py-28">
        <div aria-hidden className="absolute inset-0 bg-grid opacity-40" />
        <div
          aria-hidden
          className="absolute left-1/2 top-0 h-80 w-[600px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-brand-500/15 blur-[100px]"
        />
        <div className="container-page relative text-center">
          <span className="inline-flex items-center gap-2 rounded-full border border-brand-500/30 bg-brand-500/[0.07] px-3.5 py-1.5 text-[10.5px] font-bold uppercase tracking-[0.13em] text-brand-400">
            <Icon name="Flag" size={12} /> Made in Tunisia
          </span>
          <h1 className="mx-auto mt-6 max-w-3xl text-[32px] font-extrabold leading-[1.1] tracking-tight text-white sm:text-[46px]">
            Nous formons des développeurs, <span className="text-brand-500">pas des diplômés</span>
          </h1>
          <p className="mx-auto mt-5 max-w-2xl text-[14.5px] leading-relaxed text-ink-soft">
            ROOT 404 est née d'un constat simple : en Tunisie, le talent ne manque pas — c'est
            l'environnement pour l'exprimer qui manquait. Nous avons construit cet environnement.
          </p>
        </div>
      </section>

      {/* Stats */}
      <section className="border-b border-line bg-root-900 py-14">
        <div className="container-page">
          <dl className="grid grid-cols-2 gap-8 sm:grid-cols-3 lg:grid-cols-5">
            {heroStats.map((s) => (
              <div key={s.label} className="text-center">
                <dd className="font-mono text-[28px] font-extrabold text-brand-500">{s.value}</dd>
                <dt className="mt-1 text-[12px] text-ink-dim">{s.label}</dt>
              </div>
            ))}
          </dl>
        </div>
      </section>

      {/* Values */}
      <section className="border-b border-line bg-root-950 py-20">
        <div className="container-page">
          <SectionHeading eyebrow="Nos principes" title="Quatre convictions," highlight="non négociables" />
          <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {values.map((v) => (
              <article key={v.title} className="card p-6 transition-all hover:-translate-y-1 hover:border-brand-500/25">
                <span className="grid h-11 w-11 place-items-center rounded-lg bg-brand-500/10 text-brand-500">
                  <Icon name={v.icon} size={21} />
                </span>
                <h3 className="mt-4 text-[14px] font-bold text-white">{v.title}</h3>
                <p className="mt-2 text-[12.5px] leading-relaxed text-ink-dim">{v.text}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* Timeline */}
      <section className="border-b border-line bg-root-900 py-20">
        <div className="container-page">
          <SectionHeading eyebrow="Histoire" title="De l'idée" highlight="au campus" />
          <div className="relative mt-14">
            <div aria-hidden className="absolute left-[15px] top-2 h-[calc(100%-1rem)] w-px bg-line lg:left-1/2" />
            <ol className="space-y-8">
              {timeline.map((t, i) => (
                <li key={t.year} className={`relative flex gap-6 lg:w-1/2 ${i % 2 ? 'lg:ml-auto lg:pl-10' : 'lg:pr-10 lg:text-right'}`}>
                  <span
                    className={`relative z-10 mt-1 grid h-8 w-8 shrink-0 place-items-center rounded-full border-2 border-brand-500/40 bg-root-900 text-brand-500 lg:absolute ${
                      i % 2 ? 'lg:-left-4' : 'lg:-right-4'
                    }`}
                  >
                    <Icon name="Circle" size={9} className="fill-brand-500" />
                  </span>
                  <div className="card flex-1 p-5">
                    <span className="font-mono text-[12px] font-bold text-brand-500">{t.year}</span>
                    <h3 className="mt-1.5 text-[15px] font-bold text-white">{t.title}</h3>
                    <p className="mt-2 text-[13px] leading-relaxed text-ink-dim">{t.text}</p>
                  </div>
                </li>
              ))}
            </ol>
          </div>
        </div>
      </section>

      {/* Team */}
      <section className="border-b border-line bg-root-950 py-20">
        <div className="container-page">
          <SectionHeading eyebrow="Équipe" title="Les gens" highlight="derrière la Moulinette" />
          <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {TEAM.map((m) => (
              <article key={m.name} className="card flex flex-col items-center p-6 text-center transition-transform hover:-translate-y-1">
                <Avatar src={m.avatar} name={m.name} size="lg" ring />
                <h3 className="mt-4 text-[13.5px] font-bold text-white">{m.name}</h3>
                <p className="mt-1 text-[11.5px] text-ink-dim">{m.role}</p>
                <div className="mt-4 flex gap-1.5">
                  {['Github', 'Linkedin'].map((s) => (
                    <a key={s} href="#" aria-label={s} className="grid h-8 w-8 place-items-center rounded-md border border-line text-ink-dim transition-colors hover:border-brand-500/40 hover:text-brand-500">
                      <Icon name={s} size={14} />
                    </a>
                  ))}
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      {/* Partners */}
      <section className="border-b border-line bg-root-900 py-20">
        <div className="container-page text-center">
          <SectionHeading eyebrow="Partenaires" title="Ils recrutent" highlight="nos codeurs" className="mb-12" />
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {PARTNERS.map((p) => (
              <div key={p} className="flex h-20 items-center justify-center rounded-xl border border-line bg-root-850 text-[14px] font-bold tracking-tight text-ink-dim transition-colors hover:border-brand-500/25 hover:text-ink">
                {p}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-root-950 py-20">
        <div className="container-page text-center">
          <h2 className="text-[26px] font-extrabold tracking-tight text-white sm:text-[32px]">
            Une question, un partenariat, une idée ?
          </h2>
          <p className="mx-auto mt-3 max-w-lg text-[14px] text-ink-dim">
            L'équipe répond en général sous 48 h. Le Discord, lui, répond en dix minutes.
          </p>
          <div className="mt-7 flex flex-wrap justify-center gap-3">
            <Button size="lg" icon="Mail">contact@root404.tn</Button>
            <Button variant="outline" size="lg" icon="MessageCircle">Rejoindre le Discord</Button>
          </div>
        </div>
      </section>
    </>
  )
}
