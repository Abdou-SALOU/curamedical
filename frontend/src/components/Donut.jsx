export default function Donut({ segments, size = 160, stroke = 18 }) {
  const r = (size - stroke) / 2
  const c = 2 * Math.PI * r
  const total = segments.reduce((s, x) => s + x.value, 0)

  // Arcs précalculés (longueur + décalage cumulé) — pas de mutation pendant le rendu
  const arcs = segments.reduce((acc, s) => {
    const prev = acc[acc.length - 1]
    const offset = prev ? prev.offset + prev.dash : 0
    acc.push({ ...s, dash: (s.value / total) * c, offset })
    return acc
  }, [])

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#eef0f3" strokeWidth={stroke} />
      {arcs.map((s, i) => (
        <circle
          key={i}
          cx={size / 2} cy={size / 2} r={r}
          fill="none" stroke={s.color} strokeWidth={stroke}
          strokeDasharray={`${s.dash} ${c - s.dash}`}
          strokeDashoffset={-s.offset}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          strokeLinecap="butt"
        />
      ))}
    </svg>
  )
}
