import { useState } from "react";

/**
 * CareerReadinessPanel — overall readiness + 5 metric cards.
 * A null score means "not assessed yet" and is shown as "—", never as 0.
 */
const AREA_LABELS = {
  skill_gap: "skills",
  portfolio: "portfolio",
  resume: "resume",
  interview: "interview",
};

function Score({ value, color }) {
  if (value === null || value === undefined) {
    return (
      <>
        <p className={`text-3xl font-extrabold mt-1 ${color} opacity-40`}>—</p>
        <p className={`text-xs mt-1 ${color} opacity-70`}>Not assessed yet</p>
      </>
    );
  }
  return (
    <p className={`text-3xl font-extrabold mt-1 ${color}`}>
      {Math.round(value)}
      <span className="text-sm font-normal">/100</span>
    </p>
  );
}

function MetricCard({ title, value, caption, tone }) {
  return (
    <div className={`rounded-2xl ${tone.bg} border ${tone.border} p-4 text-center flex flex-col justify-center`}>
      <p className={`text-xs font-semibold tracking-wide ${tone.text}`}>{title}</p>
      <Score value={value} color={tone.text} />
      {value !== null && value !== undefined && (
        <p className={`text-xs mt-1 ${tone.text} opacity-80`}>{caption}</p>
      )}
    </div>
  );
}


/** "How is this calculated?" — shows the formula and what each area is based on. */
function CalculationDetails({ calculation }) {
  const [open, setOpen] = useState(false);
  if (!calculation) return null;
  const rows = calculation.breakdown || [];
  const stripLabel = (text, label) =>
    (text || "").replace(new RegExp(`^${label}:\\s*`, "i"), "");

  return (
    <div className="mt-4">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        aria-expanded={open}
        className="text-sm font-semibold text-purple-700 hover:text-purple-900"
      >
        How is this calculated? {open ? "▲" : "▼"}
      </button>

      {open && (
        <div className="mt-3 bg-white/80 rounded-xl border border-purple-200 p-4">
          <p className="text-sm text-gray-700">{calculation.method}</p>
          {calculation.formula && (
            <p className="mt-2 text-sm font-mono font-semibold text-purple-800">{calculation.formula}</p>
          )}
          <table className="mt-3 w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-gray-500 border-b border-purple-100">
                <th className="py-2 pr-3 font-semibold">Area</th>
                <th className="py-2 pr-3 font-semibold">Score</th>
                <th className="py-2 pr-3 font-semibold">Counted</th>
                <th className="py-2 font-semibold">Based on</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.area} className="border-b border-purple-50 align-top">
                  <td className="py-2 pr-3 font-medium text-gray-900">{r.label}</td>
                  <td className="py-2 pr-3 text-gray-900">
                    {r.included ? `${Math.round(r.score)}/100` : "—"}
                  </td>
                  <td className="py-2 pr-3">
                    {r.included ? (
                      <span className="text-green-700">✓ Yes</span>
                    ) : (
                      <span className="text-gray-400">No data yet</span>
                    )}
                  </td>
                  <td className="py-2 text-gray-600">{stripLabel(r.basis, r.label)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default function CareerReadinessPanel({
  readiness,
  calculation,
  scoresMissing = [],
  targetRole,
  jobs,
  interviewScore,
  portfolioScore,
  resumeScore,
  topMissingSkill,
  gapScore,
}) {
  const hasReadiness = readiness !== null && readiness !== undefined;
  const pct = hasReadiness ? Math.max(0, Math.min(100, readiness)) : 0;
  const missingText = scoresMissing.map((k) => AREA_LABELS[k] || k).join(", ");

  return (
    <div className="mb-6">
      <div className="rounded-2xl bg-gradient-to-br from-purple-100 to-purple-50 border border-purple-200 p-8 mb-4">
        <p className="text-sm font-semibold tracking-wide text-purple-800 mb-4">
          YOUR CAREER READINESS
        </p>
        <div className="flex items-center gap-8">
          <div className="min-w-[11rem]">
            <p className="text-6xl font-extrabold text-purple-800 leading-none">
              {hasReadiness ? Math.round(readiness) : "—"}
              {hasReadiness && <span className="text-3xl align-top">%</span>}
            </p>
            <p className="mt-2 text-purple-900 font-medium">
              {targetRole ? `Readiness for ${targetRole}` : "Readiness for target role"}
            </p>
            {hasReadiness && missingText && (
              <p className="mt-1 text-xs text-purple-700">Not included yet: {missingText}</p>
            )}
            {!hasReadiness && (
              <p className="mt-1 text-xs text-purple-700">Not enough data yet</p>
            )}
          </div>
          <div className="flex-1 h-24 rounded-xl overflow-hidden flex bg-gray-200">
            {hasReadiness && (
              <>
                <div className="bg-purple-600 transition-all" style={{ width: `${pct}%` }} />
                <div className="bg-amber-400 transition-all" style={{ width: `${100 - pct}%` }} />
              </>
            )}
          </div>
        </div>
        <CalculationDetails calculation={calculation} />
        <p className="mt-4 text-xs text-purple-700">
          Readiness support only. Final hiring decisions are made by employers.
        </p>
      </div>

      <div className="grid grid-cols-5 gap-3">
        <div className="rounded-2xl bg-green-50 border border-green-200 p-4 text-center flex flex-col justify-center">
          <p className="text-xs font-semibold tracking-wide text-green-800">APPLY NOW</p>
          <p className="text-3xl font-extrabold text-green-800 mt-1">{jobs}</p>
          <p className="text-xs text-green-700 mt-1">Matching postings</p>
        </div>

        <MetricCard title="INTERVIEW" value={interviewScore} caption="From mentor mock interviews"
          tone={{ bg: "bg-blue-50", border: "border-blue-200", text: "text-blue-800" }} />
        <MetricCard title="PORTFOLIO" value={portfolioScore} caption="GitHub, demo, README, LinkedIn"
          tone={{ bg: "bg-indigo-50", border: "border-indigo-200", text: "text-indigo-800" }} />
        <MetricCard title="RESUME" value={resumeScore} caption="Completeness & role fit"
          tone={{ bg: "bg-violet-50", border: "border-violet-200", text: "text-violet-800" }} />

        <div className="rounded-2xl bg-amber-50 border border-amber-200 p-4 text-center flex flex-col justify-center">
          <p className="text-xs font-semibold tracking-wide text-amber-800">LEARN NEXT</p>
          <p className="text-lg font-extrabold text-amber-800 mt-1">{topMissingSkill ?? "—"}</p>
          <p className="text-xs text-amber-700 mt-1">
            {topMissingSkill
              ? "Most requested missing skill"
              : gapScore !== null && gapScore !== undefined
              ? "All required skills present"
              : "No skill gap data yet"}
          </p>
        </div>
      </div>
    </div>
  );
}
