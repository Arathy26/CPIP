/**
 * NextStepsCard — the training plan. Every action comes from a real gap
 * found by an agent (missing skill, missing evidence, interview, resume).
 * No durations are shown: CPIP does not measure how long learning takes.
 */
const CATEGORY_STYLE = {
  "Technical Skills": "bg-amber-50 text-amber-800 border-amber-200",
  "Portfolio Development": "bg-indigo-50 text-indigo-800 border-indigo-200",
  "Interview Preparation": "bg-blue-50 text-blue-800 border-blue-200",
  "Resume Refinement": "bg-violet-50 text-violet-800 border-violet-200",
};

export default function NextStepsCard({ actions = [] }) {
  const visible = actions.slice(0, 6);
  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-4">
      <p className="font-semibold text-gray-900">Your next steps</p>
      <p className="text-sm text-gray-500 mb-4">
        Built from your actual gaps, in priority order.
      </p>
      {visible.length === 0 ? (
        <p className="text-sm text-gray-500">No gaps found in the areas assessed so far.</p>
      ) : (
        <ol className="space-y-3">
          {visible.map((a) => (
            <li key={a.rank} className="flex gap-3 items-start">
              <span className="w-7 h-7 rounded-full bg-purple-600 text-white text-xs font-bold flex items-center justify-center shrink-0">
                {a.rank}
              </span>
              <div className="flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <p className="text-sm font-semibold text-gray-900">{a.title}</p>
                  <span className={`text-[11px] px-2 py-0.5 rounded-full border ${CATEGORY_STYLE[a.category] || "bg-gray-50 text-gray-700 border-gray-200"}`}>
                    {a.category}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-0.5">{a.reason}</p>
              </div>
            </li>
          ))}
        </ol>
      )}
      {actions.length > visible.length && (
        <p className="text-xs text-gray-400 mt-3">+ {actions.length - visible.length} more action(s)</p>
      )}
    </div>
  );
}
