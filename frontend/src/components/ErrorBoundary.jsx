import { Component } from 'react'

/**
 * ErrorBoundary — Capture les erreurs React non gérées.
 * Affiche une page d'erreur soignée au lieu d'un écran blanc.
 *
 * Usage dans main.jsx :
 *   <ErrorBoundary>
 *     <App />
 *   </ErrorBoundary>
 */
export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, info) {
    console.error('[ErrorBoundary] Erreur React non gérée :', error, info)
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null })
    window.location.href = '/'
  }

  render() {
    if (!this.state.hasError) return this.props.children

    return (
      <div
        style={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '24px',
          background: 'linear-gradient(135deg, #f0f5f9 0%, #e8f4f0 100%)',
          fontFamily: 'Inter, sans-serif',
        }}
      >
        <div
          style={{
            maxWidth: '480px',
            width: '100%',
            background: 'rgba(255,255,255,0.9)',
            backdropFilter: 'blur(24px)',
            borderRadius: '28px',
            border: '1px solid rgba(226,232,240,0.8)',
            boxShadow: '0 32px 80px rgba(15,23,42,0.10)',
            padding: '48px 40px',
            textAlign: 'center',
          }}
        >
          {/* Icon */}
          <div
            style={{
              width: '72px',
              height: '72px',
              borderRadius: '22px',
              background: 'linear-gradient(135deg, #fee2e2, #fecaca)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 24px',
              fontSize: '32px',
            }}
          >
            ⚠️
          </div>

          <h1
            style={{
              fontFamily: 'Manrope, sans-serif',
              fontSize: '22px',
              fontWeight: '900',
              color: '#0f172a',
              marginBottom: '12px',
              letterSpacing: '-0.03em',
            }}
          >
            Oups, quelque chose a planté
          </h1>

          <p
            style={{
              color: '#64748b',
              fontSize: '14px',
              lineHeight: '1.7',
              marginBottom: '8px',
            }}
          >
            Une erreur inattendue s'est produite dans l'interface. Cela peut être lié à une réponse API incorrecte ou à un composant défectueux.
          </p>

          {this.state.error && (
            <details
              style={{
                marginBottom: '28px',
                background: '#f8fafc',
                borderRadius: '12px',
                padding: '12px 16px',
                textAlign: 'left',
              }}
            >
              <summary
                style={{
                  cursor: 'pointer',
                  fontSize: '11px',
                  fontWeight: '700',
                  color: '#94a3b8',
                  textTransform: 'uppercase',
                  letterSpacing: '0.08em',
                  marginBottom: '8px',
                }}
              >
                Détails techniques
              </summary>
              <pre
                style={{
                  fontSize: '11px',
                  color: '#dc2626',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  margin: 0,
                }}
              >
                {this.state.error.message}
              </pre>
            </details>
          )}

          <button
            onClick={this.handleReset}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '12px 28px',
              borderRadius: '14px',
              background: 'linear-gradient(135deg, #10b981, #0d9488)',
              color: '#fff',
              fontWeight: '700',
              fontSize: '14px',
              border: 'none',
              cursor: 'pointer',
              boxShadow: '0 4px 16px rgba(16,185,129,0.3)',
            }}
          >
            ↩ Retour à l'accueil
          </button>
        </div>
      </div>
    )
  }
}
