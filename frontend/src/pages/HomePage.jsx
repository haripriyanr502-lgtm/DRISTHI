import React from 'react';
import { 
  UploadCloud, 
  Activity, 
  ShieldCheck, 
  Cpu, 
  CheckCircle2, 
  ArrowRight, 
  Sparkles, 
  FileCode, 
  AlertCircle,
  Database,
  Sliders,
  Radio,
  UserCheck,
  Heart,
  FileText
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const HomePage = ({ setActivePage, onStartSampleDemo }) => {
  const { isPublic, isPatient, isCaregiver, currentPatientId, switchDemoPersona } = useAuth();

  const handleLaunchPatientFlow = async () => {
    await switchDemoPersona('patient');
    setActivePage('patient-dashboard');
  };

  const handleLaunchCaretakerFlow = async () => {
    await switchDemoPersona('caregiver');
    setActivePage('caregiver-dashboard');
  };

  const handleInspectReport = async () => {
    await switchDemoPersona('patient');
    setActivePage('results');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem' }}>
      {/* Hero Section */}
      <section style={{
        background: 'linear-gradient(135deg, #12304A 0%, #1A4264 60%, #205984 100%)',
        borderRadius: 'var(--radius-lg)',
        padding: '3.5rem 2.5rem',
        color: '#FFFFFF',
        boxShadow: 'var(--shadow-lg)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{
          position: 'absolute',
          right: '-5%',
          top: '10%',
          opacity: 0.08,
          pointerEvents: 'none'
        }}>
          <Activity size={420} strokeWidth={1} />
        </div>

        <div style={{ maxWidth: '780px', position: 'relative', zIndex: 1 }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.5rem',
            backgroundColor: 'rgba(32, 163, 158, 0.25)',
            border: '1px solid rgba(32, 163, 158, 0.6)',
            color: '#20A39E',
            padding: '0.35rem 0.85rem',
            borderRadius: '9999px',
            fontSize: '0.825rem',
            fontWeight: 700,
            marginBottom: '1.25rem',
            letterSpacing: '0.04em'
          }}>
            <Sparkles size={14} />
            AI-ASSISTED CARDIAC MONITORING PLATFORM
          </div>

          <h1 style={{ color: '#FFFFFF', marginBottom: '0.85rem', fontSize: '2.6rem', fontWeight: 800 }}>
            DRISTHI
          </h1>

          <div style={{
            fontSize: '1.35rem',
            fontWeight: 600,
            color: '#77C1E8',
            marginBottom: '1.25rem',
            letterSpacing: '-0.01em'
          }}>
            From ECG Signals to Timely Action.
          </div>

          <p style={{
            color: '#D4E4F0',
            fontSize: '1.05rem',
            lineHeight: 1.6,
            marginBottom: '2rem',
            maxWidth: '680px'
          }}>
            DRISTHI bridges raw electrocardiogram signals with non-destructive signal conditioning, 
            transparent AI research models, and caregiver oversight. No mandatory registration required for public users.
          </p>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.85rem', alignItems: 'center' }}>
            <button
              onClick={() => setActivePage('upload')}
              className="btn btn-teal"
              style={{ padding: '0.85rem 1.75rem', fontSize: '1rem', fontWeight: 700 }}
            >
              <UploadCloud size={20} />
              Upload ECG Record
            </button>

            <button
              onClick={() => {
                if (onStartSampleDemo) onStartSampleDemo();
                else setActivePage('upload');
              }}
              className="btn"
              style={{
                backgroundColor: 'rgba(255, 255, 255, 0.15)',
                color: '#FFFFFF',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                padding: '0.85rem 1.5rem',
                fontSize: '0.95rem'
              }}
            >
              <Activity size={18} />
              Try 10-Second Sample Demo
            </button>

            <button
              onClick={handleLaunchPatientFlow}
              className="btn btn-outline"
              style={{
                color: '#FFFFFF',
                borderColor: 'rgba(255, 255, 255, 0.4)',
                padding: '0.85rem 1.25rem'
              }}
            >
              Explore Live Patient Case (PT-4082)
              <ArrowRight size={16} />
            </button>
          </div>
        </div>
      </section>

      {/* FEATURED CASE STUDY: Total Patient & Caretaker Workflow Banner */}
      <section className="card" style={{
        border: '2px solid var(--color-blue)',
        backgroundColor: '#FFFFFF',
        padding: '2rem',
        borderRadius: 'var(--radius-lg)',
        boxShadow: 'var(--shadow-md)'
      }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: '1rem', marginBottom: '1.5rem' }}>
          <div>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', color: 'var(--color-teal)', fontWeight: 700, fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              <Sparkles size={16} />
              End-to-End Clinical Journey
            </div>
            <h2 style={{ fontSize: '1.5rem', color: 'var(--color-navy)', marginTop: '0.2rem' }}>
              Total Workflow: Patient (Rajesh Patel) & Caretaker (Priya Patel)
            </h2>
            <p style={{ margin: 0, fontSize: '0.9rem' }}>
              Explore how DRISTHI captures an exertional palpitation event, preserves original raw data, executes zero-phase filtering, and alerts the caregiver.
            </p>
          </div>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.65rem' }}>
            <button
              onClick={handleLaunchPatientFlow}
              className="btn btn-primary"
              style={{ fontSize: '0.85rem', padding: '0.55rem 1.1rem' }}
            >
              👤 Patient Portal (Rajesh)
            </button>
            <button
              onClick={handleLaunchCaretakerFlow}
              className="btn btn-teal"
              style={{ fontSize: '0.85rem', padding: '0.55rem 1.1rem' }}
            >
              🛡️ Caretaker Portal (Priya)
            </button>
            <button
              onClick={handleInspectReport}
              className="btn btn-outline"
              style={{ fontSize: '0.85rem', padding: '0.55rem 1.1rem' }}
            >
              📊 Inspect Waveform Report
            </button>
          </div>
        </div>

        {/* Chronological 5-Step Workflow Cards */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '1rem'
        }}>
          {/* Step 1 */}
          <div style={{
            backgroundColor: 'var(--color-bg-light)',
            border: '1px solid var(--color-grey-border)',
            borderRadius: 'var(--radius-sm)',
            padding: '1.15rem',
            position: 'relative'
          }}>
            <div style={{ fontSize: '0.725rem', fontWeight: 700, color: 'var(--color-blue)', textTransform: 'uppercase' }}>
              Step 1: Patient Context
            </div>
            <div style={{ fontWeight: 700, color: 'var(--color-navy)', fontSize: '0.95rem', margin: '0.35rem 0' }}>
              Rajesh Patel (58M)
            </div>
            <p style={{ fontSize: '0.8rem', margin: 0, lineHeight: 1.5 }}>
              Patient ID <strong>PT-4082</strong> with hypertension history records baseline and exertional rhythm strips. Explicit consent granted.
            </p>
          </div>

          {/* Step 2 */}
          <div style={{
            backgroundColor: 'var(--color-bg-light)',
            border: '1px solid var(--color-grey-border)',
            borderRadius: 'var(--radius-sm)',
            padding: '1.15rem'
          }}>
            <div style={{ fontSize: '0.725rem', fontWeight: 700, color: 'var(--color-teal)', textTransform: 'uppercase' }}>
              Step 2: Signal Ingestion
            </div>
            <div style={{ fontWeight: 700, color: 'var(--color-navy)', fontSize: '0.95rem', margin: '0.35rem 0' }}>
              Raw Waveform Stored
            </div>
            <p style={{ fontSize: '0.8rem', margin: 0, lineHeight: 1.5 }}>
              10-second Lead II recording preserved unmodified in <code style={{ fontSize: '0.75rem' }}>data/raw/</code>. File size: 24.8 KB.
            </p>
          </div>

          {/* Step 3 */}
          <div style={{
            backgroundColor: 'var(--color-bg-light)',
            border: '1px solid var(--color-grey-border)',
            borderRadius: 'var(--radius-sm)',
            padding: '1.15rem'
          }}>
            <div style={{ fontSize: '0.725rem', fontWeight: 700, color: 'var(--color-warning)', textTransform: 'uppercase' }}>
              Step 3: Preprocessing
            </div>
            <div style={{ fontWeight: 700, color: 'var(--color-navy)', fontSize: '0.95rem', margin: '0.35rem 0' }}>
              114 BPM Tachycardia
            </div>
            <p style={{ fontSize: '0.8rem', margin: 0, lineHeight: 1.5 }}>
              Pan-Tompkins algorithm detects 19 R-peaks. 0.67 Hz zero-phase filter suppresses respiratory baseline drift without morphology loss.
            </p>
          </div>

          {/* Step 4 */}
          <div style={{
            backgroundColor: 'var(--color-bg-light)',
            border: '1px solid var(--color-grey-border)',
            borderRadius: 'var(--radius-sm)',
            padding: '1.15rem'
          }}>
            <div style={{ fontSize: '0.725rem', fontWeight: 700, color: 'var(--color-navy)', textTransform: 'uppercase' }}>
              Step 4: AI Model Output
            </div>
            <div style={{ fontWeight: 700, color: 'var(--color-navy)', fontSize: '0.95rem', margin: '0.35rem 0' }}>
              Sinus Tachycardia
            </div>
            <p style={{ fontSize: '0.8rem', margin: 0, lineHeight: 1.5 }}>
              Structured inference identifies elevated rate (114 BPM) with narrow QRS complexes. Labeled transparently as Research Demo.
            </p>
          </div>

          {/* Step 5 */}
          <div style={{
            backgroundColor: '#FFFDF7',
            border: '1px solid var(--color-warning)',
            borderRadius: 'var(--radius-sm)',
            padding: '1.15rem'
          }}>
            <div style={{ fontSize: '0.725rem', fontWeight: 700, color: 'var(--color-alert-red)', textTransform: 'uppercase' }}>
              Step 5: Caretaker Feed
            </div>
            <div style={{ fontWeight: 700, color: 'var(--color-navy)', fontSize: '0.95rem', margin: '0.35rem 0' }}>
              Priya Patel Notified
            </div>
            <p style={{ fontSize: '0.8rem', margin: 0, lineHeight: 1.5 }}>
              Advisory alert generated in Caregiver dashboard. Priya acknowledges event with timestamp audit trail.
            </p>
          </div>
        </div>
      </section>

      {/* Public vs Registered Access Architecture Banner */}
      <div className="card" style={{
        backgroundColor: '#FFFFFF',
        borderLeft: '4px solid var(--color-teal)',
        padding: '1.25rem 1.5rem',
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '1rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{
            width: '42px',
            height: '42px',
            borderRadius: '50%',
            backgroundColor: 'var(--color-teal-light)',
            color: 'var(--color-teal)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0
          }}>
            <ShieldCheck size={24} />
          </div>
          <div>
            <div style={{ fontWeight: 700, color: 'var(--color-navy)', fontSize: '1rem' }}>
              Open Public Access & Voluntary Registration
            </div>
            <p style={{ margin: 0, fontSize: '0.875rem' }}>
              Public users can immediately upload and analyze ECG records without an account. Registered patients can permanently save records, track long-term history, and assign caregivers.
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            onClick={() => setActivePage('upload')}
            className="btn btn-outline"
            style={{ fontSize: '0.85rem', padding: '0.5rem 1rem' }}
          >
            Direct Upload (Public)
          </button>
          <button
            onClick={() => setActivePage('auth')}
            className="btn btn-secondary"
            style={{ fontSize: '0.85rem', padding: '0.5rem 1rem' }}
          >
            Account Access
          </button>
        </div>
      </div>

      {/* Project Modules Breakdown Grid */}
      <div>
        <div style={{ marginBottom: '1.25rem' }}>
          <h2>Core System Architecture</h2>
          <p>
            DRISTHI is built in accordance with a 7-stage clinical pipeline designed for modular research integration.
          </p>
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: '1.25rem'
        }}>
          {/* Card 1 */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
              <div style={{ color: 'var(--color-blue)', backgroundColor: 'var(--color-blue-light)', padding: '0.5rem', borderRadius: '8px' }}>
                <UploadCloud size={20} />
              </div>
              <div>
                <h4>1. Multi-Format Input Ingestion</h4>
                <span className="badge badge-success">Implemented</span>
              </div>
            </div>
            <p style={{ fontSize: '0.9rem' }}>
              Accepts ECG Images (.png, .jpg), XML records (.xml), DICOM files (.dcm), and numerical time-series (.csv). Preserves original raw data.
            </p>
          </div>

          {/* Card 2 */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
              <div style={{ color: 'var(--color-teal)', backgroundColor: 'var(--color-teal-light)', padding: '0.5rem', borderRadius: '8px' }}>
                <Sliders size={20} />
              </div>
              <div>
                <h4>2. Signal Preprocessing & Inspection</h4>
                <span className="badge badge-success">Implemented</span>
              </div>
            </div>
            <p style={{ fontSize: '0.9rem' }}>
              Non-destructive baseline wander removal (0.67 Hz zero-phase), powerline notch filtering (50 Hz), QRS R-peak detection, and Signal Quality Index (SNR) scoring.
            </p>
          </div>

          {/* Card 3 */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
              <div style={{ color: 'var(--color-warning)', backgroundColor: 'var(--color-warning-light)', padding: '0.5rem', borderRadius: '8px' }}>
                <FileCode size={20} />
              </div>
              <div>
                <h4>3. AI Algorithm Benchmarking</h4>
                <span className="badge badge-demo">Research Mode</span>
              </div>
            </div>
            <p style={{ fontSize: '0.9rem' }}>
              Modular AI adapter interface. Evaluation of 1D-ResNet, Bi-LSTM, and Transformer models against PTB-XL and MIT-BIH datasets currently underway.
            </p>
          </div>

          {/* Card 4 */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
              <div style={{ color: 'var(--color-navy)', backgroundColor: 'var(--color-grey-light)', padding: '0.5rem', borderRadius: '8px' }}>
                <Database size={20} />
              </div>
              <div>
                <h4>4. Patient Records & Consent</h4>
                <span className="badge badge-success">Implemented</span>
              </div>
            </div>
            <p style={{ fontSize: '0.9rem' }}>
              Patient profiles organized by unique Patient ID. Demographic info is kept strictly non-substitutive for ECG evidence. Explicit opt-in consent for research data.
            </p>
          </div>

          {/* Card 5 */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
              <div style={{ color: 'var(--color-blue)', backgroundColor: 'var(--color-blue-light)', padding: '0.5rem', borderRadius: '8px' }}>
                <Activity size={20} />
              </div>
              <div>
                <h4>5. Visual Rhythm Strip Comparison</h4>
                <span className="badge badge-success">Implemented</span>
              </div>
            </div>
            <p style={{ fontSize: '0.9rem' }}>
              Interactive medical grid visualization allowing side-by-side comparison of untouched raw signals vs conditioned signals with R-peak markers.
            </p>
          </div>

          {/* Card 6 */}
          <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
              <div style={{ color: '#D97706', backgroundColor: '#FEF3C7', padding: '0.5rem', borderRadius: '8px' }}>
                <Radio size={20} />
              </div>
              <div>
                <h4>6. Hardware & Caregiver Monitoring</h4>
                <span className="badge badge-info">Staged (ESP32)</span>
              </div>
            </div>
            <p style={{ fontSize: '0.9rem' }}>
              Dedicated Caregiver dashboard with alert acknowledgement. Staged architecture for ESP32 and AD8232 single-lead analog front-end live telemetry.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
