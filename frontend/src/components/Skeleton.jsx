/**
 * Skeleton loader components for tables, panels, and cards.
 * Usage: <SkeletonTable rows={5} cols={4} /> or <SkeletonPanel />
 */

function Bone({ className = '' }) {
  return (
    <div
      className={`rounded-xl bg-slate-100 animate-pulse ${className}`}
      style={{ animationDuration: '1.4s' }}
    />
  )
}

export function SkeletonTable({ rows = 5, cols = 4 }) {
  return (
    <div className="overflow-hidden">
      {/* Header */}
      <div className="flex gap-4 px-6 py-3.5 border-b border-slate-100">
        {Array.from({ length: cols }).map((_, i) => (
          <Bone key={i} className="h-3 flex-1" style={{ maxWidth: i === 0 ? '140px' : undefined }} />
        ))}
      </div>
      {/* Rows */}
      {Array.from({ length: rows }).map((_, ri) => (
        <div key={ri} className="flex items-center gap-4 px-6 py-4 border-b border-slate-100/60">
          {/* Avatar */}
          <div className="flex items-center gap-3 flex-1">
            <Bone className="h-10 w-10 rounded-2xl shrink-0" />
            <div className="space-y-1.5 flex-1">
              <Bone className="h-3 w-32" />
              <Bone className="h-2.5 w-20" />
            </div>
          </div>
          {Array.from({ length: cols - 1 }).map((_, ci) => (
            <Bone key={ci} className="h-3 flex-1" />
          ))}
        </div>
      ))}
    </div>
  )
}

export function SkeletonPanel() {
  return (
    <div className="space-y-5 p-5">
      <div className="flex items-center gap-4">
        <Bone className="h-16 w-16 rounded-[1.4rem]" />
        <div className="space-y-2 flex-1">
          <Bone className="h-3 w-24" />
          <Bone className="h-6 w-44" />
          <Bone className="h-3 w-32" />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <Bone className="h-16 rounded-2xl" />
        <Bone className="h-16 rounded-2xl" />
      </div>
      <Bone className="h-12 rounded-2xl" />
      <Bone className="h-12 rounded-2xl" />
      <Bone className="h-24 rounded-2xl" />
      <Bone className="h-10 rounded-2xl" />
    </div>
  )
}

export function SkeletonCard() {
  return (
    <div className="bg-white/70 rounded-3xl p-6 border border-white/80 space-y-3">
      <div className="flex items-center justify-between">
        <Bone className="h-10 w-10 rounded-2xl" />
        <Bone className="h-6 w-12 rounded-full" />
      </div>
      <Bone className="h-8 w-20 mt-2" />
      <Bone className="h-3 w-28" />
    </div>
  )
}

export default Bone
