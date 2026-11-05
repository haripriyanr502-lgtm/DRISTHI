import React, { useState, useEffect } from 'react';
import { 
  Heart, 
  Activity, 
  UploadCloud, 
  User, 
  History, 
  Calendar, 
  ArrowRight,
  ShieldCheck,
  Plus
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { MetricCard } from '../components/MetricCard';
import { StatusBadge } from '../components/StatusBadge';

export const PatientDashboardPage = ({ setActivePage, onSelectAnalysis }) => {
  const { user, currentPatientId } = useAuth();
  const [profile, setProfile] = useState(null);
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        if (currentPatientId) {
          try {
            const p = await api.getPatientProfile(currentPatientId);
            setProfile(p);
          } catch (e) {}

          const rec = await api.getPatientRecords(currentPatientId);
          setRecords(rec.records || []);
        }
      } catch (err) {
        console.warn('Dashboard fetch error:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [currentPatientId]);

  const latestRecord = records[0] || null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Welcome Bar */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '1rem'
      }}>
        <div>
          <h2>Patient Dashboard</h2>
          <div style={{ color: 'var(--color-text-muted)', fontSize: '0.95rem', marginTop: '0.25rem' }}>
            Welcome back, <strong>{user?.full_name || user?.email}</strong> (Patient ID: <strong>{currentPatientId}</strong>)
          </div>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button
            onClick={() => setActivePage('upload')}
            className="btn btn-teal"
            style={{ fontSize: '0.9rem' }}
          >
            <UploadCloud size={16} />
            Upload New ECG
          </button>
          <button
            onClick={() => setActivePage('profile')}
            className="btn btn-outline"
            style={{ fontSize: '0.9rem' }}
          >
            <User size={16} />
            Profile Details
          </button>
        </div>
      </div>

      {/* Metric Cards Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.25rem' }}>
        <MetricCard
          title="Total Uploaded ECGs"
          value={records.length}
          unit="Records"
          icon={Activity}
          color="var(--color-navy)"
          subtitle="Stored securely with Patient ID"
        />

        <MetricCard
          title="Last Recorded HR"
          value={latestRecord?.heart_rate_bpm ? Math.round(latestRecord.heart_rate_bpm) : '—'}
          unit="BPM"
          icon={Heart}
          color="var(--color-teal)"
          subtitle={latestRecord ? 'From latest rhythm strip' : 'No uploads recorded yet'}
        />

        <MetricCard
          title="Patient Age"
          value={profile?.age || '—'}
          unit="Years"
          icon={User}
          color="var(--color-blue)"
          subtitle={profile?.gender || 'Profile configured'}
        />

        <MetricCard
          title="Research Consent"
          value={profile?.consent_for_research ? 'Opted-In' : 'Private'}
          icon={ShieldCheck}
          color={profile?.consent_for_research ? 'var(--color-teal)' : 'var(--color-text-muted)'}
          subtitle="Rule #5: Explicit opt-in only"
        />
      </div>

      {/* Recent ECG Uploads Table */}
      <div className="card" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
          <div>
            <h3 style={{ fontSize: '1.15rem' }}>Recent ECG Records & Analysis</h3>
            <p style={{ fontSize: '0.85rem' }}>Electrocardiograms uploaded and linked to this patient account.</p>
          </div>

          {records.length > 0 && (
            <button
              onClick={() => setActivePage('history')}
              className="btn btn-outline"
              style={{ fontSize: '0.8rem', padding: '0.4rem 0.8rem' }}
            >
              View Full History ({records.length})
            </button>
          )}
        </div>

        {records.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--color-text-muted)' }}>
            <Activity size={36} style={{ color: 'var(--color-grey-border)', marginBottom: '0.75rem' }} />
            <div style={{ fontWeight: 600, color: 'var(--color-navy)' }}>No ECG records found yet.</div>
            <p style={{ fontSize: '0.85rem', marginTop: '0.25rem' }}>
              Upload your first ECG trace or run a demonstration sample to start monitoring.
            </p>
            <button
              onClick={() => setActivePage('upload')}
              className="btn btn-secondary"
              style={{ marginTop: '1rem', fontSize: '0.875rem' }}
            >
              <UploadCloud size={16} />
              Upload ECG Now
            </button>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem', textAlign: 'left' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--color-grey-border)', color: 'var(--color-text-muted)' }}>
                  <th style={{ padding: '0.75rem 0.5rem' }}>Date & Time</th>
                  <th style={{ padding: '0.75rem 0.5rem' }}>File Name</th>
                  <th style={{ padding: '0.75rem 0.5rem' }}>Type</th>
                  <th style={{ padding: '0.75rem 0.5rem' }}>Heart Rate</th>
                  <th style={{ padding: '0.75rem 0.5rem' }}>Analysis Output</th>
                  <th style={{ padding: '0.75rem 0.5rem', textAlign: 'right' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {records.slice(0, 5).map((rec) => (
                  <tr key={rec.id} style={{ borderBottom: '1px solid var(--color-grey-border)' }}>
                    <td style={{ padding: '0.85rem 0.5rem', color: 'var(--color-text-muted)' }}>
                      {new Date(rec.upload_timestamp).toLocaleDateString()} {new Date(rec.upload_timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td style={{ padding: '0.85rem 0.5rem', fontWeight: 600, color: 'var(--color-navy)' }}>
                      {rec.original_filename}
                    </td>
                    <td style={{ padding: '0.85rem 0.5rem' }}>
                      <span className="badge badge-info" style={{ fontSize: '0.7rem' }}>
                        {rec.file_type.toUpperCase()}
                      </span>
                    </td>
                    <td style={{ padding: '0.85rem 0.5rem', fontWeight: 600 }}>
                      {rec.heart_rate_bpm ? `${Math.round(rec.heart_rate_bpm)} BPM` : '—'}
                    </td>
                    <td style={{ padding: '0.85rem 0.5rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                        <span>{rec.prediction_label}</span>
                        <StatusBadge status={rec.status} isDemo={rec.is_simulated_demo} />
                      </div>
                    </td>
                    <td style={{ padding: '0.85rem 0.5rem', textAlign: 'right' }}>
                      {rec.analysis_id && (
                        <button
                          onClick={() => {
                            if (onSelectAnalysis) onSelectAnalysis(rec.analysis_id);
                            setActivePage('results');
                          }}
                          className="btn btn-outline"
                          style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}
                        >
                          View Results
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
