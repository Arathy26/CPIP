// API base URL — ONE place. Set VITE_API_URL in frontend/.env for deployment
// (e.g. VITE_API_URL=https://cpip-i6il.onrender.com). Local default below.
export const API_ROOT = (
  import.meta.env.VITE_API_URL ||
  import.meta.env.VITE_BACKEND_URL ||
  'http://127.0.0.1:8000'
).replace(/\/+$/, '');
export const API_BASE = `${API_ROOT}/api`;

const sendJson = (url, method, body) =>
  fetch(url, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  }).then(async (r) => {
    const data = await r.json();
    if (!r.ok) throw new Error(data.detail || `Request failed (${r.status})`);
    return data;
  });

const cpipApi = {
  // Candidate endpoints
  getCandidateProfile: (studentId) =>
    fetch(`${API_BASE}/candidates/${studentId}`).then(r => r.json()),

  getAllCandidates: () =>
    fetch(`${API_BASE}/candidates`).then(r => r.json()),

  getRoles: () =>
    fetch(`${API_BASE}/roles`).then(r => r.json()),

  // Skill Gap — supports optional role override
  getSkillGap: (studentId, role = null) => {
    const params = role ? `?role=${encodeURIComponent(role)}` : '';
    return fetch(`${API_BASE}/skill-gap/${studentId}${params}`).then(r => r.json());
  },

  // Portfolio
  getPortfolioReadiness: (studentId) =>
    fetch(`${API_BASE}/portfolio-readiness/${studentId}`).then(r => r.json()),

  // Resume
  getResumeReadiness: (studentId) =>
    fetch(`${API_BASE}/resume-readiness/${studentId}`).then(r => r.json()),

  // Role Matching
  getRoleMatch: (studentId) =>
    fetch(`${API_BASE}/role-match/${studentId}`).then(r => r.json()),

  // Interview
  getInterviewReadiness: (studentId) =>
    fetch(`${API_BASE}/interview-readiness/${studentId}`).then(r => r.json()),

  // Training
  getTrainingPlan: (studentId) =>
    fetch(`${API_BASE}/training-plan/${studentId}`).then(r => r.json()),

  // Jobs — now supports preferred location
  getJobMatch: (studentId, location = null) => {
    const params = location ? `?location=${encodeURIComponent(location)}` : '';
    return fetch(`${API_BASE}/job-match/${studentId}${params}`).then(r => r.json());
  },

  postJob: (jobData) =>
    fetch(`${API_BASE}/jobs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(jobData)
    }).then(r => r.json()),

  getAllJobs: (query) => {
    const params = query ? `?query=${encodeURIComponent(query)}` : '';
    return fetch(`${API_BASE}/jobs${params}`).then(r => r.json());
  },

  // Recruiter side: candidates matched to one posting
  getMatchedCandidates: (jobId) =>
    fetch(`${API_BASE}/jobs/${jobId}/candidates`).then(r => r.json()),

  // Recruiter bulk upload (CSV). Valid rows are saved, invalid rows returned in `errors`.
  bulkUploadJobs: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return fetch(`${API_BASE}/jobs/bulk`, { method: 'POST', body: formData }).then(r => r.json());
  },

  // Close a posting (kept for audit; hidden from candidates)
  deleteJob: (jobId) =>
    fetch(`${API_BASE}/jobs/${jobId}`, { method: 'DELETE' }).then(r => r.json()),

  // Resume Upload (new student flow)
  uploadResume: (formData) =>
    fetch(`${API_BASE}/resume/upload`, {
      method: 'POST',
      body: formData,
    }).then(r => r.json()),

  // Notifications
  getNotifications: (studentId) =>
    fetch(`${API_BASE}/notifications/${studentId}`).then(r => r.json()),

  markNotificationRead: (notificationId) =>
    fetch(`${API_BASE}/notifications/${notificationId}/read`, {
      method: 'POST',
    }).then(r => r.json()),

  // Recruiter endpoints
  updateJob: (jobId, jobData) =>
    fetch(`${API_BASE}/jobs/${jobId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(jobData)
    }).then(r => r.json()),

  getMarketSkillGap: (studentId) =>
    fetch(`${API_BASE}/skill-gap/market/${studentId}`).then(r => r.json()),

  // Readiness Scores
  getReadinessScores: (studentId) =>
    fetch(`${API_BASE}/readiness-scores/${studentId}`).then(r => r.json()),

  // ── Students list ──────────────────────────────────────────────
  getStudentsWithResumes: () =>
    fetch(`${API_BASE}/students/with-resumes`).then(r => r.json()),

  // ── Update target role (saves history in DB) ───────────────────
  updateTargetRole: (studentId, newRole) =>
    fetch(`${API_BASE}/students/${studentId}/target-role`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target_role: newRole }),
    }).then(r => r.json()),

  // ── Get role change history ────────────────────────────────────
  getRoleHistory: (studentId) =>
    fetch(`${API_BASE}/students/${studentId}/role-history`).then(r => r.json()),

  // ── Upload resume for existing student ────────────────────────
  // ── Student evidence (student edits) ───────────────────────────
  updateSkills: (studentId, skills) =>
    sendJson(`${API_BASE}/students/${studentId}/skills`, 'PUT', { skills }),

  updatePortfolioLinks: (studentId, links) =>
    sendJson(`${API_BASE}/students/${studentId}/portfolio-links`, 'PUT', links),

  updateLocation: (studentId, location) =>
    sendJson(`${API_BASE}/students/${studentId}/location`, 'PUT', { location }),

  // ── Mock interview (recorded by a mentor) ──────────────────────
  recordInterviewAssessment: (assessment) =>
    sendJson(`${API_BASE}/interview-assessments`, 'POST', assessment),

  uploadResumeForStudent: (studentId, file) => {
    const formData = new FormData();
    formData.append('file', file);
    return fetch(`${API_BASE}/resume/upload/${studentId}`, {
      method: 'POST',
      body: formData,
    }).then(r => r.json());
  },
};

export default cpipApi;