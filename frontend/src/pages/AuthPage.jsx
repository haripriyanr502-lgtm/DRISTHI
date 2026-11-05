import React, { useState } from 'react';
import { LogIn, UserPlus, ShieldCheck, Heart, AlertCircle, ArrowLeft, Sparkles } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const AuthPage = ({ setActivePage }) => {
  const { login, register } = useAuth();
  const [tab, setTab] = useState('login'); // 'login' or 'register'
  const [role, setRole] = useState('patient'); // 'patient' or 'caregiver' (NO DOCTOR per rule 6)
  
  // Form states
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [patientId, setPatientId] = useState('');
  
  // UI states
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const fillDemoPatient = () => {
    setTab('login');
    setEmail('rajesh.patel@example.com');
    setPassword('patient123');
    setError('');
  };

  const fillDemoCaregiver = () => {
    setTab('login');
    setEmail('priya.patel@example.com');
    setPassword('caregiver123');
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (tab === 'login') {
        const user = await login({ email, password });
        if (user.role === 'caregiver') {
          setActivePage('caregiver-dashboard');
        } else {
          setActivePage('patient-dashboard');
        }
      } else {
        const user = await register({
          email,
          password,
          role,
          full_name: fullName,
          patient_id: patientId ? patientId.trim().toUpperCase() : undefined
        });
        if (user.role === 'caregiver') {
          setActivePage('caregiver-dashboard');
        } else {
          setActivePage('patient-dashboard');
        }
      }
    } catch (err) {
      setError(err.message || 'Authentication failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '520px', margin: '2rem auto' }}>
      <button
        onClick={() => setActivePage('home')}
        className="btn btn-outline"
        style={{ marginBottom: '1.25rem', padding: '0.45rem 0.85rem', fontSize: '0.85rem' }}
      >
        <ArrowLeft size={16} />
        Back to Home
      </button>

      <div className="card" style={{ padding: '2rem' }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <div style={{
            width: '48px',
            height: '48px',
            borderRadius: '10px',
            backgroundColor: 'var(--color-blue-light)',
            color: 'var(--color-blue)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 0.75rem'
          }}>
            {tab === 'login' ? <LogIn size={26} /> : <UserPlus size={26} />}
          </div>
          <h2>{tab === 'login' ? 'Account Sign In' : 'Create an Account'}</h2>
          <p style={{ marginTop: '0.25rem' }}>
            {tab === 'login'
              ? 'Access saved ECG records, profile, and caregiver dashboard.'
              : 'Register as a Patient or Caregiver.'}
          </p>
        </div>

        {/* Demo Fast-Login Pills */}
        <div style={{
          backgroundColor: '#F0F7FB',
          border: '1px solid #D2E4F0',
          borderRadius: 'var(--radius-sm)',
          padding: '0.85rem',
          marginBottom: '1.25rem'
        }}>
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-navy)', marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <Sparkles size={13} color="var(--color-teal)" />
            Quick-Fill Demo Credentials:
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            <button
              type="button"
              onClick={fillDemoPatient}
              className="btn btn-outline"
              style={{ fontSize: '0.75rem', padding: '0.3rem 0.65rem', backgroundColor: '#FFFFFF' }}
            >
              👤 Patient: Rajesh Patel
            </button>
            <button
              type="button"
              onClick={fillDemoCaregiver}
              className="btn btn-outline"
              style={{ fontSize: '0.75rem', padding: '0.3rem 0.65rem', backgroundColor: '#FFFFFF' }}
            >
              🛡️ Caretaker: Priya Patel
            </button>
          </div>
        </div>

        {/* Tab Toggle */}
        <div style={{
          display: 'flex',
          backgroundColor: 'var(--color-grey-light)',
          borderRadius: 'var(--radius-sm)',
          padding: '3px',
          marginBottom: '1.5rem'
        }}>
          <button
            type="button"
            onClick={() => { setTab('login'); setError(''); }}
            style={{
              flex: 1,
              padding: '0.6rem',
              borderRadius: '4px',
              fontWeight: 600,
              fontSize: '0.9rem',
              backgroundColor: tab === 'login' ? '#FFFFFF' : 'transparent',
              color: tab === 'login' ? 'var(--color-navy)' : 'var(--color-text-muted)',
              boxShadow: tab === 'login' ? 'var(--shadow-sm)' : 'none'
            }}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => { setTab('register'); setError(''); }}
            style={{
              flex: 1,
              padding: '0.6rem',
              borderRadius: '4px',
              fontWeight: 600,
              fontSize: '0.9rem',
              backgroundColor: tab === 'register' ? '#FFFFFF' : 'transparent',
              color: tab === 'register' ? 'var(--color-navy)' : 'var(--color-text-muted)',
              boxShadow: tab === 'register' ? 'var(--shadow-sm)' : 'none'
            }}
          >
            Register
          </button>
        </div>

        {/* Error alert */}
        {error && (
          <div style={{
            backgroundColor: 'var(--color-alert-red-light)',
            border: '1px solid var(--color-alert-red)',
            color: 'var(--color-alert-red)',
            padding: '0.75rem 1rem',
            borderRadius: 'var(--radius-sm)',
            marginBottom: '1.25rem',
            fontSize: '0.875rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {tab === 'register' && (
            <div className="form-group">
              <label className="form-label">Select Account Type</label>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                <button
                  type="button"
                  onClick={() => setRole('patient')}
                  style={{
                    padding: '0.85rem 0.5rem',
                    border: `2px solid ${role === 'patient' ? 'var(--color-blue)' : 'var(--color-grey-border)'}`,
                    backgroundColor: role === 'patient' ? 'var(--color-blue-light)' : 'transparent',
                    borderRadius: 'var(--radius-sm)',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: '0.35rem',
                    color: 'var(--color-navy)',
                    fontWeight: 600,
                    fontSize: '0.875rem'
                  }}
                >
                  <Heart size={20} color={role === 'patient' ? 'var(--color-blue)' : 'var(--color-text-muted)'} />
                  Patient Account
                </button>

                <button
                  type="button"
                  onClick={() => setRole('caregiver')}
                  style={{
                    padding: '0.85rem 0.5rem',
                    border: `2px solid ${role === 'caregiver' ? 'var(--color-teal)' : 'var(--color-grey-border)'}`,
                    backgroundColor: role === 'caregiver' ? 'var(--color-teal-light)' : 'transparent',
                    borderRadius: 'var(--radius-sm)',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: '0.35rem',
                    color: 'var(--color-navy)',
                    fontWeight: 600,
                    fontSize: '0.875rem'
                  }}
                >
                  <ShieldCheck size={20} color={role === 'caregiver' ? 'var(--color-teal)' : 'var(--color-text-muted)'} />
                  Caregiver Account
                </button>
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginTop: '0.35rem' }}>
                * Note: Doctor login is not included in this release per architectural guidelines.
              </div>
            </div>
          )}

          {tab === 'register' && (
            <div className="form-group">
              <label className="form-label">Full Name</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. John Doe"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
              />
            </div>
          )}

          <div className="form-group">
            <label className="form-label">Email Address</label>
            <input
              type="email"
              className="form-input"
              placeholder="user@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              className="form-input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
            />
          </div>

          {tab === 'register' && (
            <div className="form-group">
              <label className="form-label">
                {role === 'caregiver' ? 'Assigned Patient ID' : 'Preferred Patient ID (Optional)'}
              </label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. PT-1001"
                value={patientId}
                onChange={(e) => setPatientId(e.target.value)}
                required={role === 'caregiver'}
              />
            </div>
          )}

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', padding: '0.75rem', marginTop: '0.5rem' }}
            disabled={loading}
          >
            {loading ? 'Please wait...' : tab === 'login' ? 'Sign In to DRISTHI' : 'Complete Registration'}
          </button>
        </form>
      </div>
    </div>
  );
};
