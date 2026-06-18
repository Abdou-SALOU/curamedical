export default function Bars({ data, height = 120, color = '#2a9b69' }) {
  const max = Math.max(...data.map(d => d.value))
  return (
    <div style={{ display: 'flex', alignItems: 'flex-end', gap: 10, height, padding: '8px 0' }}>
      {data.map((d, i) => (
        <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6 }}>
          <div style={{
            width: '100%',
            height: `${(d.value / max) * 100}%`,
            background: d.highlight ? color : '#dde6e1',
            borderRadius: '4px 4px 2px 2px',
            transition: 'height .3s',
          }} />
          <div style={{ fontSize: 10, color: 'var(--ink-500)', fontFamily: 'var(--font-mono)' }}>{d.label}</div>
        </div>
      ))}
    </div>
  )
}
