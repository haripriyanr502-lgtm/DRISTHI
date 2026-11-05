import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  AlertTriangle, 
  Heart, 
  Radio, 
  Clock, 
  Check, 
  User, 
  Activity, 
  Info,
  Cpu
} from 'lucide-react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { MetricCard } from '../components/MetricCard';

export const CaregiverDashboardPage = ({ setActivePage }) => {
  const { user } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [ackFeedback, setAckFeedback] = useState('');

  const fetchCaregiverData = async () => {
    try {
      const data = await api.getCaregiverDashboard();
      setDashboardData(data);
    } catch (err) {
      console.warn('Caregiver fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCaregiverData();
  }, []);

  const handleAcknowledge = async (alertId) => {
    try {
      await api.acknowledgeAlert(alertId, user?.full_name || 'Caregiver');
      setAckFeedback(`Alert #${alertId} successfully acknowledged.`);
      setTimeout(() => setAckFeedback(''), 4000);
      fetchCaregiverData();
    } catch (err) {
      alert(err.message || 'Failed to acknowledge alert.');
    }
  };

  if (loading) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
        <Activity size={36} className="spin-slow" color="var(--color-teal)" />
        <h3 style={{ marginTop: '1rem' }}>Loading Caregiver Portal...</h3>
      </div>
    );
  }

  const assignedPatients = dashboardData?.assigned_patients || [];
  const alerts = dashboardData?.alerts || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      {/* Caregiver Welcome Banner */}
      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: '1rem' }}>
        <div>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.4rem',
            color: 'var(--color-teal)',
            fontWeight: 700,
            fontSize: '0.8rem',
            textTransform: 'uppercase',
            letterSpacing: '0.04em',
            marginBottom: '0.25rem'
          }}>
            <ShieldCheck size={16} />
            Caregiver Oversight Portal
          </div>
          <h2>Caregiver Dashboard</h2>
          <p>
            Supervision and cardiac telemetry advisory feed for assigned patients.
          </p>
        </div>

        <div style={{
          backgroundColor: 'var(--color-white)',
          border: '1px solid var(--color-grey-border)',
          borderRadius: 'var(--radius-sm)',
          padding: '0.5rem 1rem',
          fontSize: '0.85rem'
        }}>
          Caregiver: <strong>{dashboardData?.caregiver?.name || user?.full_name || 'Caregiver'}</strong> ({dashboardData?.caregiver?.email || user?.email})
        </div>
      </div>

      {/* Mandatory Safety Notice: Hardware Telemetry Staging (Module 8 & 9) */}
      <div className="card" style={{
        backgroundColor: '#FFFBEB',
        borderLeft: '4px solid #F59E0B',
        padding: '1.25rem 1.5rem',
        borderRadius: '0 var(--radius-sm) var(--radius-sm) 0'
      }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.85rem' }}>
          <Radio size={22} color="#B45309" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <div style={{ fontWeight: 700, color: '#92400E', fontSize: '0.95rem', marginBottom: '0.25rem' }}>
              Hardware Monitoring Staging Notice (ESP32 + AD8232 Sensor)
            </div>
            <p style={{ color: '#78350F', fontSize: '0.875rem', margin: 0, lineHeight: 1.5 }}>
              Per development rule #15, live sensor telemetry is explicitly marked as <strong>awaiting hardware integration</strong> until real ESP32 transmission packets are received.
              Alerts displayed in this initial phase represent simulated threshold events for interface testing. Emergency response systems are not operational.
            </p>
          </div>
        </div>
      </div>

      {/* Metric Cards Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.25rem' }}>
        <MetricCard
          title="Assigned Patients"
          value={assignedPatients.length}
          unit="Patients"
          icon={User}
          color="var(--color-navy)"
          subtitle="Linked by unique Patient ID"
        />

        <MetricCard
          title="Active Alerts"
          value={alerts.filter(a => !a.is_acknowledged).length}
          unit="Pending"
          icon={AlertTriangle}
          color="var(--color-alert-red)"
          subtitle="Simulated threshold advisories"
        />

        <MetricCard
          title="Telemetry Status"
          value="Staged"
          icon={Radio}
          color="var(--color-blue)"
          subtitle="ESP32 telemetry endpoint ready"
        />

        <MetricCard
          title="Lead Quality Check"
          value="Calibrated"
          icon={Activity}
          color="var(--color-teal)"
          subtitle="AD8232 lead-off detection"
        />
      </div>

      {ackFeedback && (
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
          <Check size={18} />
          <span>{ackFeedback}</span>
        </div>
      )}

      {/* Active Alerts Section */}
      <div className="card" style={{ padding: '1.5rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
          <div>
            <h3 style={{ fontSize: '1.15rem' }}>Recent Alerts & Advisory Notifications</h3>
            <p style={{ fontSize: '0.85rem' }}>Patient monitoring alerts requiring caregiver acknowledgement.</p>
          </div>
          <span className="badge badge-demo" style={{ fontWeight: 700 }}>
            DEMO DATA – NOT A REAL PATIENT RECORD
          </span>
        </div>

        {alerts.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2rem 1rem', color: 'var(--color-text-muted)' }}>
            No alerts logged for assigned patients.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            {alerts.map((alert) => (
              <div
                key={alert.id}
                style={{
                  border: `1px solid ${alert.is_acknowledged ? 'var(--color-grey-border)' : 'var(--color-warning)'}`,
                  backgroundColor: alert.is_acknowledged ? 'var(--color-bg-light)' : '#FFFDF7',
                  borderRadius: 'var(--radius-sm)',
                  padding: '1rem 1.25rem',
                  display: 'flex',
                  flexWrap: 'wrap',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: '1rem'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.85rem' }}>
                  <div style={{
                    color: alert.is_acknowledged ? 'var(--color-text-muted)' : 'var(--color-warning)',
                    marginTop: '2px'
                  }}>
                    <AlertTriangle size={20} />
                  </div>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ fontWeight: 700, color: 'var(--color-navy)', fontSize: '0.95rem' }}>
                        {alert.title}
                      </span>
                      <span className="badge badge-info" style={{ fontSize: '0.7rem' }}>
                        {alert.patient_id}
                      </span>
                      {alert.is_hardware_simulation && (
                        <span className="badge badge-demo" style={{ fontSize: '0.65rem' }}>
                          Simulated Event
                        </span>
                      )}
                    </div>
                    <p style={{ margin: '0.25rem 0 0', fontSize: '0.875rem', color: 'var(--color-text-dark)' }}>
                      {alert.message}
                    </p>
                    <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginTop: '0.35rem' }}>
                      Timestamp: {new Date(alert.created_at).toLocaleString()}
                      {alert.is_acknowledged && (
                        <span style={{ color: 'var(--color-success)', marginLeft: '0.5rem', fontWeight: 600 }}>
                          • Acknowledged by {alert.acknowledged_by} ({new Date(alert.acknowledged_at).toLocaleTimeString()})
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <div>
                  {!alert.is_acknowledged ? (
                    <button
                      onClick={() => handleAcknowledge(alert.id)}
                      className="btn btn-teal"
                      style={{ fontSize: '0.8rem', padding: '0.45rem 0.9rem' }}
                    >
                      <Check size={14} />
                      Acknowledge Alert
                    </button>
                  ) : (
                    <span className="badge badge-success" style={{ fontSize: '0.75rem' }}>
                      Acknowledged
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Assigned Patients Overview */}
      <div className="card" style={{ padding: '1.5rem' }}>
        <h3 style={{ fontSize: '1.15rem', marginBottom: '0.5rem' }}>Assigned Patient Profiles</h3>
        <p style={{ fontSize: '0.85rem', marginBottom: '1.25rem' }}>
          Overview of patients supervised by this caregiver account.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
          {assignedPatients.map((pat, idx) => (
            <div
              key={idx}
              style={{
                border: '1px solid var(--color-grey-border)',
                borderRadius: 'var(--radius-sm)',
                padding: '1.25rem',
                backgroundColor: '#FFFFFF'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                <span style={{ fontWeight: 700, fontSize: '1.05rem', color: 'var(--color-navy)' }}>
                  Patient: {pat.patient_id}
                </span>
                <span className="badge badge-info" style={{ fontSize: '0.7rem' }}>
                  Age {pat.age} • {pat.gender}
                </span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.825rem' }}>
                <div>
                  <span style={{ color: 'var(--color-text-muted)' }}>Cardiac Condition:</span>{' '}
                  <strong>{pat.existing_condition}</strong>
                </div>
                <div>
                  <span style={{ color: 'var(--color-text-muted)' }}>Medical History:</span>{' '}
                  <span>{pat.medical_history}</span>
                </div>
                <div>
                  <span style={{ color: 'var(--color-text-muted)' }}>Hardware Stream:</span>{' '}
                  <span style={{ color: 'var(--color-warning)', fontWeight: 600 }}>{pat.hardware_monitoring_status}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
