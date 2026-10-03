import { API_BASE } from '../services/cpipApi';
import React, { useState, useEffect } from 'react';
import { Upload, Search, CheckCircle, Clock, AlertCircle, Trash2 } from 'lucide-react';

/**
 * ResumeSelector Component
 * 
 * Features:
 * - Upload resume (non-blocking)
 * - Browse resume library
 * - Search by filename
 * - Quick select
 * - Show extraction status
 */

const ResumeSelector = ({ studentId }) => {
  
  // State
  const [activeTab, setActiveTab] = useState('library'); // 'library' or 'upload'
  const [resumes, setResumes] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedResume, setSelectedResume] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [message, setMessage] = useState('');
  const [statusPolling, setStatusPolling] = useState(null);

  // Load resume library
  const loadResumes = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/resume/list/${studentId}`);
      const data = await response.json();
      setResumes(data.resumes || []);
      
      // Find selected resume
      const selected = data.resumes?.find(r => r.is_selected);
      setSelectedResume(selected);
    } catch (error) {
      console.error('Error loading resumes:', error);
      setMessage('Error loading resumes');
    } finally {
      setLoading(false);
    }
  };

  // Search resumes
  const handleSearch = async (query) => {
    setSearchQuery(query);
    
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }
    
    try {
      const response = await fetch(`${API_BASE}/resume/search/${studentId}?q=${query}`);
      const data = await response.json();
      setSearchResults(data.resumes || []);
    } catch (error) {
      console.error('Error searching:', error);
    }
  };

  // Upload resume
  const handleUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.pdf')) {
      setMessage('❌ Only PDF files allowed');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setLoading(true);
    setMessage('Uploading...');

    try {
      const response = await fetch(`${API_BASE}/resume/upload/${studentId}`, {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (data.success) {
        setMessage(`✅ ${data.message}`);
        
        // Add to resume list
        const newResume = {
          id: data.resume_id,
          file_name: data.file_name,
          extraction_status: 'pending',
          skills: null,
          uploaded_at: data.timestamp
        };
        
        setResumes([newResume, ...resumes]);
        
        // Start polling extraction status
        startStatusPolling(data.resume_id);
        
        // Clear file input
        event.target.value = '';
      } else {
        setMessage(`❌ ${data.detail}`);
      }
    } catch (error) {
      console.error('Error uploading:', error);
      setMessage('❌ Upload failed');
    } finally {
      setLoading(false);
    }
  };

  // Poll extraction status
  const startStatusPolling = (resumeId) => {
    let pollCount = 0;
    const maxPolls = 30; // 30 seconds

    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE}/resume/${resumeId}/status`);
        const data = await response.json();

        // Update resume status
        setResumes(prev => 
          prev.map(r => 
            r.id === resumeId ? { ...r, extraction_status: data.status, skills: data.skills_count > 0 ? [...Array(data.skills_count)] : null } : r
          )
        );

        if (data.status === 'completed') {
          setMessage(`✅ Resume extraction completed! ${data.skills_count} skills found.`);
          clearInterval(pollInterval);
        } else if (data.status === 'failed') {
          setMessage(`❌ Extraction failed: ${data.error}`);
          clearInterval(pollInterval);
        }

        pollCount++;
        if (pollCount >= maxPolls) {
          clearInterval(pollInterval);
        }
      } catch (error) {
        console.error('Poll error:', error);
      }
    }, 1000);

    setStatusPolling(pollInterval);
  };

  // Select resume
  const handleSelectResume = async (resumeId) => {
    if (loading) return;

    setLoading(true);

    try {
      const response = await fetch(
        `${API_BASE}/resume/select/${studentId}/${resumeId}`,
        { method: 'POST' }
      );

      const data = await response.json();

      if (data.success) {
        setMessage(`✅ Resume selected! Found ${data.skills?.length || 0} skills.`);
        loadResumes();
        setActiveTab('library');
      } else {
        setMessage(`❌ ${data.detail}`);
      }
    } catch (error) {
      console.error('Error selecting:', error);
      setMessage('Error selecting resume');
    } finally {
      setLoading(false);
    }
  };

  // Load on mount
  useEffect(() => {
    loadResumes();
  }, [studentId]);

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (statusPolling) clearInterval(statusPolling);
    };
  }, [statusPolling]);

  // Render status badge
  const StatusBadge = ({ status }) => {
    if (status === 'completed') {
      return (
        <div className="flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 rounded text-xs">
          <CheckCircle size={14} />
          Extracted
        </div>
      );
    } else if (status === 'pending') {
      return (
        <div className="flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
          <Clock size={14} />
          Processing...
        </div>
      );
    } else {
      return (
        <div className="flex items-center gap-1 px-2 py-1 bg-red-100 text-red-700 rounded text-xs">
          <AlertCircle size={14} />
          Failed
        </div>
      );
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6">Resume Management</h2>

      {/* Message */}
      {message && (
        <div className="mb-4 p-3 bg-gray-50 border border-gray-200 rounded text-sm">
          {message}
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-4 mb-6 border-b">
        <button
          onClick={() => setActiveTab('library')}
          className={`pb-3 px-4 font-medium ${
            activeTab === 'library'
              ? 'border-b-2 border-blue-500 text-blue-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          Resume Library ({resumes.length})
        </button>
        <button
          onClick={() => setActiveTab('upload')}
          className={`pb-3 px-4 font-medium ${
            activeTab === 'upload'
              ? 'border-b-2 border-blue-500 text-blue-600'
              : 'text-gray-600 hover:text-gray-800'
          }`}
        >
          Upload New
        </button>
      </div>

      {/* LIBRARY TAB */}
      {activeTab === 'library' && (
        <div>
          {/* Current Resume */}
          {selectedResume && (
            <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h3 className="font-semibold text-blue-900 mb-2">📄 Current Resume</h3>
              <p className="text-sm text-blue-800">{selectedResume.file_name}</p>
              {selectedResume.skills && (
                <p className="text-xs text-blue-700 mt-1">
                  {selectedResume.skills.length} skills extracted
                </p>
              )}
            </div>
          )}

          {/* Search */}
          <div className="mb-6 relative">
            <input
              type="text"
              placeholder="Search by filename..."
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg pl-10"
            />
            <Search size={18} className="absolute left-3 top-2.5 text-gray-400" />
          </div>

          {/* Resume List */}
          <div className="space-y-3">
            {(searchQuery ? searchResults : resumes).map((resume) => (
              <div
                key={resume.id}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition"
              >
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900">{resume.file_name}</h4>
                  <div className="flex items-center gap-2 mt-2">
                    <StatusBadge status={resume.extraction_status} />
                    {resume.skills && (
                      <span className="text-xs text-gray-500">
                        {resume.skills.length} skills
                      </span>
                    )}
                    <span className="text-xs text-gray-400">
                      {new Date(resume.uploaded_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                <div className="flex gap-2">
                  {resume.extraction_status === 'completed' && !resume.is_selected && (
                    <button
                      onClick={() => handleSelectResume(resume.id)}
                      disabled={loading}
                      className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400 text-sm font-medium"
                    >
                      Select
                    </button>
                  )}
                  {resume.is_selected && (
                    <span className="px-4 py-2 bg-green-100 text-green-700 rounded text-sm font-medium">
                      ✓ Selected
                    </span>
                  )}
                </div>
              </div>
            ))}

            {(searchQuery ? searchResults : resumes).length === 0 && (
              <p className="text-center text-gray-500 py-8">
                {searchQuery ? 'No resumes match your search' : 'No resumes uploaded yet'}
              </p>
            )}
          </div>
        </div>
      )}

      {/* UPLOAD TAB */}
      {activeTab === 'upload' && (
        <div>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
            <Upload size={32} className="mx-auto mb-3 text-gray-400" />
            
            <label className="cursor-pointer">
              <input
                type="file"
                accept=".pdf"
                onChange={handleUpload}
                disabled={loading}
                className="hidden"
              />
              <div>
                <p className="font-medium text-gray-900 mb-1">
                  {loading ? 'Uploading...' : 'Click to upload or drag and drop'}
                </p>
                <p className="text-sm text-gray-500">PDF files only</p>
              </div>
            </label>
          </div>

          {uploadProgress > 0 && (
            <div className="mt-4">
              <div className="bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-500 h-2 rounded-full transition"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ResumeSelector;