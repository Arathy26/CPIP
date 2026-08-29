import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

import LandingPage from './pages/LandingPage';
import CandidateDashboard from './pages/CandidateDashboard';
import RecruiterDashboard from './pages/RecruiterDashboard';
import StudentsListPage from './pages/StudentsListPage';
import RoleSelector from './components/upload/RoleSelector';
import ResumeUploader from './components/upload/ResumeUploader';

import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/students" element={<StudentsListPage />} />
        <Route path="/role-select" element={<RoleSelector />} />
        <Route path="/resume-upload" element={<ResumeUploader />} />
        <Route path="/dashboard/candidate/:studentId" element={<CandidateDashboard />} />
        <Route path="/dashboard/recruiter" element={<RecruiterDashboard />} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
}

export default App;