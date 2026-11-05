import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  FileText, 
  Heart, 
  ShieldAlert, 
  CheckCircle2, 
  Clock, 
  FileCheck, 
  Sliders, 
  Download, 
  ArrowLeft,
  Info,
  Layers,
  Sparkles
} from 'lucide-react';
import { api } from '../services/api';
import { ECGWaveformViewer } from '../components/ECGWaveformViewer';
import { MetricCard } from '../components/MetricCard';
import { StatusBadge } from '../components/StatusBadge';
import { useAuth } from '../context/AuthContext';

export const AnalysisResultsPage = ({ setActivePage, analysisId, onBackToUpload }) => {
  const { currentPatientId } = useAuth();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    const fetchResults = async () => {
      setLoading(true);
      setErrorMsg('');
      try {
        let targetId = analysisId;
        
        // If no specific analysis ID is supplied, check if the patient has recent records
        if (!targetId && currentPatientId) {
          const recResp = await api.getPatientRecords(currentPatientId);
          if (recResp.records && recResp.records.length > 0) {
            const latest = recResp.records.find(r => r.analysis_id) || recResp.records[0];
            targetId = latest.analysis_id;
          }
        }

        // If still no ID, generate a default demo sample
        if (!targetId) {
          const demoResp = await api.loadSampleECG({ patientId: currentPatientId || 'PT-DEMO-01', rhythmType: 'normal' });
          targetId = demoResp.data.analysis_id;
        }

        const data = await api.getAnalysisResults(targetId);
        setAnalysis(data);
      } catch (err) {
        setErrorMsg(err.message || 'Unable to retrieve analysis results.');
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
  }, [analysisId, currentPatientId]);

  if (loading) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
        <div style={{ color: 'var(--color-teal)', marginBottom: '1rem' }}>
          <Activity size={40} className="spin-slow" />
        </div>
        <h3>Loading ECG Analysis Results...</h3>
        <p style={{ marginTop: '0.5rem' }}>Extracting signal conditioning parameters and observations...</p>
      </div>
    );
  }

  if (errorMsg || !analysis) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3rem 2rem' }}>
        <div style={{ color: 'var(--color-alert-red)', marginBottom: '1rem' }}>
          <ShieldAlert size={40} />
        </div>
        <h3>Analysis Results Unavailable</h3>
        <p style={{ marginTop: '0.5rem', color: 'var(--color-text-muted)' }}>{errorMsg || 'No analysis record found.'}</p>
        <button
          onClick={() => setActivePage('upload')}
          className="btn btn-primary"
          style={{ marginTop: '1.5rem' }}
        >
          <ArrowLeft size={16} />
          Go to ECG Upload
        </button>
      </div>
    );
  }

  const { file_details, signal_quality, prediction, waveform } = analysis;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', maxWidth: '1100px', margin: '0 auto' }}>
      {/* Header bar */}
      <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: '1rem' }}>
        <div>
          <button
            onClick={() => setActivePage('upload')}
            className="btn btn-outline"
            style={{ marginBottom: '0.5rem', padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}
          >
            <ArrowLeft size={14} />
            Back to Upload
          </button>
          <h2>ECG Analysis Report</h2>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginTop: '0.25rem' }}>
            <span style={{ fontWeight: 600, color: 'var(--color-navy)' }}>
              Patient ID: {analysis.patient_id}
            </span>
            <span>•</span>
            <span style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem' }}>
              Report ID: #{analysis.id}
            </span>
            <span>•</span>
            <span style={{ color: 'var(--color-text-muted)', fontSize: '0.85rem' }}>
              {new Date(analysis.created_at).toLocaleString()}
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <StatusBadge status={analysis.status} isDemo={analysis.is_simulated_demo} />
          <button
            onClick={() => window.print()}
            className="btn btn-outline"
            style={{ fontSize: '0.85rem', padding: '0.5rem 0.85rem' }}
            title="Print or Save Report to PDF"
          >
            <Download size={15} />
            Export Report
          </button>
        </div>
      </div>

      {/* DEMO DATA MANDATORY WATERMARK BANNER (Requirement #4 & #5) */}
      <div style={{
        backgroundColor: '#FFFBEB',
        border: '2px solid #F59E0B',
        borderRadius: 'var(--radius-md)',
        padding: '1.25rem 1.5rem',
        display: 'flex',
        alignItems: 'flex-start',
        gap: '1rem',
        boxShadow: 'var(--shadow-sm)'
      }}>
        <div style={{
          backgroundColor: '#FEF3C7',
          color: '#B45309',
          padding: '0.5rem',
          borderRadius: '8px',
          flexShrink: 0
        }}>
          <ShieldAlert size={26} />
        </div>
        <div>
          <div style={{
            fontSize: '1.05rem',
            fontWeight: 800,
            color: '#92400E',
            letterSpacing: '0.03em',
            marginBottom: '0.25rem'
          }}>
            DEMO DATA – NOT A REAL PATIENT RECORD
          </div>
          <p style={{ margin: 0, color: '#78350F', fontSize: '0.885rem', lineHeight: 1.5 }}>
            This electrocardiogram trace, patient profile, and analysis summary are generated from synthetic physiological simulation data for workflow demonstration. 
            <strong> These mock results do NOT represent an actual AI prediction, medical diagnosis, or clinically validated accuracy.</strong>
          </p>
        </div>
      </div>

      {/* Metrics Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.25rem' }}>
        <MetricCard
          title="Heart Rate"
          value={signal_quality?.estimated_heart_rate_bpm ? Math.round(signal_quality.estimated_heart_rate_bpm) : '—'}
          unit="BPM"
          icon={Heart}
          color="var(--color-navy)"
          subtitle={
            signal_quality?.estimated_heart_rate_bpm > 100 ? 'Sinus Tachycardia range' :
            signal_quality?.estimated_heart_rate_bpm < 60 ? 'Sinus Bradycardia range' : 'Normofrequent range'
          }
        />

        <MetricCard
          title="Signal Quality (SNR)"
          value={signal_quality?.quality_score !== undefined ? `${Math.round(signal_quality.quality_score * 100)}%` : '—'}
          icon={Activity}
          color="var(--color-teal)"
          subtitle={`Noise Level: ${signal_quality?.noise_level || 'Low'}`}
        />

        <MetricCard
          title="QRS Complexes"
          value={signal_quality?.r_peaks_detected || 0}
          unit="R-Peaks"
          icon={Sliders}
          color="var(--color-blue)"
          subtitle={`Duration: ${signal_quality?.duration_seconds || 10} seconds`}
        />

        <MetricCard
          title="Baseline Drift"
          value={signal_quality?.baseline_wander_detected ? 'Detected' : 'Minimal'}
          icon={Layers}
          color={signal_quality?.baseline_wander_detected ? 'var(--color-warning)' : 'var(--color-teal)'}
          subtitle="Respiration filter applied"
        />
      </div>

      {/* Main Interactive Waveform Rhythm Strip */}
      <div>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
          <h3>Electrocardiogram Waveform Preview</h3>
          <span style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
            Comparing Original Unmodified Trace vs Filtered Trace
          </span>
        </div>

        {waveform && (
          <ECGWaveformViewer
            originalSignal={waveform.original_signal}
            processedSignal={waveform.processed_signal}
            rPeakIndices={signal_quality?.r_peak_indices}
            samplingRate={waveform.sampling_rate_hz || 250.0}
            leadName={waveform.lead_name}
            isSimulated={analysis.is_simulated_demo}
          />
        )}
      </div>

      {/* Model Predictions & Preprocessing Insights */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '1.5rem' }}>
        {/* Model Prediction Box */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <h3 style={{ fontSize: '1.1rem' }}>Model Prediction</h3>
            <span className="badge badge-demo">Simulated Demo</span>
          </div>

          <div style={{
            backgroundColor: 'var(--color-blue-light)',
            borderRadius: 'var(--radius-sm)',
            padding: '1.25rem',
            border: '1px solid var(--color-grey-border)',
            marginBottom: '1rem'
          }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Identified Rhythm Morphology
            </div>
            <div style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--color-navy)', marginTop: '0.25rem' }}>
              {prediction?.prediction_label || 'Normal Sinus Rhythm (Demonstration)'}
            </div>
            {prediction?.confidence_score && (
              <div style={{ fontSize: '0.85rem', color: 'var(--color-teal)', fontWeight: 600, marginTop: '0.35rem' }}>
                Demonstration Confidence: {(prediction.confidence_score * 100).toFixed(0)}%
              </div>
            )}
          </div>

          <div style={{ fontSize: '0.825rem', color: 'var(--color-text-muted)', lineHeight: 1.6 }}>
            <div><strong>Active Model Architecture:</strong> {prediction?.model_name}</div>
            <div><strong>Pipeline Version:</strong> {prediction?.model_version}</div>
          </div>
        </div>

        {/* Signal Observations */}
        <div className="card">
          <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem' }}>
            Objective Signal Observations
          </h3>

          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.65rem', fontSize: '0.875rem' }}>
            {(prediction?.observations || []).map((obs, idx) => (
              <li key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
                <CheckCircle2 size={16} color="var(--color-teal)" style={{ flexShrink: 0, marginTop: '3px' }} />
                <span>{obs}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* File & Provenance Details Card */}
      <div className="card" style={{ padding: '1.5rem' }}>
        <h4 style={{ marginBottom: '1rem' }}>Uploaded File & Provenance Metadata</h4>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '1rem',
          fontSize: '0.85rem'
        }}>
          <div>
            <span style={{ color: 'var(--color-text-muted)' }}>Original File Name:</span>
            <div style={{ fontWeight: 600 }}>{file_details?.original_filename || 'Record'}</div>
          </div>
          <div>
            <span style={{ color: 'var(--color-text-muted)' }}>Format Category:</span>
            <div style={{ fontWeight: 600 }}>{file_details?.file_type?.toUpperCase() || 'SIGNAL'}</div>
          </div>
          <div>
            <span style={{ color: 'var(--color-text-muted)' }}>Raw File Size:</span>
            <div style={{ fontWeight: 600 }}>{((file_details?.file_size_bytes || 0) / 1024).toFixed(1)} KB</div>
          </div>
          <div>
            <span style={{ color: 'var(--color-text-muted)' }}>Raw Signal Preservation:</span>
            <div style={{ fontWeight: 600, color: 'var(--color-teal)' }}>Unmodified Raw Stored</div>
          </div>
        </div>
      </div>
    </div>
  );
};
