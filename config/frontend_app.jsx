/**
 * PHASE 7 - Frontend React Complète
 * frontend_app.jsx
 * 
 * Components:
 * - LoginPage: Authentification (Analyst vs Decision Maker)
 * - ScraperInterface: Lancer scraper et tracker progrès
 * - Dashboard: Visualisations par rôle
 * - AnalystView: Charts, tables, metrics
 * - DecisionMakerView: KPIs, insights, recommendations
 */

import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import './style.css';

// ────────────────────────────────────────────────────────────
// API CLIENT
// ────────────────────────────────────────────────────────────

const API = {
  BASE_URL: 'http://localhost:5000/api',
  
  async login(username, password) {
    const res = await fetch(`${this.BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    return res.json();
  },
  
  async startScraper(query, sources) {
    const token = localStorage.getItem('token');
    const res = await fetch(`${this.BASE_URL}/scraper/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ query, sources })
    });
    return res.json();
  },
  
  async getScraperStatus(jobId) {
    const token = localStorage.getItem('token');
    const res = await fetch(`${this.BASE_URL}/scraper/status/${jobId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return res.json();
  },
  
  async getAnalyses() {
    const token = localStorage.getItem('token');
    const res = await fetch(`${this.BASE_URL}/dashboard/analyses`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return res.json();
  },
  
  async getAnalysisData(analysisId) {
    const token = localStorage.getItem('token');
    const res = await fetch(`${this.BASE_URL}/dashboard/data/${analysisId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return res.json();
  },
  
  async getStatsByRole(role) {
    const token = localStorage.getItem('token');
    const res = await fetch(`${this.BASE_URL}/dashboard/stats/${role}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return res.json();
  }
};

// ────────────────────────────────────────────────────────────
// LOGIN PAGE
// ────────────────────────────────────────────────────────────

function LoginPage({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const demoCredentials = [
    { role: 'analyst', username: 'analyst', password: 'analyst123', desc: 'Full Analytics Access' },
    { role: 'decision_maker', username: 'decision_maker', password: 'decision123', desc: 'Executive Overview' }
  ];
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const result = await API.login(username, password);
      if (result.access_token) {
        localStorage.setItem('token', result.access_token);
        localStorage.setItem('user', JSON.stringify(result.user));
        onLogin(result.user);
      } else {
        setError(result.error || 'Login failed');
      }
    } catch (err) {
      setError('Connection error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };
  
  const quickLogin = (creds) => {
    setUsername(creds.username);
    setPassword(creds.password);
  };
  
  return (
    <div className="login-container">
      <div className="login-card">
        <h1>📊 Analysis Platform</h1>
        <p className="subtitle">Enterprise Text Analysis & Reporting</p>
        
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter username"
              required
            />
          </div>
          
          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
              required
            />
          </div>
          
          {error && <div className="error-msg">{error}</div>}
          
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
        
        <div className="demo-section">
          <p className="demo-title">📌 Demo Credentials</p>
          {demoCredentials.map((cred) => (
            <div key={cred.role} className="demo-card">
              <div className="demo-info">
                <strong>{cred.role.replace('_', ' ').toUpperCase()}</strong>
                <p>{cred.desc}</p>
                <code>{cred.username} / {cred.password}</code>
              </div>
              <button
                type="button"
                className="btn btn-secondary btn-sm"
                onClick={() => quickLogin(cred)}
              >
                Try
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ────────────────────────────────────────────────────────────
// SCRAPER INTERFACE
// ────────────────────────────────────────────────────────────

function ScraperInterface() {
  const [query, setQuery] = useState('');
  const [sources, setSources] = useState(['twitter', 'press']);
  const [jobId, setJobId] = useState('');
  const [status, setStatus] = useState('');
  const [progress, setProgress] = useState(0);
  const [loading, setLoading] = useState(false);
  
  const handleStartScraper = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    setLoading(true);
    try {
      const result = await API.startScraper(query, sources);
      setJobId(result.job_id);
      setStatus('running');
      setProgress(10);
    } catch (err) {
      console.error('Scraper error:', err);
    } finally {
      setLoading(false);
    }
  };
  
  // Poll job status
  useEffect(() => {
    if (!jobId || status === 'completed' || status === 'failed') return;
    
    const interval = setInterval(async () => {
      try {
        const result = await API.getScraperStatus(jobId);
        setStatus(result.status);
        setProgress(result.progress);
      } catch (err) {
        console.error('Status error:', err);
      }
    }, 2000);
    
    return () => clearInterval(interval);
  }, [jobId, status]);
  
  return (
    <div className="scraper-panel">
      <h2>🕷️ Web Scraper</h2>
      
      <form onSubmit={handleStartScraper}>
        <div className="form-group">
          <label>Search Query</label>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., product quality, food safety, customer service"
            disabled={loading}
          />
        </div>
        
        <div className="form-group">
          <label>Data Sources</label>
          <div className="checkbox-group">
            {['twitter', 'press', 'reddit'].map((src) => (
              <label key={src} className="checkbox">
                <input
                  type="checkbox"
                  checked={sources.includes(src)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSources([...sources, src]);
                    } else {
                      setSources(sources.filter(s => s !== src));
                    }
                  }}
                  disabled={loading}
                />
                <span>{src.charAt(0).toUpperCase() + src.slice(1)}</span>
              </label>
            ))}
          </div>
        </div>
        
        <button
          type="submit"
          className="btn btn-primary"
          disabled={loading || !query.trim()}
        >
          {loading ? '⏳ Starting...' : '▶️ Start Scraper'}
        </button>
      </form>
      
      {jobId && (
        <div className="job-status">
          <h3>Job ID: {jobId.substring(0, 8)}...</h3>
          <p>Status: <strong>{status.toUpperCase()}</strong></p>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progress}%` }}>
              {progress}%
            </div>
          </div>
          
          {status === 'completed' && (
            <div className="success-msg">
              ✅ Scraping completed! Results ready for analysis.
            </div>
          )}
          
          {status === 'failed' && (
            <div className="error-msg">
              ❌ Scraping failed. Please try again.
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ────────────────────────────────────────────────────────────
// ANALYST VIEW (DETAILED CHARTS & METRICS)
// ────────────────────────────────────────────────────────────

function AnalystView({ data }) {
  if (!data) {
    return <div className="empty-state">📊 Upload or select an analysis to view data</div>;
  }
  
  // Sample data pour demo
  const topicsData = [
    { name: 'Quality', value: 35, docs: 250 },
    { name: 'Safety', value: 25, docs: 180 },
    { name: 'Service', value: 20, docs: 145 },
    { name: 'Price', value: 12, docs: 85 },
    { name: 'Other', value: 8, docs: 55 }
  ];
  
  const temporalData = [
    { month: 'Jan', tweets: 450, articles: 120 },
    { month: 'Feb', tweets: 520, articles: 135 },
    { month: 'Mar', tweets: 480, articles: 125 },
    { month: 'Apr', tweets: 610, articles: 145 },
    { month: 'May', tweets: 750, articles: 165 }
  ];
  
  const metricsData = [
    { metric: 'TTR', value: 0.92, benchmark: 0.80 },
    { metric: 'Coherence', value: 0.45, benchmark: 0.40 },
    { metric: 'Info Density', value: 0.71, benchmark: 0.65 },
    { metric: 'Complexity', value: 8.2, benchmark: 10 }
  ];
  
  const COLORS = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6'];
  
  return (
    <div className="analyst-view">
      <h2>🔬 Detailed Analysis</h2>
      
      <div className="dashboard-grid">
        {/* Topics Distribution */}
        <div className="widget">
          <h3>📈 Topics Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={topicsData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {topicsData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
        
        {/* Temporal Trends */}
        <div className="widget">
          <h3>📅 Activity Timeline</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={temporalData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="tweets" stroke="#3b82f6" />
              <Line type="monotone" dataKey="articles" stroke="#ef4444" />
            </LineChart>
          </ResponsiveContainer>
        </div>
        
        {/* Linguistic Metrics */}
        <div className="widget">
          <h3>📊 Linguistic Metrics</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={metricsData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="metric" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="value" fill="#3b82f6" name="Actual" />
              <Bar dataKey="benchmark" fill="#d1d5db" name="Benchmark" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        
        {/* Keywords */}
        <div className="widget">
          <h3>🏷️ Top Keywords</h3>
          <div className="keywords-cloud">
            <span className="keyword" style={{ fontSize: '28px' }}>quality</span>
            <span className="keyword" style={{ fontSize: '24px' }}>customer</span>
            <span className="keyword" style={{ fontSize: '20px' }}>service</span>
            <span className="keyword" style={{ fontSize: '18px' }}>good</span>
            <span className="keyword" style={{ fontSize: '22px' }}>product</span>
            <span className="keyword" style={{ fontSize: '16px' }}>satisfied</span>
            <span className="keyword" style={{ fontSize: '19px' }}>issue</span>
            <span className="keyword" style={{ fontSize: '21px' }}>recommend</span>
          </div>
        </div>
      </div>
    </div>
  );
}

// ────────────────────────────────────────────────────────────
// DECISION MAKER VIEW (KPIs & INSIGHTS)
// ────────────────────────────────────────────────────────────

function DecisionMakerView({ data }) {
  if (!data) {
    return <div className="empty-state">📊 Upload or select an analysis to view insights</div>;
  }
  
  const kpis = [
    { label: 'Overall Sentiment', value: '+68%', color: '#10b981', trend: '↑' },
    { label: 'Engagement Rate', value: '12.5%', color: '#3b82f6', trend: '↑' },
    { label: 'Risk Score', value: 'MEDIUM', color: '#f59e0b', trend: '→' },
    { label: 'Coverage', value: '1.2M', color: '#8b5cf6', trend: '↑' }
  ];
  
  const insights = [
    {
      icon: '✅',
      title: 'Strong Product Quality',
      description: 'Quality-related mentions increased 45% with 92% positive sentiment'
    },
    {
      icon: '⚠️',
      title: 'Safety Concerns Emerging',
      description: 'Food safety mentions peaked in April, requires immediate attention'
    },
    {
      icon: '📈',
      title: 'Customer Engagement',
      description: 'Social media engagement up 35%, driven by customer service initiative'
    },
    {
      icon: '🎯',
      title: 'Competitive Positioning',
      description: 'Brand favorability vs competitors improved to 78%'
    }
  ];
  
  const recommendations = [
    'Continue leveraging positive quality feedback in marketing campaigns',
    'Establish rapid response team for emerging safety concerns',
    'Invest further in customer service enhancement programs',
    'Monitor competitive landscape weekly during peak engagement periods'
  ];
  
  return (
    <div className="decision-view">
      <h2>👔 Executive Dashboard</h2>
      
      {/* KPIs */}
      <div className="kpi-grid">
        {kpis.map((kpi, idx) => (
          <div key={idx} className="kpi-card" style={{ borderColor: kpi.color }}>
            <span className="kpi-trend" style={{ color: kpi.color }}>{kpi.trend}</span>
            <p className="kpi-label">{kpi.label}</p>
            <p className="kpi-value" style={{ color: kpi.color }}>{kpi.value}</p>
          </div>
        ))}
      </div>
      
      {/* Executive Summary */}
      <div className="widget">
        <h3>📋 Executive Summary</h3>
        <div className="summary-text">
          <p>
            Based on comprehensive analysis of 1.2M mentions across press and social media,
            your organization demonstrates strong market positioning with particular strength
            in product quality perception. However, emerging safety concerns require strategic
            attention. Current engagement levels (12.5% interaction rate) indicate effective
            communication, with 68% positive sentiment overall.
          </p>
        </div>
      </div>
      
      {/* Key Insights */}
      <div className="insights-grid">
        {insights.map((insight, idx) => (
          <div key={idx} className="insight-card">
            <span className="insight-icon">{insight.icon}</span>
            <h4>{insight.title}</h4>
            <p>{insight.description}</p>
          </div>
        ))}
      </div>
      
      {/* Recommendations */}
      <div className="widget">
        <h3>💡 Strategic Recommendations</h3>
        <ol className="recommendations-list">
          {recommendations.map((rec, idx) => (
            <li key={idx}>{rec}</li>
          ))}
        </ol>
      </div>
    </div>
  );
}

// ────────────────────────────────────────────────────────────
// MAIN APP COMPONENT
// ────────────────────────────────────────────────────────────

export default function App() {
  const [user, setUser] = useState(null);
  const [currentView, setCurrentView] = useState('scraper');
  const [analyses, setAnalyses] = useState([]);
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);
  
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
      loadAnalyses();
    }
  }, []);
  
  const loadAnalyses = async () => {
    try {
      const result = await API.getAnalyses();
      setAnalyses(result.analyses || []);
    } catch (err) {
      console.error('Load error:', err);
    }
  };
  
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    setCurrentView('scraper');
    setAnalyses([]);
  };
  
  if (!user) {
    return <LoginPage onLogin={setUser} />;
  }
  
  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="header-left">
          <h1>📊 Analysis Platform</h1>
          <span className="role-badge">{user.role.replace('_', ' ').toUpperCase()}</span>
        </div>
        <div className="header-right">
          <span className="user-name">{user.username}</span>
          <button className="btn btn-secondary btn-sm" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </header>
      
      {/* Main Content */}
      <div className="app-body">
        {/* Sidebar */}
        <aside className="sidebar">
          <nav className="nav-menu">
            <button
              className={`nav-item ${currentView === 'scraper' ? 'active' : ''}`}
              onClick={() => setCurrentView('scraper')}
            >
              🕷️ Scraper
            </button>
            <button
              className={`nav-item ${currentView === 'dashboard' ? 'active' : ''}`}
              onClick={() => setCurrentView('dashboard')}
            >
              📊 Dashboard
            </button>
            <button
              className={`nav-item ${currentView === 'reports' ? 'active' : ''}`}
              onClick={() => setCurrentView('reports')}
            >
              📄 Reports
            </button>
          </nav>
          
          {analyses.length > 0 && (
            <div className="analyses-list">
              <h4>📁 Recent Analyses</h4>
              {analyses.map((analysis) => (
                <button
                  key={analysis.id}
                  className={`analysis-item ${selectedAnalysis?.id === analysis.id ? 'active' : ''}`}
                  onClick={() => setSelectedAnalysis(analysis)}
                >
                  {analysis.name}
                </button>
              ))}
            </div>
          )}
        </aside>
        
        {/* Main Panel */}
        <main className="main-panel">
          {currentView === 'scraper' && <ScraperInterface />}
          
          {currentView === 'dashboard' && user.role === 'analyst' && (
            <AnalystView data={selectedAnalysis} />
          )}
          
          {currentView === 'dashboard' && user.role === 'decision_maker' && (
            <DecisionMakerView data={selectedAnalysis} />
          )}
          
          {currentView === 'reports' && (
            <div className="reports-panel">
              <h2>📄 Generated Reports</h2>
              <p>Semantic, Temporal, Cognitive Summaries & Executive Reports</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
