import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import cpipApi from '../../services/cpipApi';

export default function MarketSkillGapCard() {
  const { studentId } = useParams();
  const [data, setData] = useState(null);
  const [status, setStatus] = useState('loading');

  useEffect(() => {
    let cancelled = false;
    cpipApi.getMarketSkillGap(studentId)
      .then((res) => {
        if (cancelled) return;
        if (res.detail) {
          setStatus('error');
          return;
        }
        setData(res);
        setStatus(res.supported ? 'done' : 'unsupported');
      })
      .catch(() => {
        if (!cancelled) setStatus('error');
      });
    return () => { cancelled = true; };
  }, [studentId]);

  if (status === 'loading') {
    return (
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-4">
        <p className="text-gray-400 text-sm">Comparing your resume against real market postings…</p>
      </div>
    );
  }

  if (status === 'error') return null;

  if (status === 'unsupported') {
    return (
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-4">
        <p className="text-sm text-gray-500">{data?.message}</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-4">
      <div className="flex items-center justify-between mb-3">
        <div>
          <p className="font-semibold text-gray-900">Market Skill Demand</p>
          <p className="text-xs text-gray-500">
            Based on {data.based_on_postings} real "{data.target_role}" postings right now
          </p>
        </div>
        <span className="text-2xl font-bold text-purple-700">{data.market_fit_score}%</span>
      </div>

      {data.missing_skills.length > 0 && (
        <div className="mb-3">
          <p className="text-xs font-semibold tracking-wide text-gray-500 mb-2">
            MISSING — RANKED BY REAL MARKET DEMAND
          </p>
          <div className="flex flex-wrap gap-2">
            {data.missing_skills.slice(0, 8).map((s) => (
              <span
                key={s.skill}
                className="px-2 py-1 rounded bg-amber-50 text-amber-700 text-xs font-medium"
              >
                {s.skill} — {s.demand_percent}% of postings need it
              </span>
            ))}
          </div>
        </div>
      )}

      {data.matched_skills.length > 0 && (
        <div className="mb-3">
          <p className="text-xs font-semibold tracking-wide text-gray-500 mb-2">YOU HAVE</p>
          <div className="flex flex-wrap gap-2">
            {data.matched_skills.slice(0, 8).map((s) => (
              <span
                key={s.skill}
                className="px-2 py-1 rounded bg-green-50 text-green-700 text-xs font-medium"
              >
                ✓ {s.skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {data.resume_quality && (
        <div className="mt-3 bg-purple-50 rounded-lg p-3">
          <p className="text-xs font-semibold tracking-wide text-purple-800 mb-1">RESUME QUALITY</p>
          <p className="text-sm text-purple-900 mb-1">
            Score: <strong>{data.resume_quality.resume_score}/100</strong>
          </p>
          {data.resume_quality.improvement_tips.slice(0, 3).map((tip, i) => (
            <p key={i} className="text-sm text-purple-700 mt-1">⚠ {tip}</p>
          ))}
        </div>
      )}
    </div>
  );
}