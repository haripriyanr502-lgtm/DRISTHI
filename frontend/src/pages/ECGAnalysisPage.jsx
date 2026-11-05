import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Cpu, 
  Database, 
  FileSearch, 
  Sliders, 
  CheckCircle2, 
  AlertTriangle, 
  ArrowRight,
  BookOpen,
  Layers,
  Sparkles
} from 'lucide-react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';

export const ECGAnalysisPage = ({ setActivePage, latestAnalysisId }) => {
  const { currentPatientId } = useAuth();
  const [aiStatus, setAiStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const data = await api.getAIStatus();
        setAiStatus(data);
      } catch (err) {
        console.warn('AI status check:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchStatus();
  }, []);

  return (
    <div style={{ maxWidth: '960px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div>
        <h2>AI-Based ECG Analysis Layer</h2>
        <p>
          Modular AI architecture staging interface for candidate neural network models and IEEE benchmark evaluation.
        </p>
      </div>

      {/* Development & Research Status Alert */}
      <div className="card" style={{
        backgroundColor: '#FFFBEB',
        border: '1px solid #FCD34D',
        padding: '1.5rem',
        borderRadius: 'var(--radius-md)'
      }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.85rem' }}>
          <div style={{
            color: '#B45309',
            backgroundColor: '#FEF3C7',
            padding: '0.5rem',
            borderRadius: '8px',
            flexShrink: 0
          }}>
            <AlertTriangle size={24} />
          </div>
          <div>
            <div style={{ fontSize: '1.05rem', fontWeight: 700, color: '#92400E', marginBottom: '0.35rem' }}>
              Module 5 Policy Notice: Algorithm Selection In Progress
            </div>
            <p style={{ color: '#78350F', fontSize: '0.9rem', lineHeight: 1.6, margin: 0 }}>
              Per development rule #3, DRISTHI does not invent final CNN or Transformer accuracy scores or fake clinical diagnoses.
              The inference layer below is currently operating in <strong>Research Demonstration Mode</strong> while parallel benchmark evaluations (IEEE literature & PhysioNet PTB-XL datasets) are conducted.
            </p>
          </div>
        </div>
      </div>

      {/* Fast Action to Results if an analysis was just run */}
      {latestAnalysisId && (
        <div className="card" style={{
          backgroundColor: 'var(--color-blue-light)',
          border: '1px solid var(--color-blue)',
          padding: '1.25rem 1.5rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '1rem'
        }}>
          <div>
            <div style={{ fontWeight: 700, color: 'var(--color-navy)' }}>
              Analysis Result Ready for Review
            </div>
            <div style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>
              Record Analysis ID: #{latestAnalysisId} (Associated with {currentPatientId})
            </div>
          </div>
          <button
            onClick={() => setActivePage('results')}
            className="btn btn-secondary"
            style={{ fontSize: '0.9rem' }}
          >
            Open Analysis Results Page
            <ArrowRight size={16} />
          </button>
        </div>
      )}

      {/* Model Architecture Specifications Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
        {/* Card 1: Active Adapter Interface */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '1rem' }}>
            <Cpu size={22} color="var(--color-teal)" />
            <h3 style={{ fontSize: '1.05rem' }}>Active Inference Adapter</h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.875rem' }}>
            <div>
              <span style={{ color: 'var(--color-text-muted)' }}>Adapter Status:</span>
              <div style={{ fontWeight: 600, color: 'var(--color-navy)' }}>
                {aiStatus?.status_description || 'Demonstration Mode Active'}
              </div>
            </div>

            <div>
              <span style={{ color: 'var(--color-text-muted)' }}>Interface Contract:</span>
              <div style={{ fontFamily: 'monospace', fontSize: '0.8rem', backgroundColor: 'var(--color-bg-light)', padding: '0.35rem 0.5rem', borderRadius: '4px' }}>
                BaseECGModel.predict(signal, sampling_rate)
              </div>
            </div>

            <div>
              <span style={{ color: 'var(--color-text-muted)' }}>Hot-Swappable Weights:</span>
              <div style={{ fontWeight: 600, color: 'var(--color-teal)' }}>
                Supported via PyTorch / ONNX / Keras
              </div>
            </div>
          </div>
        </div>

        {/* Card 2: Research Benchmark Datasets */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '1rem' }}>
            <Database size={22} color="var(--color-blue)" />
            <h3 style={{ fontSize: '1.05rem' }}>Evaluation Datasets</h3>
          </div>

          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.65rem', fontSize: '0.85rem' }}>
            <li style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
              <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: 'var(--color-blue)', marginTop: '6px' }}></span>
              <div>
                <strong>PTB-XL Database:</strong> 21,837 clinical 12-lead records (500 Hz / SCP-ECG standard).
              </div>
            </li>
            <li style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
              <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: 'var(--color-blue)', marginTop: '6px' }}></span>
              <div>
                <strong>PhysioNet MIT-BIH:</strong> Classical dual-lead arrhythmia validation benchmark.
              </div>
            </li>
            <li style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
              <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: 'var(--color-blue)', marginTop: '6px' }}></span>
              <div>
                <strong>Chapman / Shaoxing:</strong> 10,646 12-lead records for rhythm and conduction classification.
              </div>
            </li>
          </ul>
        </div>

        {/* Card 3: Candidate ML Architectures */}
        <div className="card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '1rem' }}>
            <Layers size={22} color="var(--color-navy)" />
            <h3 style={{ fontSize: '1.05rem' }}>Candidate Architectures</h3>
          </div>

          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.65rem', fontSize: '0.85rem' }}>
            <li style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
              <CheckCircle2 size={16} color="var(--color-teal)" style={{ flexShrink: 0, marginTop: '2px' }} />
              <div>
                <strong>1D Residual CNN (1D-ResNet):</strong> Deep spatial feature hierarchy across QRS complexes.
              </div>
            </li>
            <li style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
              <CheckCircle2 size={16} color="var(--color-teal)" style={{ flexShrink: 0, marginTop: '2px' }} />
              <div>
                <strong>Bi-LSTM + Self-Attention:</strong> Long-term temporal dependencies between cardiac beats.
              </div>
            </li>
            <li style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
              <CheckCircle2 size={16} color="var(--color-teal)" style={{ flexShrink: 0, marginTop: '2px' }} />
              <div>
                <strong>PatchTST / Vision Transformer:</strong> Attention-based physiological patch representations.
              </div>
            </li>
          </ul>
        </div>
      </div>

      {/* Target Diagnostic Categories Supported */}
      <div className="card" style={{ padding: '1.75rem' }}>
        <h3 style={{ fontSize: '1.15rem', marginBottom: '0.5rem' }}>
          Target Classification Categories (Taxonomy)
        </h3>
        <p style={{ marginBottom: '1.25rem', fontSize: '0.875rem' }}>
          The structured output schema prepares predictions across standard clinical cardiac rhythm classifications:
        </p>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '0.85rem'
        }}>
          {[
            { label: 'Normal Sinus Rhythm', code: 'NSR', desc: 'Uniform P waves, regular PR interval 120-200ms' },
            { label: 'Atrial Fibrillation', code: 'AFIB', desc: 'Irregularly irregular RR intervals, absent P waves' },
            { label: 'Premature Ventricular Contractions', code: 'PVC', desc: 'Bizarre, wide QRS complex (>120ms)' },
            { label: 'Sinus Tachycardia', code: 'STACH', desc: 'Physiological sinus rhythm exceeding 100 BPM' },
            { label: 'Sinus Bradycardia', code: 'SBRAD', desc: 'Physiological sinus rhythm under 60 BPM' },
            { label: 'Ventricular Bigeminy', code: 'BIGEM', desc: 'Alternating normal and ectopic ventricular complexes' }
          ].map((cat, idx) => (
            <div key={idx} style={{
              backgroundColor: 'var(--color-bg-light)',
              border: '1px solid var(--color-grey-border)',
              borderRadius: 'var(--radius-sm)',
              padding: '0.85rem'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                <span style={{ fontWeight: 700, color: 'var(--color-navy)', fontSize: '0.875rem' }}>
                  {cat.label}
                </span>
                <span className="badge badge-info" style={{ fontSize: '0.65rem' }}>
                  {cat.code}
                </span>
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                {cat.desc}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Direct Call to Action */}
      <div style={{ textAlign: 'center', padding: '1rem 0' }}>
        <button
          onClick={() => setActivePage('upload')}
          className="btn btn-teal"
          style={{ padding: '0.85rem 2rem', fontSize: '1rem' }}
        >
          <Activity size={18} />
          Go to ECG Upload & Run Pipeline
        </button>
      </div>
    </div>
  );
};
