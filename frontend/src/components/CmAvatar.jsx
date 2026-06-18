const PALETTE = ['#2a9b69', '#4178d6', '#c98b1e', '#6a5acd', '#d4543f', '#5b95a8']

export default function CmAvatar({ name = '', size = 32 }) {
  const initials = name.split(' ').map(w => w[0]).slice(0, 2).join('').toUpperCase() || '?'
  const bg = PALETTE[name.length % PALETTE.length]
  return (
    <div
      className="cm-avatar"
      style={{ background: bg, width: size, height: size, fontSize: size * 0.38 }}
    >
      {initials}
    </div>
  )
}
