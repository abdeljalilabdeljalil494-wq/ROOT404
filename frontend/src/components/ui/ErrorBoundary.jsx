import React from 'react'
import Icon from './Icon'
import Button from './Button'

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null, errorInfo: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    console.error('[ErrorBoundary] Caught error:', error, errorInfo)
    this.setState({ errorInfo })
    
    // In production, would send to error tracking service
    if (import.meta.env.PROD) {
      // Example: Sentry.captureException(error)
    }
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null })
    if (this.props.onReset) {
      this.props.onReset()
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-[400px] flex-col items-center justify-center gap-4 p-8">
          <div className="rounded-full bg-danger/15 p-4">
            <Icon name="AlertTriangle" size={32} className="text-danger" />
          </div>
          <h2 className="text-[18px] font-bold text-ink">
            {this.props.fallbackTitle || 'Une erreur est survenue'}
          </h2>
          <p className="max-w-md text-center text-[13px] leading-relaxed text-ink-dim">
            {this.props.fallbackMessage || 
              "Désolé, quelque chose s'est mal passé. L'équipe a été notifiée et va corriger le problème."}
          </p>
          {import.meta.env.DEV && this.state.error && (
            <details className="mt-4 max-w-2xl rounded-lg border border-line bg-root-850 p-4">
              <summary className="cursor-pointer text-[12px] font-medium text-ink-soft">
                Détails techniques (dev only)
              </summary>
              <pre className="mt-3 overflow-auto font-mono text-[11px] text-danger">
                {this.state.error.toString()}
                {this.state.errorInfo?.componentStack}
              </pre>
            </details>
          )}
          <div className="mt-4 flex gap-2">
            <Button onClick={this.handleReset} icon="RefreshCw">
              Réessayer
            </Button>
            <Button variant="outline" to="/" icon="Home">
              Retour à l'accueil
            </Button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

// Hook version for functional components
export function withErrorBoundary(Component, errorBoundaryProps = {}) {
  return function WrappedComponent(props) {
    return (
      <ErrorBoundary {...errorBoundaryProps}>
        <Component {...props} />
      </ErrorBoundary>
    )
  }
}

// Error fallback for specific sections
export function ErrorFallback({ error, resetError, title, message }) {
  return (
    <div className="rounded-lg border border-danger/25 bg-danger/[0.06] p-6">
      <div className="flex items-start gap-3">
        <Icon name="AlertCircle" size={20} className="mt-0.5 shrink-0 text-danger" />
        <div className="flex-1">
          <h3 className="text-[14px] font-bold text-ink">{title || 'Erreur'}</h3>
          <p className="mt-1 text-[12.5px] leading-relaxed text-ink-soft">
            {message || error?.message || "Une erreur est survenue"}
          </p>
          {resetError && (
            <Button size="sm" variant="outline" className="mt-3" onClick={resetError} icon="RefreshCw">
              Réessayer
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
