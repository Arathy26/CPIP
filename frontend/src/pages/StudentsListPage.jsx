import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, FileText, MapPin, Target, ChevronRight, Upload, History, X, Check } from 'lucide-react';
import cpipApi from '../services/cpipApi';

export default function StudentsListPage() {
  const navigate = useNavigate();
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [searchQuery, setSearchQuery] = useState('');
  const [locationFilter, setLocationFilter] = useState('');
  const [roleInputs, setRoleInputs] = useState({});
  const [savingRole, setSavingRole] = useState({});
  const [roleHistory, setRoleHistory] = useState({});
  const [showHistory, setShowHistory] = useState({});
  const [uploadingResume, setUploadingResume] = useState({});
  const [uploadSuccess, setUploadSuccess] = useState({});

  useEffect(() => { fetchStudents(); }, []);

  const fetchStudents = async () => {
    try {
      setLoading(true);
      const data = await cpipApi.getStudentsWithResumes();
      setStudents(data.students || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const filtered = students.filter((s) => {
    const q = searchQuery.toLowerCase();
    const matchesSearch = !q ||
      (s.name || '').toLowerCase().includes(q) ||
      (s.email || '').toLowerCase().includes(q) ||
      (s.target_role || '').toLowerCase().includes(q);
    const matchesLocation = !locationFilter.trim() ||
      (s.location || '').toLowerCase().includes(locationFilter.toLowerCase());
    return matchesSearch && matchesLocation;
  });

  const handleSaveRole = async (studentId, currentRole) => {
    const newRole = (roleInputs[studentId] || '').trim();
    if (!newRole || newRole === currentRole) return;
    setSavingRole(prev => ({ ...prev, [studentId]: true }));
    try {
      await cpipApi.updateTargetRole(studentId, newRole);
      setStudents(prev => prev.map(s => s.id === studentId ? { ...s, target_role: newRole } : s));
      setRoleInputs(prev => ({ ...prev, [studentId]: '' }));
    } catch (err) {
      alert('Failed to update role: ' + err.message);
    } finally {
      setSavingRole(prev => ({ ...prev, [studentId]: false }));
    }
  };

  const handleShowHistory = async (studentId) => {
    if (showHistory[studentId]) {
      setShowHistory(prev => ({ ...prev, [studentId]: false }));
      return;
    }
    try {
      const data = await cpipApi.getRoleHistory(studentId);
      setRoleHistory(prev => ({ ...prev, [studentId]: data.history || [] }));
      setShowHistory(prev => ({ ...prev, [studentId]: true }));
    } catch (err) {
      alert('Could not load history');
    }
  };

  const handleResumeUpload = async (studentId, file) => {
    if (!file) return;
    setUploadingResume(prev => ({ ...prev, [studentId]: true }));
    try {
      await cpipApi.uploadResumeForStudent(studentId, file);
      setUploadSuccess(prev => ({ ...prev, [studentId]: true }));
      await fetchStudents();
      setTimeout(() => setUploadSuccess(prev => ({ ...prev, [studentId]: false })), 3000);
    } catch (err) {
      alert('Upload failed: ' + err.message);
    } finally {
      setUploadingResume(prev => ({ ...prev, [studentId]: false }));
    }
  };

  const getStatusColor = (status) => {
    if (status === 'completed') return 'bg-green-50 text-green-700 border-green-200';
    if (status === 'pending') return 'bg-yellow-50 text-yellow-700 border-yellow-200';
    return 'bg-gray-50 text-gray-600 border-gray-200';
  };

  const formatDate = (iso) => {
    if (!iso) return '';
    return new Date(iso).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
      <div className="bg-white border-b border-gray-200 px-8 py-6 sticky top-0 z-10">
        <div className="max-w-5xl mx-auto flex items-center gap-4">
          <button onClick={() => navigate('/')} className="p-2 rounded-lg hover:bg-gray-100 transition">
            <ArrowLeft className="w-5 h-5 text-gray-600" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-purple-700">Students</h1>
            <p className="text-gray-500 text-sm mt-0.5">{students.length} student{students.length !== 1 ? 's' : ''} with uploaded resumes</p>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-8 py-8">
        <div className="flex flex-wrap gap-3 mb-6">
          <input type="text" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by name, email, or role..."
            className="flex-1 min-w-60 px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:outline-none bg-white text-sm" />
          <input type="text" value={locationFilter} onChange={(e) => setLocationFilter(e.target.value)}
            placeholder="Filter by location..."
            className="flex-1 min-w-48 px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-blue-400 focus:outline-none bg-white text-sm" />
          {(searchQuery || locationFilter) && (
            <button onClick={() => { setSearchQuery(''); setLocationFilter(''); }}
              className="px-4 py-3 rounded-xl border border-red-200 text-red-600 text-sm hover:bg-red-50">
              Reset
            </button>
          )}
        </div>

        {loading && (
          <div className="text-center py-20">
            <div className="inline-block w-8 h-8 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin" />
            <p className="text-gray-500 mt-4">Loading students...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
            <p className="text-red-700 font-medium">{error}</p>
            <button onClick={fetchStudents} className="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg text-sm">Retry</button>
          </div>
        )}

        {!loading && !error && students.length === 0 && (
          <div className="text-center py-20">
            <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg font-medium">No students yet</p>
            <p className="text-gray-400 text-sm mt-1 mb-6">Students appear here after uploading a resume</p>
            <button onClick={() => navigate('/role-select')} className="px-6 py-3 bg-purple-600 text-white rounded-xl font-semibold hover:bg-purple-700">
              Upload First Resume
            </button>
          </div>
        )}

        {!loading && !error && students.length > 0 && filtered.length === 0 && (
          <p className="text-gray-500 text-center py-12">No students match your filters.</p>
        )}

        <div className="space-y-4">
          {filtered.map((student) => (
            <div key={student.id} className="bg-white border border-gray-100 rounded-xl shadow-sm overflow-hidden">
              {/* Click to go to dashboard */}
              <div onClick={() => navigate(`/dashboard/candidate/${student.id}`)}
                className="group p-5 hover:bg-purple-50 transition cursor-pointer">
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900">{student.name}</h3>
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full border ${getStatusColor(student.resume_status)}`}>
                        {student.resume_status === 'completed' ? 'Resume Ready' : student.resume_status}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 mb-3">{student.email}</p>
                    <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                      {student.target_role && (
                        <span className="flex items-center gap-1">
                          <Target className="w-3.5 h-3.5 text-purple-500" />{student.target_role}
                        </span>
                      )}
                      {student.location && student.location !== 'Not specified' && (
                        <span className="flex items-center gap-1">
                          <MapPin className="w-3.5 h-3.5 text-blue-500" />{student.location}
                        </span>
                      )}
                      {student.resume_file && (
                        <span className="flex items-center gap-1">
                          <FileText className="w-3.5 h-3.5 text-gray-400" />{student.resume_file}
                        </span>
                      )}
                    </div>
                    {student.skills && student.skills.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 mt-3">
                        {student.skills.slice(0, 6).map((skill, i) => (
                          <span key={i} className="text-xs px-2 py-0.5 rounded-full bg-purple-50 text-purple-700 border border-purple-100">{skill}</span>
                        ))}
                        {student.skills.length > 6 && (
                          <span className="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-500">+{student.skills.length - 6} more</span>
                        )}
                      </div>
                    )}
                  </div>
                  <ChevronRight className="w-5 h-5 text-gray-300 group-hover:text-purple-500 transition shrink-0 ml-4" />
                </div>
              </div>

              {/* Actions bar */}
              <div className="border-t border-gray-100 px-5 py-3 bg-gray-50 flex flex-wrap gap-3 items-center">
                {/* Change role */}
                <div className="flex items-center gap-2 flex-1 min-w-48" onClick={(e) => e.stopPropagation()}>
                  <Target className="w-4 h-4 text-purple-400 shrink-0" />
                  <input type="text"
                    value={roleInputs[student.id] || ''}
                    onChange={(e) => setRoleInputs(prev => ({ ...prev, [student.id]: e.target.value }))}
                    onKeyDown={(e) => e.key === 'Enter' && handleSaveRole(student.id, student.target_role)}
                    placeholder={student.target_role || 'Change target role...'}
                    className="flex-1 text-sm px-3 py-1.5 rounded-lg border border-gray-200 focus:border-purple-400 focus:outline-none" />
                  <button
                    onClick={() => handleSaveRole(student.id, student.target_role)}
                    disabled={!roleInputs[student.id] || savingRole[student.id]}
                    className={`p-1.5 rounded-lg transition ${roleInputs[student.id] ? 'bg-purple-600 text-white hover:bg-purple-700' : 'bg-gray-200 text-gray-400 cursor-not-allowed'}`}>
                    <Check className="w-4 h-4" />
                  </button>
                </div>

                {/* Upload resume */}
                <label onClick={(e) => e.stopPropagation()}
                  className="flex items-center gap-1.5 text-sm px-3 py-1.5 rounded-lg border border-blue-200 text-blue-600 hover:bg-blue-50 cursor-pointer transition">
                  {uploadingResume[student.id] ? <span className="text-xs">Uploading...</span>
                    : uploadSuccess[student.id] ? <span className="text-xs text-green-600">Uploaded!</span>
                    :<><Upload className="w-3.5 h-3.5" /><span>Upload Updated Resume</span></>}
                  <input type="file" accept=".pdf" className="hidden"
                    onChange={(e) => { e.stopPropagation(); handleResumeUpload(student.id, e.target.files[0]); }} />
                </label>

                {/* History */}
                <button onClick={(e) => { e.stopPropagation(); handleShowHistory(student.id); }}
                  className="flex items-center gap-1.5 text-sm px-3 py-1.5 rounded-lg border border-gray-200 text-gray-600 hover:bg-gray-100 transition">
                  <History className="w-3.5 h-3.5" /><span>History</span>
                </button>
              </div>

              {/* Role history panel */}
              {showHistory[student.id] && (
                <div className="border-t border-gray-100 px-5 py-4 bg-white">
                  <div className="flex items-center justify-between mb-3">
                    <p className="text-sm font-semibold text-gray-700">Role Change History</p>
                    <button onClick={() => setShowHistory(prev => ({ ...prev, [student.id]: false }))}>
                      <X className="w-4 h-4 text-gray-400" />
                    </button>
                  </div>
                  {!roleHistory[student.id] || roleHistory[student.id].length === 0 ? (
                    <p className="text-sm text-gray-400">No role changes recorded yet.</p>
                  ) : (
                    <div className="space-y-2">
                      {roleHistory[student.id].map((h) => (
                        <div key={h.id} className="flex items-center gap-2 text-sm text-gray-600">
                          <span className="text-gray-400 text-xs w-24 shrink-0">{formatDate(h.changed_at)}</span>
                          <span className="text-gray-400">{h.previous_role || '—'}</span>
                          <span className="text-gray-400">→</span>
                          <span className="font-medium text-purple-700">{h.new_role}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}