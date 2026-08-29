import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import CareerReadinessPanel from '../components/cards/CareerReadinessPanel';
import SkillGapCard from '../components/cards/SkillGapCard';
import JobMatchCard from '../components/cards/JobMatchCard';
import { useCPIP } from '../hooks/useCPIP';
import cpipApi from '../services/cpipApi';
import Fuse from 'fuse.js';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// ── Job Search Component ─────────────────────────────────────────
function JobSearch({ studentId, onRoleSearch }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [status, setStatus] = useState('idle');
  const [errorMessage, setErrorMessage] = useState('');

  const handleSearch = async () => {
    if (!query.trim()) return;
    setStatus('loading');
    setErrorMessage('');
    const roleGuess = query.trim().split(' ').slice(0, 2).join(' ');
    if (onRoleSearch) onRoleSearch(roleGuess);
    try {
      const data = await cpipApi.searchExternalJobs(query.trim(), studentId);
      if (data.detail) throw new Error(data.detail);
      setResults(data.jobs || []);
      setStatus('done');
    } catch (err) {
      setErrorMessage(err.message || 'Search failed.');
      setStatus('error');
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-4">
      <p className="font-semibold text-gray-900 mb-1">Search real listings</p>
      <p className="text-sm text-gray-500 mb-4">Live external jobs via Adzuna</p>
      <div className="flex gap-2 mb-4">
        <input type="text" value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          placeholder="e.g. python developer jobs in Kochi"
          className="flex-1 px-4 py-2 rounded-lg border-2 border-gray-200 focus:border-purple-500 focus:outline-none" />
        <button onClick={handleSearch}
          disabled={!query.trim() || status === 'loading'}
          className={`px-6 py-2 rounded-lg font-semibold ${query.trim() && status !== 'loading' ? 'bg-purple-600 text-white hover:bg-purple-700' : 'bg-gray-200 text-gray-500 cursor-not-allowed'}`}>
          {status === 'loading' ? 'Searching…' : 'Search'}
        </button>
      </div>
      {status === 'error' && <p className="text-red-600 text-sm">{errorMessage}</p>}
      {status === 'done' && results.length === 0 && <p className="text-gray-500 text-sm">No listings found.</p>}
      {status === 'done' && results.length > 0 && (
        <div className="space-y-3">
          {results.slice(0, 5).map((job) => (
            <div key={job.job_id} className="border border-gray-100 rounded-lg p-4">
              <div className="flex justify-between items-start gap-4">
                <div>
                  <p className="font-semibold text-gray-900">{job.title}</p>
                  <p className="text-sm text-gray-500">{job.company} • {job.location}</p>
                </div>
                {job.skill_overlap_percent != null && (
                  <span className="text-xs font-semibold px-2 py-1 rounded bg-blue-50 text-blue-700 shrink-0">
                    {job.skill_overlap_percent}% overlap
                  </span>
                )}
              </div>
              <a href={job.apply_link} target="_blank" rel="noopener noreferrer"
                className="text-sm text-purple-600 font-semibold mt-2 inline-block">View →</a>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Location Bar Component ───────────────────────────────────────
function LocationBar({ currentLocation, onLocationChange }) {
  const [editing, setEditing] = useState(false);
  const [input, setInput] = useState('');

  const handleSave = () => {
    if (!input.trim()) return;
    onLocationChange(input.trim().toLowerCase());
    setEditing(false);
    setInput('');
  };

  if (editing) {
    return (
      <div className="bg-white rounded-2xl border border-purple-200 shadow-sm px-5 py-3 mb-3 flex items-center gap-3">
        <span className="text-sm text-gray-600 shrink-0">📍 New location:</span>
        <input type="text" value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSave()}
          placeholder="e.g. bangalore, mumbai, delhi..."
          autoFocus
          className="flex-1 px-3 py-1.5 rounded-lg border border-purple-300 text-sm focus:border-purple-500 focus:outline-none" />
        <button onClick={handleSave} disabled={!input.trim()}
          className="px-4 py-1.5 bg-purple-600 text-white rounded-lg text-sm font-semibold hover:bg-purple-700 disabled:opacity-50">
          Find Jobs
        </button>
        <button onClick={() => { setEditing(false); setInput(''); }}
          className="text-xs text-gray-400 hover:text-gray-600">Cancel</button>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm px-5 py-3 mb-3 flex items-center justify-between">
      <p className="text-sm text-gray-600">
        📍 Showing jobs in <strong className="text-purple-700">{currentLocation || 'your location'}</strong>
      </p>
      <button onClick={() => setEditing(true)}
        className="text-xs text-purple-500 hover:text-purple-700 font-medium">
        Change location →
      </button>
    </div>
  );
}

// ── Main Dashboard ───────────────────────────────────────────────
export default function CandidateDashboard() {
  const { studentId } = useParams();
  const [searchedRole, setSearchedRole] = useState(null);
  const [preferredLocation, setPreferredLocation] = useState(null);
  const [studentLocation, setStudentLocation] = useState('');

  // Load student location on mount
  useEffect(() => {
    if (!studentId) return;
    fetch(`${API_BASE}/api/students/with-resumes`)
  .then(r => r.json())
  .then(data => {
    const student = (data.students || []).find(s => s.id === parseInt(studentId));
    const loc = student?.location || '';
        setStudentLocation(loc);
        if (loc && loc !== 'not specified') {
          setPreferredLocation(loc);
        }
      })
      .catch(() => {});
  }, [studentId]);

  const handleLocationChange = (newLoc) => {
    setStudentLocation(newLoc);
    setPreferredLocation(newLoc);
  };

  // Filters
  const [locationFilter, setLocationFilter] = useState('');
  const [suitabilityFilter, setSuitabilityFilter] = useState('all');
  const [searchFilter, setSearchFilter] = useState('');
  const [workTypeFilter, setWorkTypeFilter] = useState('all');

  const {
    readiness, jobs, skillsHave, skillsMissing, gapScore,
    skillGapSupported, basedOnPostings, resumeQuality, jobMatches,
    interviewScore, portfolioScore, resumeScore, topMissingSkill,
  } = useCPIP(searchedRole, preferredLocation);

  const uniqueSuitabilities = [...new Set(jobMatches.map(j => j.suitability).filter(Boolean))];

  const filteredJobs = (() => {
    let filtered = jobMatches;
    if (suitabilityFilter !== 'all') filtered = filtered.filter(j => j.suitability === suitabilityFilter);
    if (workTypeFilter === 'remote') filtered = filtered.filter(j => j.is_remote === true);
    else if (workTypeFilter === 'onsite') filtered = filtered.filter(j => j.is_remote === false);
    if (searchFilter) filtered = filtered.filter(j =>
      j.job_title?.toLowerCase().includes(searchFilter.toLowerCase()) ||
      j.company_name?.toLowerCase().includes(searchFilter.toLowerCase())
    );
    if (locationFilter.trim()) {
      const fuse = new Fuse(filtered, { keys: ['location'], threshold: 0.4, includeScore: true });
      filtered = fuse.search(locationFilter.trim()).map(r => r.item);
    }
    return filtered;
  })();

  const hasActiveFilters = locationFilter || suitabilityFilter !== 'all' || searchFilter || workTypeFilter !== 'all';

  return (
    <div className="dashboard-container">
      <CareerReadinessPanel
        readiness={readiness} jobs={jobs}
        interviewScore={interviewScore} portfolioScore={portfolioScore}
        resumeScore={resumeScore} topMissingSkill={topMissingSkill}
      />

      {skillGapSupported && (
        <SkillGapCard
          skillsHave={skillsHave} skillsMissing={skillsMissing}
          score={gapScore} basedOnPostings={basedOnPostings} resumeQuality={resumeQuality}
        />
      )}

      {/* Location bar — always visible */}
      <LocationBar
        currentLocation={studentLocation}
        onLocationChange={handleLocationChange}
      />

      {jobMatches.length > 0 && (
        <div className="mt-4">
          <p className="text-sm font-semibold tracking-wide text-gray-500 mb-3">
            JOB MATCHES ({filteredJobs.length} of {jobMatches.length})
          </p>

          {/* Filters */}
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-4 mb-4">
            <div className="flex flex-wrap gap-3">
              <input type="text" placeholder="🔍 Search job title or company..."
                value={searchFilter} onChange={(e) => setSearchFilter(e.target.value)}
                className="flex-1 min-w-48 px-3 py-2 rounded-lg border border-gray-200 text-sm focus:border-purple-500 focus:outline-none" />
              <input type="text" placeholder="📍 Filter results by location..."
                value={locationFilter} onChange={(e) => setLocationFilter(e.target.value)}
                className="flex-1 min-w-48 px-3 py-2 rounded-lg border border-gray-200 text-sm focus:border-purple-500 focus:outline-none" />
              <select value={workTypeFilter} onChange={(e) => setWorkTypeFilter(e.target.value)}
                className="px-3 py-2 rounded-lg border border-gray-200 text-sm focus:border-purple-500 focus:outline-none">
                <option value="all">💼 All Work Types</option>
                <option value="remote">🏠 Remote</option>
                <option value="hybrid">🔄 Hybrid</option>
                <option value="onsite">🏢 On-site</option>
              </select>
              <select value={suitabilityFilter} onChange={(e) => setSuitabilityFilter(e.target.value)}
                className="px-3 py-2 rounded-lg border border-gray-200 text-sm focus:border-purple-500 focus:outline-none">
                <option value="all">⭐ All Fits</option>
                {uniqueSuitabilities.map((s, i) => <option key={i} value={s}>{s}</option>)}
              </select>
              {hasActiveFilters && (
                <button onClick={() => { setLocationFilter(''); setSuitabilityFilter('all'); setSearchFilter(''); setWorkTypeFilter('all'); }}
                  className="px-3 py-2 rounded-lg border border-red-200 text-red-600 text-sm hover:bg-red-50">
                  ✕ Reset
                </button>
              )}
            </div>
          </div>

          {filteredJobs.length === 0 ? (
            <p className="text-gray-500 text-sm text-center py-8">No jobs match your filters.</p>
          ) : (
            filteredJobs.map((match, i) => <JobMatchCard key={i} match={match} />)
          )}
        </div>
      )}

      <JobSearch studentId={studentId} onRoleSearch={setSearchedRole} />
    </div>
  );
}