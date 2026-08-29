import React, { useState, useEffect } from 'react';
import { Plus, TrendingUp, X } from 'lucide-react';
import cpipApi from '../services/cpipApi';

/**
 * ============================================================================
 * RECRUITER DASHBOARD - Job Posting & Candidate Matching
 * ============================================================================
 */

function mapJob(apiJob) {
  return {
    id: apiJob.id,
    title: apiJob.job_title,
    company: apiJob.company_name,
    location: apiJob.location || '',
    jobType: apiJob.job_type || 'Remote',
    employmentType: apiJob.employment_type || 'Full-Time',
    requiredSkills: apiJob.required_skills || [],
    preferredSkills: apiJob.preferred_skills || [],
    minCGPA: apiJob.min_cgpa,
    experience: apiJob.experience_level || 'Not specified',
    postedDate: apiJob.posted_date || 'Unknown',
  };
}

function jobMatchesSearch(job, query) {
  if (!query.trim()) return true;
  const q = query.trim().toLowerCase();
  const haystack = [
    job.title,
    job.company,
    job.location,
    job.jobType,
    job.employmentType,
    ...job.requiredSkills,
    ...job.preferredSkills,
  ].join(' ').toLowerCase();
  return haystack.includes(q);
}

const SUITABILITY_STYLES = {
  'Perfect Match': 'bg-emerald-100 text-emerald-800',
  'High Match': 'bg-blue-100 text-blue-800',
  'Medium Match': 'bg-amber-100 text-amber-800',
  'Low Match': 'bg-gray-100 text-gray-700',
};

function mapCandidateMatch(match) {
  return {
    id: match.candidate_id,
    name: match.candidate_name || 'Candidate',
    degree: match.degree || 'Not specified',
    cgpa: match.cgpa,
    fit: match.fit_score,
    fitStatus: match.suitability,
    fitColor: SUITABILITY_STYLES[match.suitability] || SUITABILITY_STYLES['Low Match'],
    skillMatch: {
      have: match.required_skills_matched || [],
      missing: match.required_skills_missing || [],
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
      setMatches((result.candidate_matches || []).map(mapCandidateMatch));
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
    if (!window.confirm('Are you sure you want to delete this job?')) return;
    try {
      await cpipApi.deleteJob(selectedJob.id);
      await loadJobs();
      setSelectedJob(null);
    } catch (err) {
      setError('Failed to delete job');
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
          <button
            onClick={() => setShowJobForm(!showJobForm)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold flex items-center gap-2 transition-colors"
          >
            <Plus size={20} />
            Post a Job
          </button>
        </div>

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

        {jobs.length === 0 && !showJobForm && (
          <div className="bg-white rounded-2xl shadow p-8 text-center text-gray-500">
            No jobs posted yet. Click "Post a Job" to add the first one.
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
                          Delete
                        </button>
                        <span className="bg-blue-100 text-blue-800 px-4 py-2 rounded-lg font-semibold">
                          {matches.length} Candidate{matches.length === 1 ? '' : 's'}
                        </span>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
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
                        <p className="text-gray-600 text-sm font-semibold">Min CGPA</p>
                        <p className="text-xl font-bold text-gray-900 mt-2">{selectedJob.minCGPA}</p>
                      </div>
                      <div>
                        <p className="text-gray-600 text-sm font-semibold">Job Type</p>
                        <p className="text-sm font-semibold text-gray-900 mt-2">{selectedJob.jobType}</p>
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
                        No candidates evaluated for this job yet.
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
              <p className="text-xs text-gray-600 mb-2">Missing: ({candidate.skillMatch.missing.length})</p>
              <div className="flex flex-wrap gap-2">
                {candidate.skillMatch.missing.map((skill) => (
                  <span key={skill} className="bg-amber-100 text-amber-800 text-xs px-3 py-1 rounded-full font-medium">
                    ⚠ {skill}
                  </span>
                ))}
              </div>
            </div>
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
    location: 'India',
    requiredSkills: '',
    minCGPA: 0,
    experience: 'Fresher',
    jobType: 'Remote',
    employmentType: 'Full-Time',
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
      const result = await cpipApi.postJob({
        job_title: jobData.title.trim(),
        company_name: jobData.company.trim() || 'Unknown',
        location: jobData.location.trim() || 'India',
        required_skills: jobData.requiredSkills
          .split(',')
          .map((s) => s.trim())
          .filter(Boolean),
        min_cgpa: jobData.minCGPA,
        experience_level: jobData.experience,
        job_type: jobData.jobType,
        employment_type: jobData.employmentType,
      });

      if (result.detail) {
        throw new Error(result.detail);
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
          <label className="block text-sm font-semibold text-gray-900 mb-2">Company Name</label>
          <input
            type="text"
            value={jobData.company}
            onChange={(e) => setJobData({ ...jobData, company: e.target.value })}
            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
            placeholder="e.g. TechCorp"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-900 mb-2">Location</label>
          <input
            type="text"
            value={jobData.location}
            onChange={(e) => setJobData({ ...jobData, location: e.target.value })}
            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
            placeholder="e.g. Bangalore, Mumbai, Remote"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-900 mb-2">Required Skills (comma-separated)</label>
          <input
            type="text"
            value={jobData.requiredSkills}
            onChange={(e) => setJobData({ ...jobData, requiredSkills: e.target.value })}
            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
            placeholder="Python, FastAPI, SQL"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-gray-900 mb-2">Minimum CGPA</label>
          <input
            type="number"
            value={jobData.minCGPA}
            onChange={(e) => setJobData({ ...jobData, minCGPA: parseFloat(e.target.value) || 0 })}
            step="0.1"
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
          <label className="block text-sm font-semibold text-gray-900 mb-2">Work Location Type *</label>
          <select
            value={jobData.jobType}
            onChange={(e) => setJobData({ ...jobData, jobType: e.target.value })}
            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
          >
            <option value="Remote">Remote</option>
            <option value="Hybrid">Hybrid</option>
            <option value="Work From Home">Work From Home</option>
            <option value="Office">Office</option>
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
    minCGPA: job.minCGPA,
    experience: job.experience,
    jobType: job.jobType,
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
        job_title: jobData.title.trim(),
        location: jobData.location.trim(),
        required_skills: jobData.requiredSkills
          .split(',')
          .map((s) => s.trim())
          .filter(Boolean),
        min_cgpa: jobData.minCGPA,
        experience_level: jobData.experience,
        job_type: jobData.jobType,
        employment_type: jobData.employmentType,
      });

      if (result.detail) {
        throw new Error(result.detail);
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

          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">Minimum CGPA</label>
            <input
              type="number"
              value={jobData.minCGPA}
              onChange={(e) => setJobData({ ...jobData, minCGPA: parseFloat(e.target.value) || 0 })}
              step="0.1"
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
            <label className="block text-sm font-semibold text-gray-900 mb-2">Work Location Type</label>
            <select
              value={jobData.jobType}
              onChange={(e) => setJobData({ ...jobData, jobType: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:border-blue-500"
            >
              <option value="Remote">Remote</option>
              <option value="Hybrid">Hybrid</option>
              <option value="Work From Home">Work From Home</option>
              <option value="Office">Office</option>
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