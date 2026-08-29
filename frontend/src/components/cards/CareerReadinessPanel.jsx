/**
 * CareerReadinessPanel — Career readiness hero card + 5 meaningful metrics
 * Props: { readiness, jobs, days, interviewScore, portfolioScore, resumeScore, topMissingSkill }
 */
export default function CareerReadinessPanel({ 
  readiness, 
  jobs, 
  interviewScore, 
  portfolioScore, 
  resumeScore,
  topMissingSkill 
}) {
  return (
    <div className="mb-6">
      {/* Purple hero card */}
      <div className="rounded-2xl bg-gradient-to-br from-purple-100 to-purple-50 border border-purple-200 p-8 mb-4">
        <p className="text-sm font-semibold tracking-wide text-purple-800 mb-4">
          YOUR CAREER READINESS
        </p>
        <div className="flex items-center gap-8">
          <div>
            <p className="text-6xl font-extrabold text-purple-800 leading-none">
              {readiness}
              <span className="text-3xl align-top">%</span>
            </p>
            <p className="mt-2 text-purple-900 font-medium">Ready for target role</p>
          </div>
          <div className="flex-1 h-24 rounded-xl overflow-hidden flex">
            <div
              className="bg-purple-600 transition-all"
              style={{ width: `${Math.max(0, Math.min(100, readiness))}%` }}
            />
            <div
              className="bg-amber-500 transition-all"
              style={{ width: `${100 - Math.max(0, Math.min(100, readiness))}%` }}
            />
          </div>
        </div>
      </div>

      {/* 5 Metric Cards */}
      <div className="grid grid-cols-5 gap-3">

        {/* Jobs You Can Apply Now */}
        <div className="rounded-2xl bg-green-50 border border-green-200 p-4 text-center flex flex-col justify-center">
          <p className="text-xs font-semibold tracking-wide text-green-800">
            APPLY NOW
          </p>
          <p className="text-3xl font-extrabold text-green-800 mt-1">
            {jobs}
          </p>
          <p className="text-xs text-green-700 mt-1">Jobs matching</p>
        </div>

        {/* Interview Readiness */}
        <div className="rounded-2xl bg-blue-50 border border-blue-200 p-4 text-center flex flex-col justify-center">
          <p className="text-xs font-semibold tracking-wide text-blue-800">
            INTERVIEW
          </p>
          <p className="text-3xl font-extrabold text-blue-800 mt-1">
            {interviewScore ?? 0}
            <span className="text-sm font-normal">/100</span>
          </p>
          <p className="text-xs text-blue-700 mt-1">Readiness score</p>
        </div>

        {/* Portfolio Score */}
        <div className="rounded-2xl bg-indigo-50 border border-indigo-200 p-4 text-center flex flex-col justify-center">
          <p className="text-xs font-semibold tracking-wide text-indigo-800">
            PORTFOLIO
          </p>
          <p className="text-3xl font-extrabold text-indigo-800 mt-1">
            {portfolioScore ?? 0}
            <span className="text-sm font-normal">/100</span>
          </p>
          <p className="text-xs text-indigo-700 mt-1">GitHub & projects</p>
        </div>

        {/* Resume Score */}
        <div className="rounded-2xl bg-violet-50 border border-violet-200 p-4 text-center flex flex-col justify-center">
          <p className="text-xs font-semibold tracking-wide text-violet-800">
            RESUME
          </p>
          <p className="text-3xl font-extrabold text-violet-800 mt-1">
            {resumeScore ?? 0}
            <span className="text-sm font-normal">/100</span>
          </p>
          <p className="text-xs text-violet-700 mt-1">Role alignment</p>
        </div>

        {/* Top Skill to Learn */}
        <div className="rounded-2xl bg-amber-50 border border-amber-200 p-4 text-center flex flex-col justify-center">
          <p className="text-xs font-semibold tracking-wide text-amber-800">
            LEARN NEXT
          </p>
          <p className="text-lg font-extrabold text-amber-800 mt-1 capitalize">
            {topMissingSkill ?? "—"}
          </p>
          <p className="text-xs text-amber-700 mt-1">Top market skill</p>
        </div>

      </div>
    </div>
  );
}