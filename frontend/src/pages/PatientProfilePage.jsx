import React, { useState, useEffect } from 'react';
import { User, Heart, Shield, Save, CheckCircle2, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

export const PatientProfilePage = () => {
  const { currentPatientId, updateActivePatientId } = useAuth();
  
  // Profile fields strictly limited to required & simple optional fields per Module 2
  const [patientId, setPatientId] = useState(currentPatientId || 'PT-1001');
  const [age, setAge] = useState(45);
  const [gender, setGender] = useState('Not specified');
  const [medicalHistory, setMedicalHistory] = useState('');
  const [existingCondition, setExistingCondition] = useState('');
  const [consentForResearch, setConsentForResearch] = useState(false);

  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    const fetchProfile = async () => {
      if (!currentPatientId) return;
      try {
        const data = await api.getPatientProfile(currentPatientId);
        setPatientId(data.patient_id);
        setAge(data.age);
        setGender(data.gender || 'Not specified');
        setMedicalHistory(data.medical_history || '');
        setExistingCondition(data.existing_condition || '');
        setConsentForResearch(data.consent_for_research || false);
      } catch (err) {
        // Not found yet is normal for new patient IDs
      }
    };
    fetchProfile();
  }, [currentPatientId]);

  const handleSave = async (e) => {
    e.preventDefault();
    setSuccessMsg('');
    setErrorMsg('');
    setLoading(true);

    try {
      const payload = {
        patient_id: patientId.trim().toUpperCase(),
        age: parseInt(age, 10),
        gender,
        medical_history: medicalHistory,
        existing_condition: existingCondition,
        consent_for_research: consentForResearch
      };

      const res = await api.savePatientProfile(payload);
      updateActivePatientId(res.patient_id);
      setSuccessMsg(`Patient profile [${res.patient_id}] successfully saved.`);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to save patient profile.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '720px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <div>
        <h2>Patient Profile</h2>
        <p>
          Manage core patient identifiers and clinical baseline information.
        </p>
      </div>

      {/* Clinical Guidance Notice */}
      <div className="disclaimer-banner">
        <Heart size={20} style={{ flexShrink: 0, marginTop: '2px' }} />
        <div>
          <strong>Clinical Principle:</strong> Patient demographics (age, medical history) are recorded solely for baseline contextual reference. Demographic information is never treated as a substitute for objective ECG evidence.
        </div>
      </div>

      {successMsg && (
        <div style={{
          backgroundColor: 'var(--color-success-light)',
          border: '1px solid var(--color-success)',
          color: 'var(--color-success)',
          padding: '0.75rem 1rem',
          borderRadius: 'var(--radius-sm)',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          fontSize: '0.9rem'
        }}>
          <CheckCircle2 size={18} />
          <span>{successMsg}</span>
        </div>
      )}

      {errorMsg && (
        <div style={{
          backgroundColor: 'var(--color-alert-red-light)',
          border: '1px solid var(--color-alert-red)',
          color: 'var(--color-alert-red)',
          padding: '0.75rem 1rem',
          borderRadius: 'var(--radius-sm)',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          fontSize: '0.9rem'
        }}>
          <AlertCircle size={18} />
          <span>{errorMsg}</span>
        </div>
      )}

      <form onSubmit={handleSave} className="card" style={{ padding: '2rem' }}>
        {/* Required Fields Group */}
        <div style={{
          borderBottom: '1px solid var(--color-grey-border)',
          paddingBottom: '1.5rem',
          marginBottom: '1.5rem'
        }}>
          <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem', color: 'var(--color-navy)' }}>
            Required Identifiers
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.25rem' }}>
            <div className="form-group" style={{ margin: 0 }}>
              <label className="form-label">
                Patient ID <span style={{ color: 'var(--color-alert-red)' }}>*</span>
              </label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. PT-1001"
                value={patientId}
                onChange={(e) => setPatientId(e.target.value)}
                required
                style={{ fontWeight: 600, letterSpacing: '0.04em' }}
              />
              <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                Unique record key connecting all ECG uploads and reports.
              </span>
            </div>

            <div className="form-group" style={{ margin: 0 }}>
              <label className="form-label">
                Age (Years) <span style={{ color: 'var(--color-alert-red)' }}>*</span>
              </label>
              <input
                type="number"
                min="1"
                max="125"
                className="form-input"
                value={age}
                onChange={(e) => setAge(e.target.value)}
                required
              />
              <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                Required for age-appropriate physiological rate evaluation.
              </span>
            </div>
          </div>
        </div>

        {/* Optional Clinical Context */}
        <div style={{
          borderBottom: '1px solid var(--color-grey-border)',
          paddingBottom: '1.5rem',
          marginBottom: '1.5rem'
        }}>
          <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem', color: 'var(--color-navy)' }}>
            Optional Clinical Information
          </h3>

          <div className="form-group">
            <label className="form-label">Gender (Optional)</label>
            <select
              className="form-select"
              value={gender}
              onChange={(e) => setGender(e.target.value)}
            >
              <option value="Not specified">Prefer not to say / Unspecified</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Existing Cardiac Condition (Optional)</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. Hypertension, Paroxysmal Atrial Fibrillation, Coronary Stent"
              value={existingCondition}
              onChange={(e) => setExistingCondition(e.target.value)}
            />
          </div>

          <div className="form-group" style={{ margin: 0 }}>
            <label className="form-label">Relevant Medical History (Optional)</label>
            <textarea
              className="form-textarea"
              rows={3}
              placeholder="Any relevant surgical history, cardiovascular medications (e.g. Beta-blockers, Anticoagulants), or family history..."
              value={medicalHistory}
              onChange={(e) => setMedicalHistory(e.target.value)}
            />
          </div>
        </div>

        {/* Research Consent Checkbox */}
        <div style={{
          backgroundColor: 'var(--color-bg-light)',
          border: '1px solid var(--color-grey-border)',
          borderRadius: 'var(--radius-sm)',
          padding: '1rem',
          marginBottom: '1.75rem',
          display: 'flex',
          gap: '0.75rem',
          alignItems: 'flex-start'
        }}>
          <input
            type="checkbox"
            id="researchConsent"
            checked={consentForResearch}
            onChange={(e) => setConsentForResearch(e.target.checked)}
            style={{ marginTop: '0.25rem', width: '18px', height: '18px', cursor: 'pointer' }}
          />
          <label htmlFor="researchConsent" style={{ cursor: 'pointer', fontSize: '0.875rem', lineHeight: 1.5 }}>
            <strong style={{ color: 'var(--color-navy)' }}>Opt-in for Anonymous Research Studies:</strong>
            <div style={{ color: 'var(--color-text-muted)', marginTop: '0.25rem' }}>
              DRISTHI strictly enforces rule #5: Patient uploads are never automatically trained upon.
              Check this box only if you voluntarily consent to have de-identified signal segments included
              in future algorithm validation research.
            </div>
          </label>
        </div>

        <button
          type="submit"
          className="btn btn-primary"
          style={{ padding: '0.75rem 1.75rem', fontSize: '0.95rem' }}
          disabled={loading}
        >
          <Save size={18} />
          {loading ? 'Saving Profile...' : 'Save Profile Details'}
        </button>
      </form>
    </div>
  );
};
