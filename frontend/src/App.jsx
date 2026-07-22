import { useState, useEffect } from 'react';
import './index.css';

export default function App() {
  const [backendStatus, setBackendStatus] = useState('checking...');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/health')
      .then(res => res.json())
      .then(data => {
        setBackendStatus('✅ ' + data.message);
        setLoading(false);
      })
      .catch(err => {
        setBackendStatus('❌ Backend not running');
        setLoading(false);
      });
  }, []);

  return (
    <div className="app">
      <header className="header">
        <h1>CPIP</h1>
        <p>Career & Placement Intelligence Platform</p>
      </header>

      <main className="main">
        <section className="status-card">
          <h2>Backend Status</h2>
          <p className={loading ? 'checking' : 'ready'}>
            {backendStatus}
          </p>
        </section>

        <section className="info-card">
          <h2>Phase 1.1 — Platform Foundation</h2>
          <ul>
            <li>✅ Backend API running</li>
            <li>✅ Frontend initialized</li>
            <li>✅ Health check working</li>
          </ul>
        </section>
      </main>
    </div>
  );
}