import { useState } from 'react';

const TIER_STYLES = {
  'Excellent Fit': { badge: 'bg-emerald-100 text-emerald-800', bar: 'bg-emerald-500' },
  'Good Fit': { badge: 'bg-blue-100 text-blue-800', bar: 'bg-blue-500' },
  'Possible Fit': { badge: 'bg-amber-100 text-amber-800', bar: 'bg-amber-500' },
  'Not Suitable Yet': { badge: 'bg-gray-100 text-gray-700', bar: 'bg-gray-400' },
  'Perfect Match': { badge: 'bg-emerald-100 text-emerald-800', bar: 'bg-emerald-500' },
  'High Match': { badge: 'bg-blue-100 text-blue-800', bar: 'bg-blue-500' },
  'Medium Match': { badge: 'bg-amber-100 text-amber-800', bar: 'bg-amber-500' },
  'Low Match': { badge: 'bg-gray-100 text-gray-700', bar: 'bg-gray-400' },
};

export default function JobMatchCard({ match }) {
  const [open, setOpen] = useState(false);
  const style = TIER_STYLES[match.suitability] || TIER_STYLES['Not Suitable Yet'];

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden mb-3">

      {/* Header */}
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between px-5 py-4 text-left hover:bg-gray-50 transition-colors"
      >
        <div>
          <p className="font-semibold text-gray-900">{match.job_title}</p>
          <p className="text-xs text-gray-500 mt-0.5">
            {match.company_name} • {match.location}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className={`px-3 py-1.5 rounded-lg text-sm font-semibold ${style.badge}`}>
            {match.suitability}
          </span>
          <span className="text-lg font-bold text-gray-900">{match.fit_score}%</span>
          <svg
            className={`w-4 h-4 text-gray-400 transition-transform ${open ? 'rotate-180' : ''}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {/* Expanded */}
      {open && (
        <div className="border-t border-gray-100 px-5 py-4 space-y-4">

          {/* Job info */}
          <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-sm text-gray-600 bg-gray-50 rounded-lg p-3">
  <p><span className="text-gray-400">Company:</span> {match.company_name || 'Unknown'}</p>
  <p><span className="text-gray-400">Location:</span> {match.location}</p>
  <p>
    <span className="text-gray-400">Work Type:</span>{' '}
    {match.is_remote ? (
      <span className="text-green-600 font-medium">🏠 Remote</span>
    ) : (
      <span className="text-blue-600 font-medium">🏢 On-site</span>
    )}
  </p>
  <p>
    <span className="text-gray-400">Type:</span>{' '}
    {match.employment_type || 'Full-time'}
  </p>
</div>

          {/* Agent scores */}
          {match.agent_scores && (
            <div className="bg-blue-50 rounded-lg p-3">
              <p className="text-xs font-semibold tracking-wide text-blue-800 mb-2">
                READINESS SCORES
              </p>
              <div className="grid grid-cols-2 gap-2 text-sm text-blue-900">
                <span>Skill Gap: <strong>{match.agent_scores.skill_gap}/100</strong></span>
                <span>Portfolio: <strong>{match.agent_scores.portfolio}/100</strong></span>
                <span>Resume: <strong>{match.agent_scores.resume}/100</strong></span>
                <span>Interview: <strong>{match.agent_scores.interview}/100</strong></span>
              </div>
            </div>
          )}

          {/* Skill coverage */}
          {match.skill_coverage && (
            <div>
              <p className="text-xs font-semibold tracking-wide text-gray-500 mb-2">
                SKILL COVERAGE
              </p>
              <div className="flex gap-4 text-sm">
                <span className="text-green-700">
                  Required: <strong>{match.skill_coverage.required_percent}%</strong>
                </span>
                <span className="text-blue-700">
                  Preferred: <strong>{match.skill_coverage.preferred_percent}%</strong>
                </span>
              </div>
            </div>
          )}

          {/* Required skills */}
          {match.required_skills?.length > 0 && (
            <div>
              <p className="text-xs font-semibold tracking-wide text-gray-500 mb-2">
                REQUIRED SKILLS
              </p>
              <div className="flex flex-wrap gap-2">
                {match.required_skills.map((s, i) => (
                  <span
                    key={i}
                    className="px-2 py-1 rounded bg-gray-50 text-gray-700 text-xs font-medium border"
                  >
                    {s}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Resume quality */}
          {match.resume_score !== undefined && (
            <div className="bg-purple-50 rounded-lg p-3">
              <p className="text-xs font-semibold tracking-wide text-purple-800 mb-2">
                RESUME QUALITY FOR THIS JOB
              </p>
              <div className="flex gap-4 text-sm text-purple-900 mb-2">
                <span>Resume score: <strong>{match.resume_score}/100</strong></span>
                {match.resume_keyword_match_percent != null && (
                  <span>Keyword match: <strong>{match.resume_keyword_match_percent}%</strong></span>
                )}
              </div>
              {match.resume_tips?.slice(0, 2).map((tip, i) => (
                <p key={i} className="text-sm text-purple-700 mt-1">⚠ {tip}</p>
              ))}
            </div>
          )}

          {/* Apply button */}
          {match.apply_link ? (
            
             <a href={match.apply_link}
              target="_blank"
              rel="noopener noreferrer"
              className="block w-full text-center bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 rounded-xl transition-colors"
            >
              Apply Now →
            </a>
          ) : (
            <p className="text-sm text-gray-400 text-center">No apply link available</p>
          )}

        </div>
      )}
    </div>
  );
}