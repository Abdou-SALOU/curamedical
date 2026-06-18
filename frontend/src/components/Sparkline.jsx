import { useState, useRef, useCallback } from 'react'

export default function Sparkline({ data, labels = [], color = '#2a9b69', height = 60, width = 240, fill = true }) {
  const [tooltip, setTooltip] = useState(null)
  const svgRef = useRef(null)

  const max = Math.max(...data, 0)
  const min = Math.min(...data, 0)
  const range = max - min || 1
  const pts = data.map((v, i) => ({
    x: data.length > 1 ? (i / (data.length - 1)) * width : width / 2,
    y: height - ((v - min) / range) * (height - 8) - 4,
  }))

  const path = pts.map((p, i) => (i === 0 ? `M${p.x},${p.y}` : `L${p.x},${p.y}`)).join(' ')
  const area = `${path} L${width},${height} L0,${height} Z`
  const gradId = `sg-${color.replace('#', '')}`

  const handleMouseMove = useCallback((e) => {
    const el = svgRef.current
    if (!el) return
    const rect = el.getBoundingClientRect()
    const relX = e.clientX - rect.left
    const idx = Math.max(0, Math.min(data.length - 1, Math.round((relX / rect.width) * (data.length - 1))))
    const domX = (pts[idx].x / width) * rect.width
    const domY = (pts[idx].y / height) * rect.height
    // La largeur est mesurée ici (événement) plutôt que via la ref pendant le rendu
    setTooltip({ idx, domX, domY, svgWidth: rect.width })
  }, [data.length, pts, width, height])

  return (
    <div style={{ position: 'relative' }}>
      <svg
        ref={svgRef}
        width="100%" height={height}
        viewBox={`0 0 ${width} ${height}`}
        preserveAspectRatio="none"
        onMouseMove={handleMouseMove}
        onMouseLeave={() => setTooltip(null)}
        style={{ cursor: 'crosshair', display: 'block' }}
      >
        {fill && (
          <defs>
            <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={color} stopOpacity="0.18" />
              <stop offset="100%" stopColor={color} stopOpacity="0" />
            </linearGradient>
          </defs>
        )}
        {fill && <path d={area} fill={`url(#${gradId})`} />}
        <path d={path} stroke={color} strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" />
        {tooltip && (
          <>
            <line
              x1={pts[tooltip.idx].x} y1={0}
              x2={pts[tooltip.idx].x} y2={height}
              stroke={color} strokeWidth={1} strokeDasharray="3 3" opacity={0.4}
            />
            <circle
              cx={pts[tooltip.idx].x} cy={pts[tooltip.idx].y}
              r={4} fill="white" stroke={color} strokeWidth={2}
            />
          </>
        )}
      </svg>
      {tooltip && (
        <div style={{
          position: 'absolute',
          left: Math.max(0, Math.min(
            tooltip.domX - 45,
            (tooltip.svgWidth ?? 200) - 90
          )),
          top: Math.max(0, tooltip.domY - 36),
          background: 'var(--ink-900, #1a2332)',
          color: '#fff',
          fontSize: 12,
          fontWeight: 600,
          padding: '4px 10px',
          borderRadius: 6,
          pointerEvents: 'none',
          whiteSpace: 'nowrap',
          zIndex: 10,
          boxShadow: '0 2px 10px rgba(0,0,0,0.2)',
        }}>
          {labels[tooltip.idx] ? `${labels[tooltip.idx]}: ` : ''}{data[tooltip.idx]}
        </div>
      )}
    </div>
  )
}
