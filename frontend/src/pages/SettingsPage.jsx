import React, { useState, useEffect } from 'react';
import { 
  Settings, 
  Server, 
  Shield, 
  Cpu, 
  RefreshCw, 
  CheckCircle2, 
  AlertCircle,
  Database,
  Radio,
  UserCheck
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

export const SettingsPage = ({ setActivePage }) => {
  const { user, role, isPublic, currentPatientId, updateActivePatientId, logout } = useAuth();
  
  const [pidInput, setPidInput] = useState(currentPatientId || 'PT-1001');
  const [healthStatus, setHealthStatus] = useState(null);
  const [hardwareStatus, setHardwareStatus] = useState(null);
  const [healthLoading, setHealthLoading] = useState(false);
  const [saveMsg, setSaveMsg] = useState('');

  const checkDiagnostics = async () => {
    setHealthLoading(true);
    try {
      const h = await api.getHealth();
      setHealthStatus(h);
      const hw = await api.getHardwareStatus();
      setHardwareStatus(hw);
    } catch (err) {
      setHealthStatus({ status: 'unreachable', error: err.message });
    } finally {
      setHealthLoading(false);
    }
  };

  useEffect(() => {
    checkDiagnostics();
  }, []);

  const handleUpdatePid = (e) => {
    e.preventDefault();
    if (pidInput.trim()) {
      updateActivePatientId(pidInput.trim());
      setSaveMsg(`Active Patient ID set to ${pidInput.trim().toUpperCase()}`);
      setTimeout(() => setSaveMsg(''), 3000);
    }
  };

  return (
    <div style={{ maxWidth: '840px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div>
        <h2>System Settings & Diagnostics</h2>
        <p>
          Configure active patient session, verify backend microservices, and review research parameters.
        </p>
      </div>

      {saveMsg && (
        <div style={{
          backgroundColor: 'var(--color-success-light)',
          border: '1px solid var(--color-success)',
          color: 'var(--color-success)',
          padding: '0.75rem 1rem',
          borderRadius: 'var(--radius-sm)',
          fontSize: '0.9rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          <CheckCircle2 size={18} />
          <span>{saveMsg}</span>
        </div>
      )}

      {/* Active Session & Patient ID Switcher */}
      <div className="card" style={{ padding: '1.75rem' }}>
        <h3 style={{ fontSize: '1.15rem', marginBottom: '0.5rem' }}>Active Session Context</h3>
        <p style={{ fontSize: '0.85rem', marginBottom: '1.25rem' }}>
          Organizes which patient stream is selected for ECG uploads and historical reports.
        </p>

        <form onSubmit={handleUpdatePid} style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', alignItems: 'flex-end' }}>
          <div className="form-group" style={{ margin: 0, flex: 1, minWidth: '220px' }}>
            <label className="form-label">Active Patient ID</label>
            <input
              type="text"
              className="form-input"
              value={pidInput}
              onChange={(e) => setPidInput(e.target.value)}
              placeholder="e.g. PT-1001"
              required
            />
          </div>

          <button type="submit" className="btn btn-primary" style={{ padding: '0.65rem 1.25rem' }}>
            Update Active ID
          </button>
        </form>

        <div style={{
          marginTop: '1.25rem',
          paddingTop: '1rem',
          borderTop: '1px solid var(--color-grey-border)',
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '1rem',
          fontSize: '0.85rem'
        }}>
          <div>
            Current Role: <strong>{role.toUpperCase()}</strong>
            {user && <span> ({user.email})</span>}
          </div>

          {isPublic ? (
            <button
              onClick={() => setActivePage('auth')}
              className="btn btn-outline"
              style={{ fontSize: '0.8rem', padding: '0.35rem 0.75rem' }}
            >
              Sign In to Registered Account
            </button>
          ) : (
            <button
              onClick={logout}
              className="btn btn-outline"
              style={{ fontSize: '0.8rem', padding: '0.35rem 0.75rem', color: 'var(--color-alert-red)' }}
            >
              Sign Out
            </button>
          )}
        </div>
      </div>

      {/* Backend Health & Connectivity */}
      <div className="card" style={{ padding: '1.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
          <div>
            <h3 style={{ fontSize: '1.15rem' }}>Backend Microservice Health</h3>
            <p style={{ fontSize: '0.85rem' }}>Diagnostics for FastAPI REST services, SQLite DB, and AI adapter.</p>
          </div>

          <button
            onClick={checkDiagnostics}
            className="btn btn-outline"
            style={{ fontSize: '0.8rem', padding: '0.35rem 0.75rem' }}
            disabled={healthLoading}
          >
            <RefreshCw size={14} className={healthLoading ? 'spin-slow' : ''} />
            Re-check
          </button>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '1rem',
          fontSize: '0.85rem'
        }}>
          <div style={{ padding: '1rem', backgroundColor: 'var(--color-bg-light)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ color: 'var(--color-text-muted)' }}>REST API Server</div>
            <div style={{ fontWeight: 700, marginTop: '0.25rem', color: healthStatus?.status === 'operational' ? 'var(--color-teal)' : 'var(--color-alert-red)' }}>
              {healthStatus?.status === 'operational' ? '● Operational (Port 8000)' : '○ Offline / Reconnecting'}
            </div>
          </div>

          <div style={{ padding: '1rem', backgroundColor: 'var(--color-bg-light)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ color: 'var(--color-text-muted)' }}>Database Storage</div>
            <div style={{ fontWeight: 700, marginTop: '0.25rem', color: healthStatus?.database === 'healthy' ? 'var(--color-teal)' : 'var(--color-warning)' }}>
              {healthStatus?.database === 'healthy' ? '● Healthy (SQLite / SQLite3)' : 'Checking connection...'}
            </div>
          </div>

          <div style={{ padding: '1rem', backgroundColor: 'var(--color-bg-light)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ color: 'var(--color-text-muted)' }}>AI Inference Pipeline</div>
            <div style={{ fontWeight: 700, marginTop: '0.25rem', color: '#D97706' }}>
              ● Research Demo Staging
            </div>
          </div>

          <div style={{ padding: '1rem', backgroundColor: 'var(--color-bg-light)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ color: 'var(--color-text-muted)' }}>Hardware ESP32 Stream</div>
            <div style={{ fontWeight: 700, marginTop: '0.25rem', color: '#2563EB' }}>
              ● Awaiting Pairing
            </div>
          </div>
        </div>
      </div>

      {/* Future Hardware Telemetry Configuration Specifications */}
      <div className="card" style={{ padding: '1.75rem' }}>
        <h3 style={{ fontSize: '1.15rem', marginBottom: '0.5rem' }}>Hardware & Sensor Integration Specs</h3>
        <p style={{ fontSize: '0.85rem', marginBottom: '1.25rem' }}>
          Staged specifications for live cardiac monitoring using microcontroller hardware.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem', fontSize: '0.85rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '0.5rem', borderBottom: '1px solid var(--color-grey-border)' }}>
            <span style={{ color: 'var(--color-navy)', fontWeight: 600 }}>Analog Front End:</span>
            <span>Analog Devices AD8232 (Single Lead ECG Heart Rate Monitor)</span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '0.5rem', borderBottom: '1px solid var(--color-grey-border)' }}>
            <span style={{ color: 'var(--color-navy)', fontWeight: 600 }}>Microcontroller SoC:</span>
            <span>Espressif ESP32 Dual-Core (Wi-Fi 802.11 b/g/n + BLE)</span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '0.5rem', borderBottom: '1px solid var(--color-grey-border)' }}>
            <span style={{ color: 'var(--color-navy)', fontWeight: 600 }}>Sampling ADC Resolution:</span>
            <span>12-bit SAR ADC (250 Samples/Sec Target Rate)</span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '0.5rem', borderBottom: '1px solid var(--color-grey-border)' }}>
            <span style={{ color: 'var(--color-navy)', fontWeight: 600 }}>Lead-Off Detection (LO+ / LO-):</span>
            <span>Supported via GPIO interrupt handlers</span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: 'var(--color-navy)', fontWeight: 600 }}>Telemetry Ingestion Endpoint:</span>
            <span style={{ fontFamily: 'monospace' }}>POST /api/v1/monitoring/telemetry</span>
          </div>
        </div>
      </div>
    </div>
  );
};
