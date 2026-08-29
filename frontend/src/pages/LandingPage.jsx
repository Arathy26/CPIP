import { useNavigate } from 'react-router-dom';
import { User, Briefcase, Users } from 'lucide-react';

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-8 py-6 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-purple-700">CPIP</h1>
          <p className="text-gray-500 text-sm mt-1">Career & Placement Intelligence Platform</p>
        </div>
      </div>

      {/* Hero */}
      <div className="max-w-7xl mx-auto px-8 py-10 flex flex-col justify-center min-h-[calc(100vh-110px)]">
        <div className="text-center mb-10">
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Intelligent readiness assessment and job matching for students and recruiters
          </p>
        </div>

        {/* Three-Sided CTA */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* UPLOAD RESUME (new student) */}
          <div
            onClick={() => navigate('/role-select')}
            className="group bg-white border border-purple-200 rounded-2xl p-10 shadow-sm hover:shadow-md hover:border-purple-400 transition-all cursor-pointer"
          >
            <User className="w-14 h-14 mb-5 text-purple-600 group-hover:scale-110 transition-transform" strokeWidth={1.5} />
            <h3 className="text-2xl font-bold text-gray-900 mb-3">Upload Resume</h3>
            <p className="text-gray-600 mb-6 leading-relaxed">
              New student? Upload your resume, select a target role, and get your readiness assessment
            </p>
            <div className="flex items-center gap-2 text-purple-600 group-hover:text-purple-700 font-semibold">
              <span>Start Assessment</span>
              <span className="group-hover:translate-x-2 transition-transform">→</span>
            </div>
          </div>

          {/* STUDENTS LIST (existing students) */}
          <div
            onClick={() => navigate('/students')}
            className="group bg-white border border-emerald-200 rounded-2xl p-10 shadow-sm hover:shadow-md hover:border-emerald-400 transition-all cursor-pointer"
          >
            <Users className="w-14 h-14 mb-5 text-emerald-600 group-hover:scale-110 transition-transform" strokeWidth={1.5} />
            <h3 className="text-2xl font-bold text-gray-900 mb-3">Students</h3>
            <p className="text-gray-600 mb-6 leading-relaxed">
              View students who already uploaded resumes — search by name and instantly see their analysis and job matches
            </p>
            <div className="flex items-center gap-2 text-emerald-600 group-hover:text-emerald-700 font-semibold">
              <span>View Students</span>
              <span className="group-hover:translate-x-2 transition-transform">→</span>
            </div>
          </div>

          {/* RECRUITER */}
          <div
            onClick={() => navigate('/dashboard/recruiter')}
            className="group bg-white border border-blue-200 rounded-2xl p-10 shadow-sm hover:shadow-md hover:border-blue-400 transition-all cursor-pointer"
          >
            <Briefcase className="w-14 h-14 mb-5 text-blue-600 group-hover:scale-110 transition-transform" strokeWidth={1.5} />
            <h3 className="text-2xl font-bold text-gray-900 mb-3">Recruiter</h3>
            <p className="text-gray-600 mb-6 leading-relaxed">
              Post job opportunities, see AI-matched candidates with fit scores, skill coverage, and shortlists
            </p>
            <div className="flex items-center gap-2 text-blue-600 group-hover:text-blue-700 font-semibold">
              <span>Post a Job</span>
              <span className="group-hover:translate-x-2 transition-transform">→</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}