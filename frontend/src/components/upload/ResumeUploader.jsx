import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import cpipApi from '../../services/cpipApi';

export default function ResumeUploader() {
  const navigate = useNavigate();
  const [resumeFile, setResumeFile] = useState(null);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [location, setLocation] = useState('');
  const [status, setStatus] = useState('idle');
  const [errorMessage, setErrorMessage] = useState('');

  const targetRole = localStorage.getItem('targetRole') || '';

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) setResumeFile(file);
  };

  const handleUpload = async () => {
    if (!resumeFile) return;
    if (!name.trim()) { setErrorMessage('Please enter your name.'); return; }
    if (!email.trim()) { setErrorMessage('Please enter your email.'); return; }
    if (!location.trim()) { setErrorMessage('Please enter your preferred job location.'); return; }

    setStatus('uploading');
    setErrorMessage('');

    try {
      const formData = new FormData();
      formData.append('file', resumeFile);
      formData.append('name', name.trim());
      formData.append('email', email.trim());
      formData.append('target_role', targetRole);
      formData.append('location', location.trim());

      const result = await cpipApi.uploadResume(formData);

      if (result.detail) throw new Error(result.detail);
      if (!result.student_id) throw new Error('No student ID returned');

      setStatus('success');
      navigate(`/dashboard/candidate/${result.student_id}`);
    } catch (err) {
      console.error('Resume upload failed:', err);
      setStatus('error');
      setErrorMessage(err.message || 'Upload failed. Try again.');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 p-8">
      <div className="max-w-2xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Upload Your Resume</h1>
          <p className="text-lg text-gray-600">
            We'll scan your resume and check readiness for{' '}
            <strong>{targetRole || 'your target role'}</strong>.
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-8 space-y-5">

          {/* Name */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">
              Full Name <span className="text-red-500">*</span>
            </label>
            <input type="text" value={name} onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Arathy Rajeev"
              className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:outline-none text-sm" />
          </div>

          {/* Email */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">
              Email <span className="text-red-500">*</span>
            </label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
              placeholder="e.g. arathy@example.com"
              className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:outline-none text-sm" />
          </div>

          {/* Location */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-1">
              Preferred Job Location <span className="text-red-500">*</span>
            </label>
            <input type="text" value={location} onChange={(e) => setLocation(e.target.value)}
              placeholder="e.g. bangalore, kochi, mumbai..."
              className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:outline-none text-sm" />
            <p className="text-xs text-gray-400 mt-1">Used to find jobs in your city</p>
          </div>

          {/* File upload */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Resume (PDF) <span className="text-red-500">*</span>
            </label>
            <div className="border-2 border-dashed border-purple-300 rounded-xl p-6 text-center">
              <input type="file" accept=".pdf" onChange={handleFileSelect}
                className="hidden" id="resume-input" />
              <label htmlFor="resume-input"
                className="bg-purple-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-purple-700 cursor-pointer inline-block">
                Choose File
              </label>
              {resumeFile && (
                <p className="text-green-700 text-sm mt-3 font-medium">
                  ✓ {resumeFile.name}
                </p>
              )}
            </div>
          </div>

          {/* Status messages */}
          {status === 'uploading' && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-blue-800 font-medium">
                Uploading and scanning your resume…
              </p>
            </div>
          )}

          {status === 'error' && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-800 font-medium">{errorMessage}</p>
            </div>
          )}

          {/* Submit */}
          <button onClick={handleUpload}
            disabled={!resumeFile || !name.trim() || !email.trim() || !location.trim() || status === 'uploading'}
            className={`w-full py-3 rounded-lg font-semibold transition-all ${
              resumeFile && name.trim() && email.trim() && location.trim() && status !== 'uploading'
                ? 'bg-purple-600 text-white hover:bg-purple-700'
                : 'bg-gray-200 text-gray-500 cursor-not-allowed'
            }`}>
            {status === 'uploading' ? 'Uploading…' : 'Upload & Analyze Resume'}
          </button>
        </div>
      </div>
    </div>
  );
}