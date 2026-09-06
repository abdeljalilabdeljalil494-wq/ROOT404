export default function SectionHeading({
  eyebrow,
  title,
  highlight,
  text,
  align = 'center',
  className = '',
}) {
  const a = align === 'center' ? 'text-center items-center mx-auto' : 'text-left items-start'
  return (
    <div className={`flex max-w-2xl flex-col ${a} ${className}`}>
      {eyebrow && (
        <span className="mb-3 inline-flex items-center gap-2 rounded-full border border-brand-500/25 bg-brand-500/[0.07] px-3 py-1 text-[10.5px] font-bold uppercase tracking-[0.13em] text-brand-400">
          {eyebrow}
        </span>
      )}
      <h2 className="text-[26px] font-extrabold leading-tight tracking-tight text-white sm:text-[34px]">
        {title} {highlight && <span className="text-brand-500">{highlight}</span>}
      </h2>
      {text && <p className="mt-3.5 text-[14px] leading-relaxed text-ink-dim">{text}</p>}
    </div>
  )
}
