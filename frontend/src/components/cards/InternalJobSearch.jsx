import { useState, useEffect } from 'react';
import cpipApi from '../../services/cpipApi';

/**
 * InternalJobSearch — lets a student browse/search ALL internally posted
 * jobs (recruiter postings), separate from their personalized JobMatchCard
 * list (which only shows fit-scored matches). Case-insensitive search
 * across title, company, location, and skills — same logic as the
 * recruiter dashboard's search, backed by the same seed_data.search_jobs().
 */
export default function InternalJobSearch() {
  const [allJobs, setAllJobs] = useState([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    cpipApi.getAllJobs().then((data) => {
      if (!cancelled) {
        setAllJobs(data.jobs || []);
        setLoading(false);
      }
    });
    return () => { cancelled = true; };
  }, []);

  const filtered = allJobs.filter((job) => {
    if (!query.trim()) return true;
    const q = query.trim().toLowerCase();
    const haystack = [
      job.job_title,
      job.company_name,
      job.location,
      ...(job.required_skills || []),
      ...(job.preferred_skills || []),
    ].join(' ').toLowerCase();
    return haystack.includes(q);
  });

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-4">
      <p className="font-semibold text-gray-900 mb-1">Browse all posted jobs</p>
      <p className="text-sm text-gray-500 mb-4">
        Search internal postings by title, company, location, or skill — case doesn't matter.
      </p>

      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="e.g. python, TechCorp, Kochi"
        className="w-full px-4 py-2 rounded-lg border-2 border-gray-200 focus:border-purple-500 focus:outline-none mb-4"
      />

      {loading && <p className="text-gray-400 text-sm">Loading jobs…</p>}

      {!loading && filtered.length === 0 && (
        <p className="text-gray-500 text-sm">No jobs match "{query}".</p>
      )}

      {!loading && filtered.length > 0 && (
        <div className="space-y-3">
          {filtered.map((job) => (
            <div key={job.id} className="border border-gray-100 rounded-lg p-4">
              <p className="font-semibold text-gray-900">{job.job_title}</p>
              <p className="text-sm text-gray-500">{job.company_name} • {job.location}</p>
              {job.required_skills && job.required_skills.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {job.required_skills.map((s) => (
                    <span key={s} className="px-2 py-1 rounded bg-red-50 text-red-700 text-xs font-medium">
                      {s}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}