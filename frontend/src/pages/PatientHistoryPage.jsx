import React, { useState, useEffect } from 'react';
import { 
  History, 
  Activity, 
  UploadCloud, 
  Calendar, 
  FileCheck, 
  ArrowRight, 
  Search, 
  Filter,
  CheckCircle2
} from 'lucide-react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { StatusBadge } from '../components/StatusBadge';

export const PatientHistoryPage = ({ setActivePage, onSelectAnalysis }) => {
  const { currentPatientId } = useAuth();
  const [records, setRecords] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      setLoading(true);
      try {
        if (currentPatientId) {
          const res = await api.getPatientRecords(currentPatientId);
          setRecords(res.records || []);
        }
      } catch (err) {
        console.warn('History fetch error:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, [currentPatientId]);

  const filteredRecords = records.filter(r => {
    const matchesSearch = r.original_filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          r.patient_id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = selectedType === 'all' || r.file_type.toLowerCase() === selectedType.toLowerCase();
    return matchesSearch && matchesType;
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem', maxWidth: '1100px', margin: '0 auto' }}>
      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: '1rem' }}>
        <div>
          <h2>Patient ECG Records History</h2>
          <p>
            Historical record series for Patient ID: <strong>{currentPatientId}</strong>
          </p>
        </div>

        <button
          onClick={() => setActivePage('upload')}
          className="btn btn-teal"
          style={{ fontSize: '0.9rem' }}
        >
          <UploadCloud size={16} />
          Upload New ECG
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="card" style={{ padding: '1rem 1.25rem', display: 'flex', flexWrap: 'wrap', gap: '1rem', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flex: 1, minWidth: '220px' }}>
          <Search size={18} color="var(--color-text-muted)" />
          <input
            type="text"
            className="form-input"
            placeholder="Search by filename or keyword..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ margin: 0 }}
          />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Filter size={16} color="var(--color-text-muted)" />
          <select
            className="form-select"
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            style={{ width: 'auto', minWidth: '150px' }}
          >
            <option value="all">All Formats</option>
            <option value="image">ECG Images (.png/.jpg)</option>
            <option value="xml">ECG XML (.xml)</option>
            <option value="dicom">DICOM (.dcm)</option>
            <option value="numerical">Numerical / CSV</option>
          </select>
        </div>
      </div>

      {/* Records Table */}
      <div className="card" style={{ padding: '1.5rem' }}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem 1rem' }}>
            <Activity size={32} className="spin-slow" color="var(--color-teal)" />
            <div style={{ marginTop: '0.75rem', color: 'var(--color-text-muted)' }}>Loading historical records...</div>
          </div>
        ) : filteredRecords.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--color-text-muted)' }}>
            <History size={36} color="var(--color-grey-border)" style={{ marginBottom: '0.75rem' }} />
            <div style={{ fontWeight: 600, color: 'var(--color-navy)' }}>No matching ECG records found.</div>
            <p style={{ fontSize: '0.85rem', marginTop: '0.25rem' }}>
              Upload an ECG file or load a calibrated sample rhythm to create historical recordings.
            </p>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem', textAlign: 'left' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--color-grey-border)', color: 'var(--color-text-muted)' }}>
                  <th style={{ padding: '0.75rem 0.5rem' }}>Record ID</th>
                  <th style={{ padding: '0.75rem 0.5rem' }}>Upload Timestamp</th>
                  <th style={{ padding: '0.75rem 0.5rem' }}>File Details</th>
                  <th style={{ padding: '0.75rem 0.5rem' }}>Heart Rate</th>
                  <th style={{ padding: '0.75rem 0.5rem' }}>Research Demo Result</th>
                  <th style={{ padding: '0.75rem 0.5rem', textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredRecords.map((r) => (
                  <tr key={r.id} style={{ borderBottom: '1px solid var(--color-grey-border)' }}>
                    <td style={{ padding: '0.85rem 0.5rem', fontWeight: 700, color: 'var(--color-navy)' }}>
                      #{r.id}
                    </td>
                    <td style={{ padding: '0.85rem 0.5rem', color: 'var(--color-text-muted)' }}>
                      {new Date(r.upload_timestamp).toLocaleDateString()} {new Date(r.upload_timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td style={{ padding: '0.85rem 0.5rem' }}>
                      <div style={{ fontWeight: 600, color: 'var(--color-navy)' }}>{r.original_filename}</div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                        {r.file_type.toUpperCase()} • {(r.file_size_bytes / 1024).toFixed(1)} KB
                      </div>
                    </td>
                    <td style={{ padding: '0.85rem 0.5rem', fontWeight: 600 }}>
                      {r.heart_rate_bpm ? `${Math.round(r.heart_rate_bpm)} BPM` : '—'}
                    </td>
                    <td style={{ padding: '0.85rem 0.5rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                        <span>{r.prediction_label}</span>
                        <StatusBadge status={r.status} isDemo={r.is_simulated_demo} />
                      </div>
                    </td>
                    <td style={{ padding: '0.85rem 0.5rem', textAlign: 'right' }}>
                      {r.analysis_id && (
                        <button
                          onClick={() => {
                            if (onSelectAnalysis) onSelectAnalysis(r.analysis_id);
                            setActivePage('results');
                          }}
                          className="btn btn-outline"
                          style={{ fontSize: '0.8rem', padding: '0.35rem 0.75rem' }}
                        >
                          View Report
                          <ArrowRight size={14} />
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
