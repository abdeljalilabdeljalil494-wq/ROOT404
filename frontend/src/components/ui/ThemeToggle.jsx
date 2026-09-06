import { useTheme } from '../../hooks/useTheme'
import Icon from './Icon'

export default function ThemeToggle({ className = '' }) {
  const { theme, toggle } = useTheme()
  return (
    <button
      onClick={toggle}
      aria-label={theme === 'dark' ? 'Activer le thème clair' : 'Activer le thème sombre'}
      title={theme === 'dark' ? 'Thème clair' : 'Thème sombre'}
      className={`grid h-9 w-9 place-items-center rounded-lg text-ink-soft transition-colors hover:bg-white/[0.06] hover:text-ink ${className}`}
    >
      <Icon name={theme === 'dark' ? 'Moon' : 'Sun'} size={17} />
    </button>
  )
}
