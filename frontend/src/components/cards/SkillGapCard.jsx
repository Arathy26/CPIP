import { useState } from 'react';

export default function SkillGapCard({ skillsHave, skillsMissing, score, basedOnPostings, resumeQuality }) {
  const [showAllMissing, setShowAllMissing] = useState(false);

  const scoreColor =
    score >= 80 ? 'text-green-600' : score >= 60 ? 'text-blue-600' : 'text-amber-600';

  const normalizedMissing = (skillsMissing || []).map((item) =>
    typeof item === 'string'
      ? { skill: item, demand_weight: null }
      : item
  );

  const visibleMissing = showAllMissing ? normalizedMissing : normalizedMissing.slice(0, 8);

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-purple-100 flex items-center justify-center text-xl">
            🎯
          </div>
          <div>
            <p className="font-semibold text-gray-900">Skill Gap</p>
            <p className="text-sm text-gray-500">
              {basedOnPostings
                ? `Based on ${basedOnPostings} real job postings`
                : 'Skills vs role requirements'}
            </p>
          </div>
        </div>
        <div className="text-right">
          <span className={`text-2xl font-bold ${scoreColor}`}>{score}</span>
          <span className="block text-xs text-gray-400">/100</span>
        </div>
      </div>

      {/* HAVE skills */}
      {skillsHave && skillsHave.length > 0 && (
        <div className="mb-4">
          <p className="text-xs font-semibold tracking-wide text-gray-500 mb-2">
            HAVE ({skillsHave.length})
          </p>
          <div className="flex flex-wrap gap-2">
            {skillsHave.map((skill, i) => (
              <span key={i} className="px-3 py-1.5 rounded-lg bg-green-50 text-green-700 text-sm font-medium whitespace-nowrap">
                ✓ {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* MISSING skills - grid layout for alignment */}
      {normalizedMissing.length > 0 && (
        <div className="mb-3">
          <p className="text-xs font-semibold tracking-wide text-gray-500 mb-2">
            MISSING ({normalizedMissing.length})
          </p>
          <div className="grid grid-cols-4 gap-2">
            {visibleMissing.map((item, i) => (
              <div
                key={i}
                className="flex items-center justify-between px-3 py-1.5 rounded-lg bg-amber-50 text-amber-700 text-sm font-medium w-full"
              >
                <span className="truncate text-xs">⚠ {item.skill}</span>
                {item.demand_weight != null && (
                  <span className="text-xs text-amber-500 ml-1 shrink-0">
                    ({item.demand_weight}%)
                  </span>
                )}
              </div>
            ))}
          </div>

          {normalizedMissing.length > 8 && (
            <button
              onClick={() => setShowAllMissing(!showAllMissing)}
              className="mt-3 text-sm font-semibold text-purple-600 hover:text-purple-800"
            >
              {showAllMissing
                ? '▲ Show less'
                : `▼ Show ${normalizedMissing.length - 8} more missing skills`}
            </button>
          )}
        </div>
      )}

      {resumeQuality && (
        <div className="mt-4 bg-purple-50 rounded-lg p-3">
          <p className="text-xs font-semibold tracking-wide text-purple-800 mb-1">RESUME QUALITY</p>
          <p className="text-sm text-purple-900 mb-1">
            Score: <strong>{resumeQuality.resume_score}/100</strong>
          </p>
          {(resumeQuality.improvement_tips || []).slice(0, 3).map((tip, i) => (
            <p key={i} className="text-sm text-purple-700 mt-1">⚠ {tip}</p>
          ))}
        </div>
      )}
    </div>
  );
}