// Insurance Leads Dashboard Component for Riff
// Copy this entire file into your Riff project

import React, { useState, useEffect } from 'react';

const InsuranceLeadsDashboard = () => {
  const [leads, setLeads] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  // TODO: Update this URL to your deployed FastAPI backend
  const API_BASE_URL = 'http://localhost:8000';

  useEffect(() => {
    fetchLeads();
  }, []);

  const fetchLeads = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/leads`);
      const data = await response.json();
      setLeads(data.leads || []);
      setStats(data.stats || {});
      setError(null);
    } catch (err) {
      setError('Failed to load leads');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filteredLeads = leads.filter(lead =>
    lead['Job Title']?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    lead['Company Name']?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    lead['Location']?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getUrgencyColor = (score) => {
    const urgency = parseFloat(score);
    if (urgency >= 80) return '#ef4444';
    if (urgency >= 50) return '#f59e0b';
    return '#10b981';
  };

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(to bottom right, #eff6ff, #e0e7ff)' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ width: '64px', height: '64px', border: '4px solid #e5e7eb', borderTop: '4px solid #4f46e5', borderRadius: '50%', animation: 'spin 1s linear infinite', margin: '0 auto 1rem' }}></div>
          <p style={{ color: '#6b7280', fontSize: '1.125rem' }}>Loading insurance leads...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(to bottom right, #eff6ff, #e0e7ff)' }}>
        <div style={{ background: 'white', borderRadius: '0.5rem', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)', padding: '2rem', maxWidth: '28rem' }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#1f2937', marginBottom: '0.5rem', textAlign: 'center' }}>Error</h2>
          <p style={{ color: '#6b7280', textAlign: 'center', marginBottom: '1rem' }}>{error}</p>
          <button
            onClick={fetchLeads}
            style={{ width: '100%', background: '#4f46e5', color: 'white', padding: '0.5rem 1rem', borderRadius: '0.5rem', border: 'none', cursor: 'pointer' }}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(to bottom right, #eff6ff, #e0e7ff)', padding: '2rem 1rem' }}>
      <div style={{ maxWidth: '1280px', margin: '0 auto' }}>

        {/* Header */}
        <div style={{ marginBottom: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <h1 style={{ fontSize: '2.25rem', fontWeight: 'bold', color: '#111827', marginBottom: '0.5rem' }}>
                🎯 Insurance Leads Dashboard
              </h1>
              <p style={{ color: '#6b7280' }}>
                Real-time commercial insurance job opportunities with contact data
              </p>
            </div>
            <button
              onClick={fetchLeads}
              style={{ background: '#4f46e5', color: 'white', padding: '0.75rem 1.5rem', borderRadius: '0.5rem', border: 'none', cursor: 'pointer', fontWeight: '600', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
            >
              Refresh Data
            </button>
          </div>

          {/* Stats Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
            <div style={{ background: 'white', borderRadius: '0.75rem', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)', padding: '1.5rem', borderLeft: '4px solid #4f46e5' }}>
              <p style={{ color: '#6b7280', fontSize: '0.875rem', fontWeight: '500' }}>Total Leads</p>
              <p style={{ fontSize: '1.875rem', fontWeight: 'bold', color: '#111827' }}>{stats.total_leads || 0}</p>
            </div>

            <div style={{ background: 'white', borderRadius: '0.75rem', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)', padding: '1.5rem', borderLeft: '4px solid #ef4444' }}>
              <p style={{ color: '#6b7280', fontSize: '0.875rem', fontWeight: '500' }}>High Priority</p>
              <p style={{ fontSize: '1.875rem', fontWeight: 'bold', color: '#111827' }}>{stats.high_priority || 0}</p>
            </div>

            <div style={{ background: 'white', borderRadius: '0.75rem', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)', padding: '1.5rem', borderLeft: '4px solid #10b981' }}>
              <p style={{ color: '#6b7280', fontSize: '0.875rem', fontWeight: '500' }}>With Contacts</p>
              <p style={{ fontSize: '1.875rem', fontWeight: 'bold', color: '#111827' }}>{stats.with_contacts || 0}</p>
            </div>

            <div style={{ background: 'white', borderRadius: '0.75rem', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)', padding: '1.5rem', borderLeft: '4px solid #8b5cf6' }}>
              <p style={{ color: '#6b7280', fontSize: '0.875rem', fontWeight: '500' }}>Companies</p>
              <p style={{ fontSize: '1.875rem', fontWeight: 'bold', color: '#111827' }}>{stats.unique_companies || 0}</p>
            </div>
          </div>

          {/* Last Updated */}
          <div style={{ textAlign: 'center', color: '#6b7280', fontSize: '0.875rem', marginBottom: '1.5rem' }}>
            📅 Last updated: {stats.last_updated || 'Unknown'}
          </div>

          {/* Search Bar */}
          <div style={{ background: 'white', borderRadius: '0.75rem', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)', padding: '1.5rem', marginBottom: '2rem' }}>
            <input
              type="text"
              placeholder="🔍 Search by job title, company, or location..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{ width: '100%', padding: '0.75rem', border: '1px solid #d1d5db', borderRadius: '0.5rem', fontSize: '1rem' }}
            />
            <p style={{ color: '#6b7280', fontSize: '0.875rem', marginTop: '0.75rem' }}>
              Showing {filteredLeads.length} of {leads.length} leads
            </p>
          </div>
        </div>

        {/* Leads List */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1.5rem' }}>
          {filteredLeads.map((lead, index) => (
            <div
              key={index}
              style={{ background: 'white', borderRadius: '0.75rem', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)', padding: '1.5rem', border: '1px solid #e5e7eb', transition: 'box-shadow 0.3s' }}
              onMouseEnter={(e) => e.currentTarget.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.1)'}
              onMouseLeave={(e) => e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)'}
            >
              {/* Header */}
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                <div>
                  <h3 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#111827', marginBottom: '0.5rem' }}>
                    {lead['Job Title']}
                  </h3>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', color: '#6b7280', fontSize: '0.875rem' }}>
                    <span>🏢 {lead['Company Name']}</span>
                    <span>📍 {lead['Location']}</span>
                    <span style={{ color: '#ef4444', fontWeight: '600' }}>📅 {lead['Days Open']} days open</span>
                  </div>
                </div>
                <span
                  style={{
                    padding: '0.5rem 1rem',
                    borderRadius: '9999px',
                    fontSize: '0.75rem',
                    fontWeight: '600',
                    color: 'white',
                    background: getUrgencyColor(lead['Urgency Score'])
                  }}
                >
                  {parseFloat(lead['Urgency Score']).toFixed(0)}% Urgent
                </span>
              </div>

              {/* Salary */}
              {lead['Salary Range'] && !lead['Salary Range'].includes('nan') && (
                <div style={{ marginBottom: '1rem', color: '#10b981', fontWeight: '600' }}>
                  💰 {lead['Salary Range']}
                </div>
              )}

              {/* Contacts */}
              <div style={{ background: '#f9fafb', borderRadius: '0.5rem', padding: '1rem', marginBottom: '1rem' }}>
                <h4 style={{ fontWeight: '600', color: '#111827', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  👥 Leadership Contacts
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                  {[1, 2, 3].map((num) => {
                    const name = lead[`Leadership ${num} Name`];
                    const title = lead[`Leadership ${num} Title`];
                    const email = lead[`Leadership ${num} Email`];
                    if (!name) return null;

                    return (
                      <div key={num} style={{ background: 'white', borderRadius: '0.5rem', padding: '0.75rem', border: '1px solid #e5e7eb' }}>
                        <p style={{ fontWeight: '600', color: '#111827', fontSize: '0.875rem' }}>{name}</p>
                        <p style={{ color: '#6b7280', fontSize: '0.75rem', marginBottom: '0.5rem' }}>{title}</p>
                        {email && (
                          <p style={{ color: '#4f46e5', fontSize: '0.75rem' }}>✉️ {email}</p>
                        )}
                      </div>
                    );
                  })}
                </div>

                {/* Company Info */}
                <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid #e5e7eb', display: 'flex', flexWrap: 'wrap', gap: '1rem', fontSize: '0.875rem' }}>
                  {lead['Company Website'] && lead['Company Website'] !== 'nan' && (
                    <a
                      href={lead['Company Website']}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ color: '#4f46e5', textDecoration: 'none' }}
                    >
                      🌐 {lead['Company Website']}
                    </a>
                  )}
                  {lead['Phone Number'] && lead['Phone Number'] !== '' && (
                    <span style={{ color: '#6b7280' }}>📞 {lead['Phone Number']}</span>
                  )}
                </div>
              </div>

              {/* Action Buttons */}
              <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                {lead['Job URL'] && (
                  <a
                    href={lead['Job URL']}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ flex: '1', minWidth: '200px', background: '#4f46e5', color: 'white', padding: '0.75rem 1rem', borderRadius: '0.5rem', textAlign: 'center', textDecoration: 'none', fontWeight: '600', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
                  >
                    View Job Posting 🔗
                  </a>
                )}
                <button
                  style={{ padding: '0.75rem 1.5rem', border: '2px solid #4f46e5', color: '#4f46e5', borderRadius: '0.5rem', background: 'transparent', cursor: 'pointer', fontWeight: '600' }}
                  onClick={() => alert(`Add ${lead['Company Name']} to CRM`)}
                >
                  Add to CRM
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* No Results */}
        {filteredLeads.length === 0 && (
          <div style={{ background: 'white', borderRadius: '0.75rem', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)', padding: '3rem', textAlign: 'center' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔍</div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#111827', marginBottom: '0.5rem' }}>No leads found</h3>
            <p style={{ color: '#6b7280' }}>Try adjusting your search criteria</p>
          </div>
        )}
      </div>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default InsuranceLeadsDashboard;
