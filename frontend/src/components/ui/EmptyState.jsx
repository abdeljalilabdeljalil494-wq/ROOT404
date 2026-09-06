import Icon from './Icon'

export default function EmptyState({ icon = 'Inbox', title, text, action, className = '' }) {
  return (
    <div className={`flex flex-col items-center justify-center px-6 py-16 text-center ${className}`}>
      <span className="mb-4 grid h-14 w-14 place-items-center rounded-xl border border-line bg-root-850 text-ink-dim">
        <Icon name={icon} size={22} />
      </span>
      <h3 className="text-sm font-semibold text-ink">{title}</h3>
      {text && <p className="mt-1.5 max-w-sm text-[13px] leading-relaxed text-ink-dim">{text}</p>}
      {action && <div className="mt-5">{action}</div>}
    </div>
  )
}
