export default function AgentScoreCard({
  title,
  score,
  icon,
  description,
  isExpanded,
  onToggle,
  details,
}) {
  return (
    <div className="bg-slate-800 border border-slate-700 rounded-lg overflow-hidden">
      {/* Header */}
      <button
        onClick={onToggle}
        className="w-full p-4 flex items-center justify-between hover:bg-slate-700/50 transition"
      >
        <div className="flex items-center gap-4 flex-1">
          <div className="text-2xl">{icon}</div>
          <div className="text-left">
            <p className="text-white font-semibold">{title}</p>
            <p className="text-slate-400 text-sm">{description}</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-blue-400 font-bold text-lg">{score}</p>
          <p className="text-slate-500 text-xs">/100</p>
        </div>
      </button>

      {/* Expanded Content */}
      {isExpanded && details && (
        <div className="border-t border-slate-700 p-4 space-y-4 bg-slate-700/30">
          {details.have && (
            <div>
              <p className="text-xs text-slate-400 uppercase font-semibold mb-2">Have</p>
              <div className="flex flex-wrap gap-2">
                {details.have.map((skill) => (
                  <span
                    key={skill}
                    className="bg-green-900/40 border border-green-700 text-green-300 px-3 py-1 rounded text-xs font-medium"
                  >
                    ✓ {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {details.missing && (
            <div>
              <p className="text-xs text-slate-400 uppercase font-semibold mb-2">Missing</p>
              <div className="flex flex-wrap gap-2">
                {details.missing.map((skill) => (
                  <span
                    key={skill}
                    className="bg-amber-900/40 border border-amber-700 text-amber-300 px-3 py-1 rounded text-xs font-medium"
                  >
                    ⚠ {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {details.action && (
            <div className="bg-blue-900/40 border border-blue-700 rounded p-3">
              <p className="text-blue-200 text-sm">
                <span className="font-semibold">💡</span> {details.action}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}