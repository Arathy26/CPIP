import { useState } from 'react';

// Fit categories come from the backend recruiter_matching_agent (MATCHING_RULES).
const TIER_STYLES = {
  'Strong Fit': 'bg-emerald-100 text-emerald-800',
  'Good Fit': 'bg-blue-100 text-blue-800',
  'Stretch Fit': 'bg-amber-100 text-amber-800',
  'Not Suitable Yet': 'bg-gray-100 text-gray-700',
};

function SkillChips({ label, skills, tone }) {
  if (!skills || skills.length === 0) return null;
  const styles = {
    have: 'bg-green-100 text-green-800',
    missing: 'bg-amber-100 text-amber-800',
  };
  return (
    <div>
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      <div className="flex flex-wrap gap-2">
        {skills.map((s) => (
          <span key={s} className={`text-xs px-2 py-1 rounded-full font-medium ${styles[tone]}`}>
            {tone === 'have' ? '✓' : '⚠'} {s}
          </span>
        ))}
      </div>
    </div>
  );
}

export default function JobMatchCard({ match }) {
  const [open, setOpen] = useState(false);
  const badge = TIER_STYLES[match.fit_category] || TIER_STYLES['Not Suitable Yet'];

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden mb-3">
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
          <span className={`px-3 py-1.5 rounded-lg text-sm font-semibold ${badge}`}>
            {match.fit_category}
          </span>
          <span className="text-lg font-bold text-gray-900">{match.fit_score}%</span>
          <svg
            className={`w-4 h-4 text-gray-400 transition-transform ${open ? 'rotate-180' : ''}`}
            fill="none" viewBox="0 0 24 24" stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {open && (
        <div className="border-t border-gray-100 px-5 py-4 space-y-4">
          <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-sm text-gray-600 bg-gray-50 rounded-lg p-3">
            <p><span className="text-gray-400">Company:</span> {match.company_name}</p>
            <p><span className="text-gray-400">Location:</span> {match.location}</p>
            <p><span className="text-gray-400">Type:</span> {match.employment_type || 'Not specified'}</p>
            <p><span className="text-gray-400">Experience:</span> {match.experience_level || 'Not specified'}</p>
            {match.salary_range && (
              <p><span className="text-gray-400">Salary:</span> {match.salary_range}</p>
            )}
          </div>

          {match.reason && (
            <div className="bg-blue-50 rounded-lg p-3">
              <p className="text-xs font-semibold tracking-wide text-blue-800 mb-1">WHY THIS ROLE MATCHES</p>
              <p className="text-sm text-blue-900">{match.reason}</p>
            </div>
          )}

          <div>
            <p className="text-xs font-semibold tracking-wide text-gray-500 mb-2">SKILL COVERAGE</p>
            <div className="flex gap-4 text-sm mb-3">
              <span className="text-green-700">Required: <strong>{match.required_coverage_percent}%</strong></span>
              {match.preferred_skills?.length > 0 && (
                <span className="text-blue-700">Preferred: <strong>{match.preferred_coverage_percent}%</strong></span>
              )}
            </div>
            <div className="space-y-3">
              <SkillChips label="Required skills you have" skills={match.matched_required_skills} tone="have" />
              <SkillChips label="Required skills to build" skills={match.missing_required_skills} tone="missing" />
              <SkillChips label="Preferred skills you have" skills={match.matched_preferred_skills} tone="have" />
              <SkillChips label="Preferred skills to build" skills={match.missing_preferred_skills} tone="missing" />
            </div>
          </div>

          {match.description && (
            <p className="text-sm text-gray-600 whitespace-pre-line">{match.description}</p>
          )}

          <p className="text-xs text-gray-400">
            Posted on CPIP by {match.posted_by || 'Recruiter'}. This is a fit recommendation, not a selection decision.
          </p>
        </div>
      )}
    </div>
  );
}
