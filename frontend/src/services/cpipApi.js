// API Base URL - SINGLE DECLARATION ONLY
const API_BASE = 'http://127.0.0.1:8000/api';

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

  getMatchedCandidates: (jobId) =>
    fetch(`${API_BASE}/jobs/${jobId}/matches`).then(r => r.json()),

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

  // External Jobs search
  searchExternalJobs: (query, studentId) => {
    const params = new URLSearchParams({ query });
    if (studentId) params.append('student_id', studentId);
    return fetch(`${API_BASE}/jobs/external/search?${params}`).then(r => r.json());
  },

  // Recruiter endpoints
  updateJob: (jobId, jobData) =>
    fetch(`${API_BASE}/recruiter/jobs/${jobId}`, {
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