import { Link } from 'react-router-dom'
import Icon from './Icon'

const VARIANTS = {
  primary: 'btn-primary',
  outline: 'btn-outline',
  ghost: 'btn-ghost',
  soft: 'btn-soft',
  danger: 'btn-danger',
}

const SIZES = { sm: 'btn-sm', md: 'btn-md', lg: 'btn-lg' }

export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  icon,
  iconRight,
  to,
  href,
  className = '',
  loading = false,
  full = false,
  ...rest
}) {
  const cls = [
    'btn',
    SIZES[size] || SIZES.md,
    VARIANTS[variant] || VARIANTS.primary,
    full ? 'w-full' : '',
    className,
  ].join(' ')

  const inner = (
    <>
      {loading ? (
        <Icon name="Loader2" size={size === 'sm' ? 13 : 15} className="animate-spin" />
      ) : (
        icon && <Icon name={icon} size={size === 'sm' ? 13 : 15} />
      )}
      {children}
      {iconRight && <Icon name={iconRight} size={size === 'sm' ? 13 : 15} />}
    </>
  )

  if (to) return <Link to={to} className={cls} {...rest}>{inner}</Link>
  if (href) return <a href={href} className={cls} {...rest}>{inner}</a>
  return (
    <button className={cls} disabled={loading || rest.disabled} {...rest}>
      {inner}
    </button>
  )
}
