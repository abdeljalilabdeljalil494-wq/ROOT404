import { Link } from 'react-router-dom'

/**
 * ROOT 404 brand mark — recreated as inline SVG from the reference artwork:
 * a circuit "root tree" (branches + nodes above, roots below) flanked by
 * the shell prompt `>_` on the left and the numeral `4` on the right.
 */
export function LogoMark({ size = 34, className = '' }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 64 64"
      fill="none"
      className={className}
      role="img"
      aria-label="ROOT 404"
    >
      <g
        stroke="#F8851F"
        strokeWidth="2.1"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      >
        {/* trunk */}
        <path d="M32 8v48" stroke="url(#r404-trunk)" strokeWidth="2.4" />

        {/* upper branches */}
        <path d="M32 24 22 16" />
        <path d="M32 22 42 14" />
        <path d="M32 27 18 20" />
        <path d="M27 19v-5" />
        <path d="M37 19v-5" />

        {/* lower roots */}
        <path d="M32 40 22 47" />
        <path d="M32 40 42 47" />
        <path d="M32 44 25 54" />
        <path d="M32 44 39 54" />
        <path d="M32 42 17 46" />
        <path d="M32 42 47 46" />
        <path d="M25 54v3" />
        <path d="M32 50v8" />

        {/* nodes */}
        <circle cx="22" cy="16" r="2.6" />
        <circle cx="42" cy="14" r="2.6" />
        <circle cx="18" cy="20" r="2.6" />
        <circle cx="32" cy="58" r="2.6" />
      </g>

      {/* crown node — white */}
      <circle cx="32" cy="8" r="3.1" stroke="#FFFFFF" strokeWidth="2.1" fill="none" />

      {/* shell prompt >_ */}
      <g stroke="#FFFFFF" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round">
        <path d="m6 25 6 5-6 5" />
        <path d="M14 37h8" />
      </g>

      {/* numeral 4 */}
      <path
        d="M55 18v14M55 32h-3M55 32h4M55 18 44 32h11"
        stroke="#F8851F"
        strokeWidth="3.2"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />

      <defs>
        <linearGradient id="r404-trunk" x1="32" y1="8" x2="32" y2="56" gradientUnits="userSpaceOnUse">
          <stop stopColor="#FFFFFF" />
          <stop offset="0.45" stopColor="#FFD9AE" />
          <stop offset="1" stopColor="#F8851F" />
        </linearGradient>
      </defs>
    </svg>
  )
}

/**
 * Full lockup: mark + "ROOT 404" wordmark + optional tagline.
 * `compact` drops the tagline (used in dense app headers).
 */
export default function Logo({ to = '/', compact = false, size = 34, className = '' }) {
  const Wrapper = to ? Link : 'div'
  const props = to ? { to } : {}

  return (
    <Wrapper
      {...props}
      className={`group flex shrink-0 items-center gap-2.5 ${className}`}
      aria-label="ROOT 404 — Elite Coder Platform"
    >
      <LogoMark size={size} className="transition-transform duration-300 group-hover:scale-105" />
      <span className="flex flex-col leading-none">
        <span className="text-[17px] font-extrabold tracking-tight">
          <span className="text-white dark:text-white">ROOT</span>{' '}
          <span className="text-brand-500">404</span>
        </span>
        {!compact && (
          <span className="mt-1 text-[9.5px] font-medium uppercase tracking-[0.14em] text-ink-dim">
            Elite Coder Platform
          </span>
        )}
      </span>
    </Wrapper>
  )
}
