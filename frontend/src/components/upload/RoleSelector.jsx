import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function RoleSelector() {
  const navigate = useNavigate();
  const [targetRole, setTargetRole] = useState('');

  const handleNext = () => {
    const trimmed = targetRole.trim();
    if (trimmed) {
      localStorage.setItem('targetRole', trimmed);
      navigate('/resume-upload');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 p-8">
      <div className="max-w-2xl mx-auto">
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            What's Your Target Role?
          </h1>
          <p className="text-lg text-gray-600">
            Type the job role you're aiming for. This helps us assess your readiness.
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-lg p-8">
          <label htmlFor="target-role-input" className="block text-sm font-semibold text-gray-700 mb-2">
            Target role
          </label>
          <input
            id="target-role-input"
            type="text"
            value={targetRole}
            onChange={(e) => setTargetRole(e.target.value)}
            placeholder="e.g. Backend Developer, AI Engineer, Full Stack Developer"
            className="w-full px-6 py-4 rounded-lg border-2 border-gray-200 focus:border-purple-500 focus:outline-none text-gray-900 mb-6"
            autoFocus
          />

          <button
            onClick={handleNext}
            disabled={!targetRole.trim()}
            className={`w-full py-3 rounded-lg font-semibold transition-all ${
              targetRole.trim()
                ? 'bg-purple-600 text-white hover:bg-purple-700'
                : 'bg-gray-200 text-gray-500 cursor-not-allowed'
            }`}
          >
            Next: Upload Resume →
          </button>
        </div>
      </div>
    </div>
  );
}