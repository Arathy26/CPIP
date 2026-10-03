import React, { useState, useEffect } from 'react';
import { Plus, TrendingUp, X, Upload } from 'lucide-react';
import cpipApi from '../services/cpipApi';

/**
 * ============================================================================
 * RECRUITER DASHBOARD - Job Posting & Candidate Matching
 * ============================================================================
 */

function mapJob(apiJob) {
  return {
    id: apiJob.id,
    title: apiJob.title,
    company: apiJob.company_name,
    location: apiJob.location || '',
    employmentType: apiJob.employment_type || 'Full-Time',
    requiredSkills: apiJob.required_skills || [],
    preferredSkills: apiJob.preferred_skills || [],
    description: apiJob.description || '',
    experience: apiJob.experience_level || 'Not specified',
    postedDate: apiJob.created_at ? new Date(apiJob.created_at).toLocaleDateString() : 'Unknown',
  };
}

function jobMatchesSearch(job, query) {
  if (!query.trim()) return true;
  const q = query.trim().toLowerCase();
  const haystack = [
    job.title,
    job.company,
    job.location,
    job.employmentType,
    ...job.requiredSkills,
    ...job.preferredSkills,
  ].join(' ').toLowerCase();
  return haystack.includes(q);
}

// Fit categories come from the backend recruiter_matching_agent (same rules as the candidate side).
const SUITABILITY_STYLES = {
  'Strong Fit': 'bg-emerald-100 text-emerald-800',
  'Good Fit': 'bg-blue-100 text-blue-800',
  'Stretch Fit': 'bg-amber-100 text-amber-800',
  'Not Suitable Yet': 'bg-gray-100 text-gray-700',
};

function mapCandidateMatch(match) {
  return {
    id: match.student_id,
    name: match.name || 'Candidate',
    degree: match.degree || 'Not specified',
    cgpa: match.cgpa,
    fit: match.fit_score,
    fitStatus: match.fit_category,
    fitColor: SUITABILITY_STYLES[match.fit_category] || SUITABILITY_STYLES['Not Suitable Yet'],
    reason: match.reason,
    skillMatch: {
      have: [...(match.matched_required_skills || []), ...(match.matched_preferred_skills || [])],
      missing: match.missing_required_skills || [],
      missingPreferred: match.missing_preferred_skills || [],
    },
  };
}

export default function RecruiterDashboard() {
  const [jobs, setJobs] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedJob, setSelectedJob] = useState(null);
  const [matches, setMatches] = useState([]);
  const [loadingJobs, setLoadingJobs] = useState(true);
  const [loadingMatches, setLoadingMatches] = useState(false);
  const [showJobForm, setShowJobForm] = useState(false);
  const [showBulkForm, setShowBulkForm] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadJobs();
  }, []);

  async function loadJobs() {
    try {
      setLoadingJobs(true);
      setError(null);
      const result = await cpipApi.getAllJobs();
      const mappedJobs = (result.jobs || []).map(mapJob);
      setJobs(mappedJobs);

      if (mappedJobs.length > 0) {
        selectJob(mappedJobs[0]);
      } else {
        setSelectedJob(null);
        setMatches([]);
      }
    } catch (err) {
      console.error('Failed to load jobs:', err);
      setError('Failed to load job opportunities. Is the backend awake?');
    } finally {
      setLoadingJobs(false);
    }
  }

  async function selectJob(job) {
    setSelectedJob(job);
    setLoadingMatches(true);
    try {
      const result = await cpipApi.getMatchedCandidates(job.id);
      setMatches((result.candidates || []).map(mapCandidateMatch));
    } catch (err) {
      console.error('Failed to load matches:', err);
      setMatches([]);
    } finally {
      setLoadingMatches(false);
    }
  }

  async function handleJobPosted(newJob) {
    setShowJobForm(false);
    await loadJobs();
    selectJob(mapJob(newJob));
  }

  async function handleJobUpdated(updatedJob) {
    setShowEditForm(false);
    await loadJobs();
    selectJob(mapJob(updatedJob));
  }
  async function handleDeleteJob() {
    if (!window.confirm('Close this job? Candidates will no longer see it.')) return;
    try {
      await cpipApi.deleteJob(selectedJob.id);
      await loadJobs();
    } catch (err) {
      setError('Failed to close job');
    }
  }


  if (loadingJobs) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 p-8 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600 font-medium">Loading job opportunities…</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 p-8">
        <div className="max-w-7xl mx-auto bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800 font-medium">{error}</p>
          <button
            onClick={loadJobs}
            className="mt-4 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Recruiter Portal</h1>
            <p className="text-gray-600 mt-2">Post jobs and find matched candidates</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => { setShowBulkForm(!showBulkForm); setShowJobForm(false); }}
              className="bg-white border-2 border-blue-600 text-blue-700 hover:bg-blue-50 px-6 py-3 rounded-lg font-semibold flex items-center gap-2 transition-colors"
            >
              <Upload size={20} />
              Bulk Upload
            </button>
            <button
              onClick={() => { setShowJobForm(!showJobForm); setShowBulkForm(false); }}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold flex items-center gap-2 transition-colors"
            >
              <Plus size={20} />
              Post a Job
            </button>
          </div>
        </div>

        {showBulkForm && (
          <BulkUploadForm onClose={() => setShowBulkForm(false)} onUploaded={loadJobs} />
        )}

        {showJobForm && (
          <JobPostingForm onClose={() => setShowJobForm(false)} onPosted={handleJobPosted} />
        )}

        {showEditForm && selectedJob && (
          <EditJobForm 
            job={selectedJob} 
            onClose={() => setShowEditForm(false)} 
            onUpdated={handleJobUpdated} 
          />
        )}

        {jobs.length === 0 && !showJobForm && !showBulkForm && (
          <div className="bg-white rounded-2xl shadow p-8 text-center text-gray-500">
            No jobs posted yet. Click "Post a Job" or "Bulk Upload" to add jobs.
          </div>
        )}

        {jobs.length > 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            <div className="lg:col-span-1">
              <div className="bg-white rounded-2xl shadow p-6 sticky top-8">
                <h2 className="text-lg font-bold text-gray-900 mb-4">Posted Jobs</h2>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search title, company, skills…"
                  className="w-full mb-4 px-3 py-2 rounded-lg border-2 border-gray-200 focus:border-blue-500 focus:outline-none text-sm"
                />
                <div className="space-y-3">
                  {jobs.filter((job) => jobMatchesSearch(job, searchQuery)).length === 0 && (
                    <p className="text-sm text-gray-400">No jobs match "{searchQuery}".</p>
                  )}
                  {jobs.filter((job) => jobMatchesSearch(job, searchQuery)).map((job) => (
                    <button
                      key={job.id}
                      onClick={() => selectJob(job)}
                      className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
                        selectedJob?.id === job.id
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-50 text-gray-900 hover:bg-gray-100'
                      }`}
                    >
                      <p className="font-semibold text-sm">{job.title}</p>
                      <p className={`text-xs mt-1 ${selectedJob?.id === job.id ? 'text-blue-100' : 'text-gray-600'}`}>
                        {job.company}
                      </p>
                      <div className={`text-xs font-bold mt-2 flex items-center gap-1 ${
                        selectedJob?.id === job.id ? 'text-blue-100' : 'text-blue-600'
                      }`}>
                        <TrendingUp size={14} />
                        {job.requiredSkills.length} required skill{job.requiredSkills.length === 1 ? '' : 's'}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="lg:col-span-3">
              {selectedJob && (
                <>
                  <div className="bg-white rounded-2xl shadow p-8 mb-8 border border-gray-100">
                    <div className="flex items-start justify-between mb-6">
                      <div>
                        <h2 className="text-2xl font-bold text-gray-900">{selectedJob.title}</h2>
                        <p className="text-gray-600 mt-2">{selectedJob.company}</p>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => setShowEditForm(true)}
                          className="bg-amber-500 hover:bg-amber-600 text-white px-4 py-2 rounded-lg font-semibold transition-colors"
                        >
                          Edit Job
                        </button>
                        <button
                          onClick={handleDeleteJob}
                          className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg font-semibold transition-colors"
                        >
                          Close Job
                        </button>
                        <span className="bg-blue-100 text-blue-800 px-4 py-2 rounded-lg font-semibold">
                          {matches.length} Candidate{matches.length === 1 ? '' : 's'}
                        </span>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                      <div>
                        <p className="text-gray-600 text-sm font-semibold">Required Skills</p>
                        <div className="flex flex-wrap gap-2 mt-2">
                          {selectedJob.requiredSkills.map((skill) => (
                            <span key={skill} className="bg-red-50 text-red-700 text-xs px-2 py-1 rounded font-medium">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div>
                        <p className="text-gray-600 text-sm font-semibold">Preferred Skills</p>
                        <div className="flex flex-wrap gap-2 mt-2">
                          {selectedJob.preferredSkills.length === 0 && <span className="text-xs text-gray-400">None</span>}
                          {selectedJob.preferredSkills.map((skill) => (
                            <span key={skill} className="bg-blue-50 text-blue-700 text-xs px-2 py-1 rounded font-medium">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div>
                        <p className="text-gray-600 text-sm font-semibold">Experience</p>
                        <p className="text-sm font-semibold text-gray-900 mt-2">{selectedJob.experience}</p>
                      </div>
                      <div>
                        <p className="text-gray-600 text-sm font-semibold">Location</p>
                        <p className="text-sm font-semibold text-gray-900 mt-2">{selectedJob.location}</p>
                      </div>
                      <div>
                        <p className="text-gray-600 text-sm font-semibold">Employment</p>
                        <p className="text-sm font-semibold text-gray-900 mt-2">{selectedJob.employmentType}</p>
                      </div>
                      <div>
                        <p className="text-gray-600 text-sm font-semibold">Posted</p>
                        <p className="text-sm font-semibold text-gray-900 mt-2">{selectedJob.postedDate}</p>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-2xl font-bold text-gray-900 mb-6">Auto-Matched Candidates</h3>

                    {loadingMatches && (
                      <p className="text-gray-500">Loading matches…</p>
                    )}

                    {!loadingMatches && matches.length === 0 && (
                      <div className="bg-white rounded-2xl shadow p-8 text-center text-gray-500">
                        No candidates match this job yet. Candidates appear here when their skills and eligibility fit the posting.
                      </div>
                    )}

                    <div className="space-y-4">
                      {matches.map((candidate) => (
                        <CandidateMatchCard key={candidate.id} candidate={candidate} />
                      ))}
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function CandidateMatchCard({ candidate }) {
  const nameParts = candidate.name.trim().split(' ').filter(Boolean);
  const initials =
    nameParts.length > 1
      ? nameParts[0].charAt(0) + nameParts[1].charAt(0)
      : nameParts[0]?.charAt(0) || '?';

  return (
    <div className="bg-white rounded-2xl shadow hover:shadow-lg transition-shadow overflow-hidden border border-gray-100">
      <div className="p-8">
        <div className="flex items-start justify-between mb-6">
          <div className="flex-1">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center text-white font-bold text-lg">
                {initials.toUpperCase()}
              </div>
              <div>
                <h4 className="text-lg font-bold text-gray-900">{candidate.name}</h4>
                <p className="text-gray-600 text-sm">
                  {candidate.degree} • CGPA {candidate.cgpa}
                </p>
              </div>
            </div>
          </div>

          <div className={`${candidate.fitColor} px-6 py-4 rounded-xl text-center flex-shrink-0 font-bold`}>
            <p className="text-sm">{candidate.fitStatus}</p>
            <p className="text-3xl mt-1">{candidate.fit}%</p>
            <p className="text-xs mt-2">fit score</p>
          </div>
        </div>

        {candidate.reason && (
          <p className="text-sm text-gray-700 bg-gray-50 rounded-lg p-3 mb-4">{candidate.reason}</p>
        )}

        <div className="mb-6 pb-6 border-b border-gray-200">
          <p className="text-sm font-semibold text-gray-900 mb-3">Skills Match</p>

          {candidate.skillMatch.have.length > 0 && (
            <div className="mb-3">
              <p className="text-xs text-gray-600 mb-2">Have: ({candidate.skillMatch.have.length})</p>
              <div className="flex flex-wrap gap-2">
                {candidate.skillMatch.have.map((skill) => (
                  <span key={skill} className="bg-green-100 text-green-800 text-xs px-3 py-1 rounded-full font-medium">
                    ✓ {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {candidate.skillMatch.missing.length > 0 && (
            <div>
              <p className="text-xs text-gray-600 mb-2">Missing required: ({candidate.skillMatch.missing.length})</p>
              <div className="flex flex-wrap gap-2">
                {candidate.skillMatch.missing.map((skill) => (
                  <span key={skill} className="bg-amber-100 text-amber-800 text-xs px-3 py-1 rounded-full font-medium">
                    ⚠ {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {candidate.skillMatch.missingPreferred.length > 0 && (
            <p className="text-xs text-gray-500 mt-3">
              Missing preferred: {candidate.skillMatch.missingPreferred.join(', ')}
            </p>
          )}
        </div>

        <div className="flex gap-3 pt-6 border-t border-gray-200">
          <button className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-semibold transition-colors">
            Shortlist candidate
          </button>
          <button className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-900 px-4 py-2 rounded-lg font-semibold transition-colors">
            View full profile
          </button>
        </div>
      </div>
    </div>
  );
}

function JobPostingForm({ onClose, onPosted }) {
  const [jobData, setJobData] = useState({
    title: '',
    company: '',
    location: '',
    requiredSkills: '',
    preferredSkills: '',
    description: '',
    experience: 'Fresher',
    employmentType: 'Full-Time',
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    const requiredSkills = splitSkills(jobData.requiredSkills);
    if (!jobData.title.trim() || !jobData.company.trim() || !jobData.location.trim()) {
      setError('Job title, company name and location are required.');
      return;
    }
    if (requiredSkills.length === 0) {
      setError('Add at least one required skill — matching uses it.');
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      const result = await cpipApi.postJob({
        title: jobData.title.trim(),
        company_name: jobData.company.trim(),
        location: jobData.location.trim(),
        required_skills: requiredSkills,
        preferred_skills: splitSkills(jobData.preferredSkills),
        description: jobData.description.trim() || null,
        experience_level: jobData.experience,
        employment_type: jobData.employmentType,
      });

      if (result.detail) {
        throw new Error(formatApiError(result.detail));
      }

      onPosted(result.job);
    } catch (err) {
      console.error('Failed to post job:', err);
      setError(err.message || 'Failed to post job.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow p-8 mb-8 border border-gray-100">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Post a Job Opportunity</h2>
        <button onClick={onClose} className="text-gray-600 hover:text-gray-900 text-2xl">
          <X size={24} />
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-800 text-sm font-medium">{error}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-semibold text-gray-900 mb-2">Job Title *</label>
          <input
            type="text"
            value={jobData.title}
            onChange={(e) => setJobData({ ...jobData, title: e.target.value })}
            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
            placeholder="e.g. Junior Backend Developer"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-900 mb-2">Company Name *</label>
          <input
            type="text"
            value={jobData.company}
            onChange={(e) => setJobData({ ...jobData, company: e.target.value })}
            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
            placeholder="e.g. TechCorp"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-900 mb-2">Location *</label>
          <input
            type="text"
            value={jobData.location}
            onChange={(e) => setJobData({ ...jobData, location: e.target.value })}
            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
            placeholder="e.g. Kochi, Bangalore, Remote"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-900 mb-2">Required Skills * (comma-separated)</label>
          <input
            type="text"
            value={jobData.requiredSkills}
            onChange={(e) => setJobData({ ...jobData, requiredSkills: e.target.value })}
            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
            placeholder="Python, FastAPI, SQL"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-900 mb-2">Preferred Skills (comma-separated)</label>
          <input
            type="text"
            value={jobData.preferredSkills}
            onChange={(e) => setJobData({ ...jobData, preferredSkills: e.target.value })}
            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
            placeholder="Docker, AWS"
          />
        </div>

        <div className="md:col-span-2">
          <label className="block text-sm font-semibold text-gray-900 mb-2">Job Description</label>
          <textarea
            value={jobData.description}
            onChange={(e) => setJobData({ ...jobData, description: e.target.value })}
            rows={3}
            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
            placeholder="Responsibilities, team, what the role involves"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-900 mb-2">Experience Level</label>
          <select
            value={jobData.experience}
            onChange={(e) => setJobData({ ...jobData, experience: e.target.value })}
            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
          >
            <option>Fresher</option>
            <option>0-1 years</option>
            <option>1-3 years</option>
            <option>3+ years</option>
          </select>
        </div>


        <div>
          <label className="block text-sm font-semibold text-gray-900 mb-2">Employment Type *</label>
          <select
            value={jobData.employmentType}
            onChange={(e) => setJobData({ ...jobData, employmentType: e.target.value })}
            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
          >
            <option value="Internship">Internship</option>
            <option value="Full-Time">Full-Time</option>
            <option value="Part-Time">Part-Time</option>
          </select>
        </div>
      </div>

      <button
        onClick={handleSubmit}
        disabled={submitting}
        className={`mt-6 w-full px-6 py-3 rounded-lg font-semibold transition-colors ${
          submitting
            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
            : 'bg-blue-600 hover:bg-blue-700 text-white'
        }`}
      >
        {submitting ? 'Posting…' : 'Post Job & See Matched Candidates'}
      </button>
    </div>
  );
}

function EditJobForm({ job, onClose, onUpdated }) {
  const [jobData, setJobData] = useState({
    title: job.title,
    location: job.location,
    requiredSkills: job.requiredSkills.join(', '),
    preferredSkills: job.preferredSkills.join(', '),
    experience: job.experience,
    employmentType: job.employmentType,
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    if (!jobData.title.trim()) {
      setError('Job title is required.');
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      const result = await cpipApi.updateJob(job.id, {
        title: jobData.title.trim(),
        location: jobData.location.trim(),
        required_skills: splitSkills(jobData.requiredSkills),
        preferred_skills: splitSkills(jobData.preferredSkills),
        experience_level: jobData.experience,
        employment_type: jobData.employmentType,
      });

      if (result.detail) {
        throw new Error(formatApiError(result.detail));
      }

      onUpdated(result.job);
    } catch (err) {
      console.error('Failed to update job:', err);
      setError(err.message || 'Failed to update job.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Edit Job: {job.title}</h2>
          <button onClick={onClose} className="text-gray-600 hover:text-gray-900 text-2xl">
            <X size={24} />
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800 text-sm font-medium">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">Job Title</label>
            <input
              type="text"
              value={jobData.title}
              onChange={(e) => setJobData({ ...jobData, title: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">Location</label>
            <input
              type="text"
              value={jobData.location}
              onChange={(e) => setJobData({ ...jobData, location: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
            />
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-semibold text-gray-900 mb-2">Required Skills (comma-separated)</label>
            <input
              type="text"
              value={jobData.requiredSkills}
              onChange={(e) => setJobData({ ...jobData, requiredSkills: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
            />
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-semibold text-gray-900 mb-2">Preferred Skills (comma-separated)</label>
            <input
              type="text"
              value={jobData.preferredSkills}
              onChange={(e) => setJobData({ ...jobData, preferredSkills: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">Experience Level</label>
            <select
              value={jobData.experience}
              onChange={(e) => setJobData({ ...jobData, experience: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
            >
              <option>Fresher</option>
              <option>0-1 years</option>
              <option>1-3 years</option>
              <option>3+ years</option>
            </select>
          </div>


          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">Employment Type</label>
            <select
              value={jobData.employmentType}
              onChange={(e) => setJobData({ ...jobData, employmentType: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
            >
              <option value="Internship">Internship</option>
              <option value="Full-Time">Full-Time</option>
              <option value="Part-Time">Part-Time</option>
            </select>
          </div>
        </div>

        <div className="flex gap-3 mt-6">
          <button
            onClick={handleSubmit}
            disabled={submitting}
            className={`flex-1 px-6 py-3 rounded-lg font-semibold transition-colors ${
              submitting
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            }`}
          >
            {submitting ? 'Updating…' : 'Update Job'}
          </button>
          <button
            onClick={onClose}
            className="flex-1 px-6 py-3 rounded-lg font-semibold bg-gray-200 text-gray-900 hover:bg-gray-300 transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Helpers ──────────────────────────────────────────────────────
function splitSkills(text) {
  return (text || '').split(',').map((s) => s.trim()).filter(Boolean);
}

// FastAPI returns `detail` as a string or as a list of validation errors.
function formatApiError(detail) {
  if (Array.isArray(detail)) {
    return detail
      .map((d) => `${(d.loc || []).slice(1).join('.')}: ${(d.msg || '').replace('Value error, ', '')}`)
      .join('; ');
  }
  return String(detail);
}

// ── Bulk upload (CSV) ────────────────────────────────────────────
const BULK_TEMPLATE =
  'job_title,company_name,location,required_skills,preferred_skills,experience_level,employment_type,description,salary_range\n' +
  'Junior Backend Developer,DemoCo,Kochi,"Python, FastAPI, SQL",Docker,Fresher,Full-Time,Build REST APIs,\n';

function BulkUploadForm({ onClose, onUploaded }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const downloadTemplate = () => {
    const blob = new Blob([BULK_TEMPLATE], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'cpip_bulk_jobs_template.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);
    setResult(null);
    try {
      const data = await cpipApi.bulkUploadJobs(file);
      if (data.detail) throw new Error(formatApiError(data.detail));
      setResult(data);
      if (data.saved_count > 0) await onUploaded();
    } catch (err) {
      setError(err.message || 'Upload failed.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow p-8 mb-8 border border-gray-100">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-gray-900">Bulk Upload Jobs (CSV)</h2>
        <button onClick={onClose} className="text-gray-600 hover:text-gray-900">
          <X size={24} />
        </button>
      </div>

      <p className="text-sm text-gray-600 mb-2">
        Required columns: <code>job_title, company_name, location, required_skills</code>.
        Optional: <code>preferred_skills, experience_level, employment_type, description, salary_range</code>.
      </p>
      <p className="text-sm text-gray-600 mb-4">
        Put several skills in one cell inside quotes, e.g. <code>"Python, FastAPI, SQL"</code>.
        Each row is checked separately — valid rows are saved even if some rows have errors.
      </p>

      <button onClick={downloadTemplate} className="text-sm text-blue-600 font-semibold mb-4 hover:underline">
        ⬇ Download CSV template
      </button>

      <div className="flex gap-3 items-center">
        <input
          type="file"
          accept=".csv"
          onChange={(e) => { setFile(e.target.files?.[0] || null); setResult(null); setError(null); }}
          className="flex-1 text-sm"
        />
        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className={`px-6 py-2 rounded-lg font-semibold ${
            file && !uploading ? 'bg-blue-600 hover:bg-blue-700 text-white' : 'bg-gray-200 text-gray-500 cursor-not-allowed'
          }`}
        >
          {uploading ? 'Uploading…' : 'Upload'}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mt-4">
          <p className="text-red-800 text-sm font-medium">{error}</p>
        </div>
      )}

      {result && (
        <div className="mt-6 space-y-4">
          <p className="font-semibold text-gray-900">{result.message}</p>

          {result.jobs.length > 0 && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <p className="text-sm font-semibold text-green-800 mb-2">Saved</p>
              <ul className="text-sm text-green-900 space-y-1">
                {result.jobs.map((j) => (
                  <li key={j.id}>✓ {j.title} — {j.company_name} ({j.matched_candidates_count} candidate{j.matched_candidates_count === 1 ? '' : 's'} matched)</li>
                ))}
              </ul>
            </div>
          )}

          {result.errors.length > 0 && (
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
              <p className="text-sm font-semibold text-amber-800 mb-2">Rejected rows — fix and upload these again</p>
              <ul className="text-sm text-amber-900 space-y-1">
                {result.errors.map((e) => (
                  <li key={e.row}>Row {e.row}{e.job_title ? ` (${e.job_title})` : ''}: {e.error}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
