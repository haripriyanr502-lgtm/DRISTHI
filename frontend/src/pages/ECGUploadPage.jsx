import React, { useState, useEffect, useRef } from 'react';
import { 
  UploadCloud, 
  FileText, 
  Image as ImageIcon, 
  FileCode, 
  Activity, 
  AlertCircle, 
  CheckCircle2, 
  Zap, 
  Layers, 
  Clock, 
  FileCheck,
  ShieldAlert,
  Sparkles,
  Heart,
  ArrowRight,
  Database
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';

export const ECGUploadPage = ({ setActivePage, onAnalysisComplete }) => {
  const { currentPatientId, updateActivePatientId, isPublic } = useAuth();
  
  // Tab: 'demo-mode' or 'file-upload'
  const [activeTab, setActiveTab] = useState('demo-mode');
  
  // Demo catalog
  const [demoCases, setDemoCases] = useState([]);
  const [loadingCases, setLoadingCases] = useState(false);
  const [loadingCaseId, setLoadingCaseId] = useState(null);

  // File upload state
  const [patientId, setPatientId] = useState(currentPatientId || 'PT-1001');
  const [file, setFile] = useState(null);
  const [filePreview, setFilePreview] = useState(null);
  const [fileCategory, setFileCategory] = useState(null);
  const [consentForResearch, setConsentForResearch] = useState(false);
  const [samplingRate, setSamplingRate] = useState(250.0);
  
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successResult, setSuccessResult] = useState(null);

  const fileInputRef = useRef(null);

  useEffect(() => {
    const fetchDemoCases = async () => {
      setLoadingCases(true);
      try {
        const resp = await api.getDemoCases();
        setDemoCases(resp.cases || []);
      } catch (err) {
        console.warn('Failed to load demo cases catalog:', err);
      } finally {
        setLoadingCases(false);
      }
    };
    fetchDemoCases();
  }, []);

  const handleSelectDemoCase = async (caseId) => {
    setErrorMsg('');
    setLoadingCaseId(caseId);

    try {
      const resp = await api.loadDemoCase(caseId);
      updateActivePatientId(resp.patient_id);
      if (onAnalysisComplete) {
        onAnalysisComplete(resp.analysis_id);
      } else {
        setActivePage('results');
      }
    } catch (err) {
      setErrorMsg(err.message || `Failed to load demo case ${caseId}`);
    } finally {
      setLoadingCaseId(null);
    }
  };

  const handleFileSelection = (selectedFile) => {
    setErrorMsg('');
    setSuccessResult(null);

    if (!selectedFile) return;

    const maxBytes = 25 * 1024 * 1024;
    if (selectedFile.size > maxBytes) {
      setErrorMsg(`File size (${(selectedFile.size / (1024 * 1024)).toFixed(2)} MB) exceeds 25 MB limit.`);
      return;
    }

    const name = selectedFile.name.toLowerCase();
    const ext = name.slice(name.lastIndexOf('.'));
    const supportedExts = ['.png', '.jpg', '.jpeg', '.xml', '.dcm', '.csv', '.json', '.dat'];

    if (!supportedExts.includes(ext)) {
      setErrorMsg(`Unsupported file type '${ext}'. Supported formats: ECG Images (.png, .jpg), XML (.xml), DICOM (.dcm), Numerical (.csv, .dat, .json).`);
      return;
    }

    setFile(selectedFile);

    if (['.png', '.jpg', '.jpeg'].includes(ext)) {
      setFileCategory('image');
      const reader = new FileReader();
      reader.onload = (e) => setFilePreview({ type: 'image', src: e.target.result });
      reader.readAsDataURL(selectedFile);
    } else if (['.csv', '.xml', '.json'].includes(ext)) {
      setFileCategory(ext.slice(1));
      const reader = new FileReader();
      reader.onload = (e) => {
        const textSample = e.target.result.slice(0, 300);
        setFilePreview({ type: 'text', content: textSample });
      };
      reader.readAsText(selectedFile);
    } else {
      setFileCategory('dicom');
      setFilePreview({ type: 'binary', name: selectedFile.name });
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setErrorMsg('Please select or drop an ECG file to upload.');
      return;
    }

    if (!patientId.trim()) {
      setErrorMsg('Please enter a valid Patient ID.');
      return;
    }

    setErrorMsg('');
    setIsUploading(true);
    setUploadProgress(20);

    const timer = setInterval(() => {
      setUploadProgress(prev => (prev < 85 ? prev + 15 : prev));
    }, 150);

    try {
      const pid = patientId.trim().toUpperCase();
      updateActivePatientId(pid);

      const resp = await api.uploadECG({
        file,
        patientId: pid,
        consentForResearch,
        samplingRate
      });

      clearInterval(timer);
      setUploadProgress(100);
      setSuccessResult(resp.data);

      if (onAnalysisComplete) {
        onAnalysisComplete(resp.data.analysis_id);
      }
    } catch (err) {
      clearInterval(timer);
      setErrorMsg(err.message || 'File upload failed. Please verify format and backend connectivity.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      <div>
        <h2>ECG Input & Testing Center</h2>
        <p>
          Test the complete DRISTHI workflow using synthetic sample ECG signals or upload clinical recordings.
        </p>
      </div>

      {/* Mode Switcher Tabs */}
      <div style={{
        display: 'flex',
        backgroundColor: 'var(--color-grey-light)',
        borderRadius: 'var(--radius-sm)',
        padding: '3px'
      }}>
        <button
          type="button"
          onClick={() => setActiveTab('demo-mode')}
          style={{
            flex: 1,
            padding: '0.75rem 1rem',
            borderRadius: '4px',
            fontWeight: 700,
            fontSize: '0.925rem',
            backgroundColor: activeTab === 'demo-mode' ? '#FFFFFF' : 'transparent',
            color: activeTab === 'demo-mode' ? 'var(--color-navy)' : 'var(--color-text-muted)',
            boxShadow: activeTab === 'demo-mode' ? 'var(--shadow-sm)' : 'none',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.5rem'
          }}
        >
          <Sparkles size={16} color="var(--color-teal)" />
          Temporary Demo Data Mode (5 Synthetic Cases)
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('file-upload')}
          style={{
            flex: 1,
            padding: '0.75rem 1rem',
            borderRadius: '4px',
            fontWeight: 700,
            fontSize: '0.925rem',
            backgroundColor: activeTab === 'file-upload' ? '#FFFFFF' : 'transparent',
            color: activeTab === 'file-upload' ? 'var(--color-navy)' : 'var(--color-text-muted)',
            boxShadow: activeTab === 'file-upload' ? 'var(--shadow-sm)' : 'none',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.5rem'
          }}
        >
          <UploadCloud size={16} color="var(--color-blue)" />
          Custom File Upload (Image / XML / DICOM / CSV)
        </button>
      </div>

      {errorMsg && (
        <div style={{
          backgroundColor: 'var(--color-alert-red-light)',
          border: '1px solid var(--color-alert-red)',
          color: 'var(--color-alert-red)',
          padding: '0.85rem 1rem',
          borderRadius: 'var(--radius-sm)',
          display: 'flex',
          alignItems: 'center',
          gap: '0.65rem',
          fontSize: '0.9rem'
        }}>
          <AlertCircle size={20} style={{ flexShrink: 0 }} />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* TAB 1: TEMPORARY DEMO DATA MODE */}
      {activeTab === 'demo-mode' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Mandatory Watermark Alert */}
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
                The application currently operates with synthetic sample ECG signals to demonstrate and test the complete workflow while verified clinical dataset collection and algorithm benchmarking are in progress.
                <strong> Mock results are for workflow verification only and do not represent actual AI predictions, medical diagnoses, or validated accuracy.</strong>
              </p>
            </div>
          </div>

          <div>
            <h3 style={{ fontSize: '1.15rem', marginBottom: '0.35rem' }}>
              Select a Synthetic ECG Case to Test the Workflow:
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>
              Each case includes calibrated physiological waveforms (Lead II, 250 Hz, 10s), sample patient profiles, and structured mock report data.
            </p>
          </div>

          {loadingCases ? (
            <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
              <Activity size={32} className="spin-slow" color="var(--color-teal)" />
              <div style={{ marginTop: '0.75rem', color: 'var(--color-text-muted)' }}>Loading synthetic case catalog...</div>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {demoCases.map((c) => (
                <div
                  key={c.case_id}
                  className="card"
                  style={{
                    padding: '1.25rem 1.5rem',
                    display: 'flex',
                    flexWrap: 'wrap',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    gap: '1rem',
                    borderLeft: `4px solid ${
                      c.rhythm_type === 'normal' ? 'var(--color-teal)' :
                      c.rhythm_type === 'tachycardia' ? 'var(--color-warning)' :
                      c.rhythm_type === 'afib' ? 'var(--color-alert-red)' : 'var(--color-blue)'
                    }`
                  }}
                >
                  <div style={{ flex: 1, minWidth: '280px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
                      <span style={{ fontWeight: 800, color: 'var(--color-navy)', fontSize: '1.05rem' }}>
                        {c.title}
                      </span>
                      <span className="badge badge-demo" style={{ fontSize: '0.65rem' }}>
                        DEMO DATA
                      </span>
                    </div>

                    <div style={{ fontSize: '0.85rem', color: 'var(--color-text-dark)', marginBottom: '0.35rem' }}>
                      Patient: <strong>{c.patient_id}</strong> (Age {c.patient_age}{c.patient_gender ? `, ${c.patient_gender}` : ''}) • Condition: <em>{c.existing_condition}</em>
                    </div>

                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem', fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>
                      <span>Heart Rate: <strong style={{ color: 'var(--color-navy)' }}>{c.heart_rate_bpm} BPM</strong></span>
                      <span>•</span>
                      <span>Signal SNR: <strong>{Math.round(c.signal_quality_score * 100)}%</strong></span>
                      <span>•</span>
                      <span>Format: <strong>Lead II (250 Hz, 10s)</strong></span>
                    </div>
                  </div>

                  <div>
                    <button
                      type="button"
                      onClick={() => handleSelectDemoCase(c.case_id)}
                      className="btn btn-primary"
                      disabled={loadingCaseId === c.case_id}
                      style={{ fontSize: '0.875rem', padding: '0.55rem 1.15rem' }}
                    >
                      {loadingCaseId === c.case_id ? (
                        <>
                          <Activity size={16} className="spin-slow" />
                          Loading Workflow...
                        </>
                      ) : (
                        <>
                          Load Case & View Report
                          <ArrowRight size={16} />
                        </>
                      )}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 2: CUSTOM FILE UPLOAD MODE */}
      {activeTab === 'file-upload' && (
        <form onSubmit={handleUploadSubmit} className="card" style={{ padding: '2rem' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.25rem', marginBottom: '1.5rem' }}>
            <div className="form-group" style={{ margin: 0 }}>
              <label className="form-label">
                Patient ID <span style={{ color: 'var(--color-alert-red)' }}>*</span>
              </label>
              <input
                type="text"
                className="form-input"
                value={patientId}
                onChange={(e) => setPatientId(e.target.value)}
                placeholder="e.g. PT-1001"
                required
              />
              <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                Associates this recording with the patient's record series.
              </span>
            </div>

            <div className="form-group" style={{ margin: 0 }}>
              <label className="form-label">
                Sampling Frequency (Hz)
              </label>
              <select
                className="form-select"
                value={samplingRate}
                onChange={(e) => setSamplingRate(parseFloat(e.target.value))}
              >
                <option value="250">250 Hz (Clinical Standard Monitor)</option>
                <option value="360">360 Hz (MIT-BIH Arrhythmia Database)</option>
                <option value="500">500 Hz (PTB-XL Diagnostic 12-Lead)</option>
                <option value="128">128 Hz (Low-power Telemetry)</option>
              </select>
            </div>
          </div>

          {/* Drag and Drop Zone */}
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onClick={() => fileInputRef.current && fileInputRef.current.click()}
            style={{
              border: `2px dashed ${isDragging ? 'var(--color-teal)' : 'var(--color-grey-border)'}`,
              backgroundColor: isDragging ? 'var(--color-teal-light)' : 'var(--color-bg-light)',
              borderRadius: 'var(--radius-md)',
              padding: '2.5rem 1.5rem',
              textAlign: 'center',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              marginBottom: '1.5rem'
            }}
          >
            <input
              type="file"
              ref={fileInputRef}
              style={{ display: 'none' }}
              onChange={(e) => e.target.files && handleFileSelection(e.target.files[0])}
              accept=".png,.jpg,.jpeg,.xml,.dcm,.csv,.json,.dat"
            />

            <div style={{
              width: '56px',
              height: '56px',
              borderRadius: '50%',
              backgroundColor: 'var(--color-white)',
              color: 'var(--color-blue)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 1rem',
              boxShadow: 'var(--shadow-sm)'
            }}>
              <UploadCloud size={28} />
            </div>

            <div style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--color-navy)', marginBottom: '0.35rem' }}>
              Drag and drop clinical ECG file here, or click to browse
            </div>

            <p style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)', maxWidth: '520px', margin: '0 auto 1rem' }}>
              Supported Categories: <strong>ECG Image (.png, .jpg)</strong>, <strong>XML (.xml)</strong>, <strong>DICOM (.dcm)</strong>, <strong>Numerical (.csv, .json)</strong>.
            </p>

            <span className="badge badge-info" style={{ fontSize: '0.75rem' }}>
              Maximum file size: 25 MB
            </span>
          </div>

          {file && (
            <div style={{
              backgroundColor: '#FFFFFF',
              border: '1px solid var(--color-grey-border)',
              borderRadius: 'var(--radius-sm)',
              padding: '1rem',
              marginBottom: '1.5rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: '1rem'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <div style={{
                  color: 'var(--color-teal)',
                  backgroundColor: 'var(--color-teal-light)',
                  padding: '0.5rem',
                  borderRadius: '6px'
                }}>
                  <FileCheck size={22} />
                </div>
                <div>
                  <div style={{ fontWeight: 600, color: 'var(--color-navy)', fontSize: '0.925rem' }}>
                    {file.name}
                  </div>
                  <div style={{ fontSize: '0.775rem', color: 'var(--color-text-muted)' }}>
                    Size: {(file.size / 1024).toFixed(1)} KB • Type: {fileCategory?.toUpperCase() || 'DOCUMENT'}
                  </div>
                </div>
              </div>

              <button
                type="button"
                onClick={() => { setFile(null); setFilePreview(null); }}
                className="btn btn-outline"
                style={{ fontSize: '0.75rem', padding: '0.3rem 0.65rem' }}
              >
                Remove
              </button>
            </div>
          )}

          {isUploading && (
            <div style={{ marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.35rem' }}>
                <span style={{ fontWeight: 600, color: 'var(--color-navy)' }}>Conditioning and Ingesting Signal...</span>
                <span>{uploadProgress}%</span>
              </div>
              <div style={{ width: '100%', height: '8px', backgroundColor: 'var(--color-grey-light)', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{
                  width: `${uploadProgress}%`,
                  height: '100%',
                  backgroundColor: 'var(--color-teal)',
                  transition: 'width 0.2s ease'
                }}></div>
              </div>
            </div>
          )}

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', padding: '0.85rem', fontSize: '1rem' }}
            disabled={!file || isUploading}
          >
            <UploadCloud size={20} />
            {isUploading ? 'Executing Preprocessing Pipeline...' : 'Upload & Execute Analysis Pipeline'}
          </button>
        </form>
      )}
    </div>
  );
};
