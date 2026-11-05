import React from 'react';
import { ShieldAlert, Cpu, Heart, CheckCircle2 } from 'lucide-react';

export const Footer = () => {
  return (
    <footer style={{
      backgroundColor: '#0c1f30',
      color: '#A0B3C6',
      borderTop: '1px solid rgba(255, 255, 255, 0.08)',
      padding: '2.5rem 1.5rem 1.5rem',
      fontSize: '0.85rem'
    }}>
      <div style={{
        maxWidth: '1280px',
        margin: '0 auto',
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
        gap: '2rem',
        marginBottom: '2rem'
      }}>
        {/* Col 1: Project Identity */}
        <div>
          <div style={{
            fontSize: '1.15rem',
            fontWeight: 800,
            color: '#FFFFFF',
            marginBottom: '0.5rem',
            letterSpacing: '0.04em'
          }}>
            DRISTHI
          </div>
          <p style={{ color: '#8BA0B5', lineHeight: 1.6, marginBottom: '0.75rem' }}>
            AI-Assisted ECG Analysis and Patient-Specific Cardiac Monitoring.
            Bridging raw physiological electrocardiogram data with timely, understandable action.
          </p>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.4rem',
            color: 'var(--color-teal)',
            fontWeight: 600,
            fontSize: '0.8rem'
          }}>
            <span>Tagline:</span> From ECG Signals to Timely Action.
          </div>
        </div>

        {/* Col 2: Research & Development Status */}
        <div>
          <div style={{
            fontSize: '0.925rem',
            fontWeight: 700,
            color: '#FFFFFF',
            marginBottom: '0.75rem',
            textTransform: 'uppercase',
            letterSpacing: '0.05em'
          }}>
            Architecture Status
          </div>
          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <li style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#10B981' }}></span>
              <span><strong>Module 3 & 4:</strong> Preprocessing Pipeline (Operational)</span>
            </li>
            <li style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#F59E0B' }}></span>
              <span><strong>Module 5:</strong> AI Model (Research Demo / IEEE Review)</span>
            </li>
            <li style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#3B82F6' }}></span>
              <span><strong>Module 8 & 9:</strong> ESP32 + AD8232 Hardware (Staged)</span>
            </li>
          </ul>
        </div>

        {/* Col 3: Research Integrity & Regulatory Notice */}
        <div>
          <div style={{
            fontSize: '0.925rem',
            fontWeight: 700,
            color: '#FFFFFF',
            marginBottom: '0.75rem',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem'
          }}>
            <ShieldAlert size={16} color="var(--color-warning)" />
            Clinical Notice
          </div>
          <p style={{ color: '#8BA0B5', lineHeight: 1.6 }}>
            DRISTHI is under active software and algorithm development. All predictions are generated in 
            research demonstration mode. The system does not constitute medical advice, diagnosis, 
            or clinical validation.
          </p>
        </div>
      </div>

      <div style={{
        maxWidth: '1280px',
        margin: '0 auto',
        paddingTop: '1.25rem',
        borderTop: '1px solid rgba(255, 255, 255, 0.05)',
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '1rem',
        color: '#60758A',
        fontSize: '0.775rem'
      }}>
        <div>
          © 2026 DRISTHI Project. Developed with clean modular architecture.
        </div>
        <div style={{ display: 'flex', gap: '1.25rem' }}>
          <span>Privacy & Data Sovereignty</span>
          <span>Explicit Consent Enforced</span>
          <span>Zero Fabricated Telemetry</span>
        </div>
      </div>
    </footer>
  );
};
