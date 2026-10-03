import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import CareerReadinessPanel from '../components/cards/CareerReadinessPanel';
import SkillGapCard from '../components/cards/SkillGapCard';
import JobMatchCard from '../components/cards/JobMatchCard';
import NextStepsCard from '../components/cards/NextStepsCard';
import StudentEvidenceCard from '../components/cards/StudentEvidenceCard';
import MockInterviewForm from '../components/cards/MockInterviewForm';
import { useCPIP } from '../hooks/useCPIP';
import cpipApi from '../services/cpipApi';
import Fuse from 'fuse.js';

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
          Save
        </button>
        <button onClick={() => { setEditing(false); setInput(''); }}
          className="text-xs text-gray-400 hover:text-gray-600">Cancel</button>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm px-5 py-3 mb-3 flex items-center justify-between">
      <p className="text-sm text-gray-600">
        📍 Preferred location: <strong className="text-purple-700">{currentLocation || 'not set'}</strong>
        <span className="text-gray-400"> · jobs are matched on skills; use the location filter below to narrow them</span>
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
  const [refreshKey, setRefreshKey] = useState(0);
  const reload = () => setRefreshKey((k) => k + 1);

  const {
    readiness, calculation, scoresMissing, targetRole, jobs, skillsHave, skillsMissing, gapScore,
    skillGapMessage, basedOnPostings, jobMatches, actionPlans, profile,
    interviewScore, portfolioScore, resumeScore, topMissingSkill, loading, error,
  } = useCPIP(refreshKey);

  const [studentLocation, setStudentLocation] = useState('');
  const [locationError, setLocationError] = useState('');
  useEffect(() => {
    const loc = profile?.contact?.location;
    setStudentLocation(loc && loc.trim().toLowerCase() !== 'not specified' ? loc : '');
  }, [profile]);

  const handleLocationChange = async (newLoc) => {
    setLocationError('');
    try {
      await cpipApi.updateLocation(studentId, newLoc);
      setStudentLocation(newLoc);
    } catch (err) {
      setLocationError(err.message);
    }
  };

  // Filters
  const [locationFilter, setLocationFilter] = useState('');
  const [suitabilityFilter, setSuitabilityFilter] = useState('all');
  const [searchFilter, setSearchFilter] = useState('');
  const [workTypeFilter, setWorkTypeFilter] = useState('all');

  const uniqueSuitabilities = [...new Set(jobMatches.map(j => j.fit_category).filter(Boolean))];

  const filteredJobs = (() => {
    let filtered = jobMatches;
    if (suitabilityFilter !== 'all') filtered = filtered.filter(j => j.fit_category === suitabilityFilter);
    const isRemote = (j) => (j.location || '').toLowerCase().includes('remote');
    if (workTypeFilter === 'remote') filtered = filtered.filter(isRemote);
    else if (workTypeFilter === 'onsite') filtered = filtered.filter(j => !isRemote(j));
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

  if (loading) {
    return <div className="dashboard-container text-gray-500 text-sm p-8">Loading your readiness…</div>;
  }
  if (error) {
    return <div className="dashboard-container text-red-600 text-sm p-8">{error}</div>;
  }

  return (
    <div className="dashboard-container">
      <CareerReadinessPanel
        readiness={readiness} calculation={calculation} scoresMissing={scoresMissing} targetRole={targetRole} jobs={jobs}
        interviewScore={interviewScore} portfolioScore={portfolioScore}
        resumeScore={resumeScore} topMissingSkill={topMissingSkill} gapScore={gapScore}
      />

      <SkillGapCard
        skillsHave={skillsHave} skillsMissing={skillsMissing}
        score={gapScore} basedOnPostings={basedOnPostings} message={skillGapMessage}
      />

      <NextStepsCard actions={actionPlans} />

      <StudentEvidenceCard studentId={studentId} profile={profile} onSaved={reload} />

      <MockInterviewForm studentId={studentId} onSaved={reload} />

      <LocationBar
        currentLocation={studentLocation}
        onLocationChange={handleLocationChange}
      />
      {locationError && <p className="text-xs text-red-600 -mt-2 mb-3">{locationError}</p>}

      <div className="mt-4">
          <p className="text-sm font-semibold tracking-wide text-gray-500 mb-1">
            MATCHING ROLES ({filteredJobs.length} of {jobMatches.length})
          </p>
          <p className="text-xs text-gray-400 mb-3">
            Roles posted by recruiters on CPIP that match your skills. Matching is skills-only.
          </p>

          {jobMatches.length === 0 && (
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-8 text-center text-gray-500 text-sm">
              No matching roles yet. New roles appear here when recruiters post jobs that fit your skills.
            </div>
          )}

          {jobMatches.length > 0 && (<>

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
            <p className="text-gray-500 text-sm text-center py-8">No roles match your filters.</p>
          ) : (
            filteredJobs.map((match) => <JobMatchCard key={match.job_id} match={match} />)
          )}
          </>)}
      </div>

    </div>
  );
}