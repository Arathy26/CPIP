export default function SkillBadge({ skill, status = 'have', className = '' }) {
  const baseClass =
    status === 'have'
      ? 'bg-green-900/40 border border-green-700 text-green-300'
      : status === 'missing'
      ? 'bg-amber-900/40 border border-amber-700 text-amber-300'
      : 'bg-slate-700 border border-slate-600 text-slate-300';

  const icon = status === 'have' ? '✓' : status === 'missing' ? '⚠' : '◇';

  return (
    <span className={`inline-flex items-center gap-1 px-3 py-1 rounded text-xs font-medium border ${baseClass} ${className}`}>
      <span>{icon}</span>
      {skill}
    </span>
  );
}