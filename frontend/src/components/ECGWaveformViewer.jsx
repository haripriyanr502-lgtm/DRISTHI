import React, { useState, useMemo } from 'react';
import { Eye, Layers, ZoomIn, ZoomOut, CheckCircle, Info } from 'lucide-react';

export const ECGWaveformViewer = ({
  originalSignal = [],
  processedSignal = [],
  rPeakIndices = [],
  samplingRate = 250.0,
  leadName = 'Lead II (Standard Rhythm Strip)',
  isSimulated = true
}) => {
  const [viewMode, setViewMode] = useState('comparison'); // 'comparison', 'processed', 'original'
  const [zoomLevel, setZoomLevel] = useState(1); // 1 = full, 2 = 50%, 4 = 25%
  const [windowOffset, setWindowOffset] = useState(0); // 0 to 1

  const numPoints = Math.max(originalSignal.length, processedSignal.length);

  // Compute visible slice according to zoom and scroll
  const visiblePoints = useMemo(() => {
    if (numPoints === 0) return { orig: [], proc: [], rPeaks: [], startSec: 0, endSec: 0 };
    const sliceLength = Math.max(100, Math.floor(numPoints / zoomLevel));
    const maxStart = Math.max(0, numPoints - sliceLength);
    const startIndex = Math.min(maxStart, Math.floor(windowOffset * maxStart));
    const endIndex = Math.min(numPoints, startIndex + sliceLength);

    const orig = originalSignal.slice(startIndex, endIndex);
    const proc = processedSignal.slice(startIndex, endIndex);

    // Visible R-peaks offset
    const visibleRPeaks = (rPeakIndices || [])
      .filter(idx => idx >= startIndex && idx < endIndex)
      .map(idx => idx - startIndex);

    const startSec = (startIndex / samplingRate).toFixed(2);
    const endSec = (endIndex / samplingRate).toFixed(2);

    return { orig, proc, visibleRPeaks, startSec, endSec, count: endIndex - startIndex };
  }, [originalSignal, processedSignal, rPeakIndices, zoomLevel, windowOffset, numPoints, samplingRate]);

  // SVG coordinate transformation
  const svgWidth = 1000;
  const svgHeight = 260;
  const paddingY = 30;

  // Compute min/max for dynamic auto-scaling
  const { minVal, maxVal } = useMemo(() => {
    const all = [...visiblePoints.orig, ...visiblePoints.proc];
    if (all.length === 0) return { minVal: -1.5, maxVal: 2.0 };
    let min = Math.min(...all);
    let max = Math.max(...all);
    if (max - min < 0.2) {
      min -= 0.5;
      max += 0.5;
    }
    return { minVal: min - 0.2, maxVal: max + 0.2 };
  }, [visiblePoints]);

  const mapPoint = (val, index, total) => {
    const x = (index / (total - 1 || 1)) * svgWidth;
    const normY = (val - minVal) / (maxVal - minVal || 1);
    const y = svgHeight - paddingY - normY * (svgHeight - paddingY * 2);
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  };

  const origPath = useMemo(() => {
    if (!visiblePoints.orig.length) return '';
    return visiblePoints.orig.map((val, idx) => `${idx === 0 ? 'M' : 'L'} ${mapPoint(val, idx, visiblePoints.count)}`).join(' ');
  }, [visiblePoints.orig, minVal, maxVal, visiblePoints.count]);

  const procPath = useMemo(() => {
    if (!visiblePoints.proc.length) return '';
    return visiblePoints.proc.map((val, idx) => `${idx === 0 ? 'M' : 'L'} ${mapPoint(val, idx, visiblePoints.count)}`).join(' ');
  }, [visiblePoints.proc, minVal, maxVal, visiblePoints.count]);

  if (numPoints === 0) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3rem 1.5rem' }}>
        <p style={{ color: 'var(--color-text-muted)' }}>No ECG waveform signal data available for preview.</p>
      </div>
    );
  }

  return (
    <div className="card" style={{ padding: '1.25rem' }}>
      {/* Top Controls Toolbar */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '0.75rem',
        marginBottom: '0.85rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          <span style={{ fontWeight: 700, color: 'var(--color-navy)', fontSize: '1rem' }}>
            {leadName}
          </span>
          <span className="badge badge-info" style={{ fontSize: '0.72rem' }}>
            {samplingRate} Hz
          </span>
          {isSimulated && (
            <span className="badge badge-demo" style={{ fontSize: '0.7rem', fontWeight: 700 }}>
              DEMO DATA – NOT A REAL PATIENT RECORD
            </span>
          )}
        </div>

        {/* View Mode Switcher */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
          <div style={{
            display: 'inline-flex',
            backgroundColor: 'var(--color-grey-light)',
            padding: '2px',
            borderRadius: '6px'
          }}>
            <button
              onClick={() => setViewMode('comparison')}
              style={modeBtnStyle(viewMode === 'comparison')}
              title="Overlay Original & Processed Signals"
            >
              <Layers size={14} />
              Comparison
            </button>
            <button
              onClick={() => setViewMode('processed')}
              style={modeBtnStyle(viewMode === 'processed')}
              title="View Filtered Signal"
            >
              <Eye size={14} />
              Processed
            </button>
            <button
              onClick={() => setViewMode('original')}
              style={modeBtnStyle(viewMode === 'original')}
              title="View Raw Unconditioned Signal"
            >
              Raw
            </button>
          </div>

          {/* Zoom buttons */}
          <div style={{ display: 'flex', gap: '2px' }}>
            <button
              onClick={() => setZoomLevel(prev => Math.min(4, prev * 2))}
              className="btn btn-outline"
              style={{ padding: '0.35rem 0.55rem', fontSize: '0.75rem' }}
              title="Zoom In"
              disabled={zoomLevel >= 4}
            >
              <ZoomIn size={14} />
            </button>
            <button
              onClick={() => {
                setZoomLevel(prev => Math.max(1, prev / 2));
                setWindowOffset(0);
              }}
              className="btn btn-outline"
              style={{ padding: '0.35rem 0.55rem', fontSize: '0.75rem' }}
              title="Zoom Out"
              disabled={zoomLevel <= 1}
            >
              <ZoomOut size={14} />
            </button>
          </div>
        </div>
      </div>

      {/* ECG Medical Grid SVG Viewport */}
      <div className="ecg-grid-canvas" style={{ width: '100%', height: '260px' }}>
        <svg
          viewBox={`0 0 ${svgWidth} ${svgHeight}`}
          preserveAspectRatio="none"
          style={{ width: '100%', height: '100%', display: 'block' }}
        >
          {/* Center Zero-Voltage Guide line */}
          <line
            x1="0"
            y1={mapPoint(0.0, 0, 1).split(',')[1]}
            x2={svgWidth}
            y2={mapPoint(0.0, 0, 1).split(',')[1]}
            stroke="#D09298"
            strokeDasharray="4 4"
            strokeWidth="1"
          />

          {/* Original Signal Path (Muted Coral/Red trace) */}
          {(viewMode === 'comparison' || viewMode === 'original') && (
            <path
              d={origPath}
              fill="none"
              stroke="#D9534F"
              strokeWidth={viewMode === 'comparison' ? '1.5' : '2'}
              strokeOpacity={viewMode === 'comparison' ? '0.55' : '0.95'}
              strokeLinejoin="round"
            />
          )}

          {/* Processed Signal Path (Crisp Navy/Teal trace) */}
          {(viewMode === 'comparison' || viewMode === 'processed') && (
            <path
              d={procPath}
              fill="none"
              stroke="#12304A"
              strokeWidth="2.2"
              strokeLinejoin="round"
            />
          )}

          {/* Detected R-Peaks Markers */}
          {visiblePoints.visibleRPeaks && visiblePoints.visibleRPeaks.map((peakIdx, i) => {
            if (peakIdx < 0 || peakIdx >= visiblePoints.count) return null;
            const ptStr = mapPoint(visiblePoints.proc[peakIdx] || 0, peakIdx, visiblePoints.count);
            const [cx, cy] = ptStr.split(',');
            return (
              <g key={i}>
                <circle cx={cx} cy={cy} r="4" fill="#20A39E" stroke="#FFFFFF" strokeWidth="1.5" />
                <line x1={cx} y1={parseFloat(cy) - 8} x2={cx} y2={parseFloat(cy) - 2} stroke="#20A39E" strokeWidth="2" />
              </g>
            );
          })}
        </svg>

        {/* Lead Calibration Voltage Stamp */}
        <div style={{
          position: 'absolute',
          top: '8px',
          left: '12px',
          fontSize: '0.72rem',
          fontWeight: 700,
          color: '#8A3B43',
          backgroundColor: 'rgba(255, 253, 249, 0.85)',
          padding: '2px 6px',
          borderRadius: '4px',
          border: '1px solid #E8B4B8'
        }}>
          Standard 25 mm/s • 10 mm/mV
        </div>

        {/* DEMO DATA Watermark Stamp */}
        {isSimulated && (
          <div style={{
            position: 'absolute',
            top: '8px',
            right: '12px',
            fontSize: '0.72rem',
            fontWeight: 800,
            letterSpacing: '0.04em',
            color: '#92400E',
            backgroundColor: 'rgba(254, 243, 199, 0.95)',
            padding: '3px 8px',
            borderRadius: '4px',
            border: '1px solid #FCD34D',
            boxShadow: '0 1px 2px rgba(0,0,0,0.05)'
          }}>
            DEMO DATA – NOT A REAL PATIENT RECORD
          </div>
        )}

        {/* Time Window Stamp */}
        <div style={{
          position: 'absolute',
          bottom: '8px',
          right: '12px',
          fontSize: '0.72rem',
          fontWeight: 600,
          color: '#5C7182',
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          padding: '2px 6px',
          borderRadius: '4px',
          border: '1px solid var(--color-grey-border)'
        }}>
          Window: {visiblePoints.startSec}s – {visiblePoints.endSec}s ({((numPoints)/samplingRate).toFixed(1)}s total)
        </div>
      </div>

      {/* Scrub bar if zoomed */}
      {zoomLevel > 1 && (
        <div style={{ marginTop: '0.65rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>Scroll Timeline:</span>
          <input
            type="range"
            min="0"
            max="1"
            step="0.01"
            value={windowOffset}
            onChange={(e) => setWindowOffset(parseFloat(e.target.value))}
            style={{ flex: 1, cursor: 'pointer' }}
          />
        </div>
      )}

      {/* Trace Legend */}
      <div style={{
        marginTop: '0.85rem',
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '0.75rem',
        paddingTop: '0.75rem',
        borderTop: '1px solid var(--color-grey-border)',
        fontSize: '0.8rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
          {(viewMode === 'comparison' || viewMode === 'processed') && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span style={{ width: '16px', height: '3px', backgroundColor: '#12304A', display: 'inline-block' }}></span>
              <span style={{ fontWeight: 600, color: '#12304A' }}>Conditioned Signal (Processed)</span>
            </div>
          )}
          {(viewMode === 'comparison' || viewMode === 'original') && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span style={{ width: '16px', height: '3px', backgroundColor: '#D9534F', display: 'inline-block' }}></span>
              <span style={{ fontWeight: 600, color: '#D9534F' }}>Raw Unmodified Signal (Original)</span>
            </div>
          )}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#20A39E', display: 'inline-block' }}></span>
            <span style={{ color: 'var(--color-text-muted)' }}>Identified R-Peaks</span>
          </div>
        </div>

        <div style={{ color: 'var(--color-text-muted)', fontSize: '0.75rem' }}>
          Showing {visiblePoints.count} samples ({samplingRate} samples/sec)
        </div>
      </div>
    </div>
  );
};

const modeBtnStyle = (isActive) => ({
  display: 'inline-flex',
  alignItems: 'center',
  gap: '0.3rem',
  padding: '0.3rem 0.65rem',
  fontSize: '0.75rem',
  fontWeight: isActive ? 600 : 500,
  borderRadius: '4px',
  backgroundColor: isActive ? 'var(--color-white)' : 'transparent',
  color: isActive ? 'var(--color-navy)' : 'var(--color-text-muted)',
  boxShadow: isActive ? '0 1px 2px rgba(0,0,0,0.06)' : 'none'
});
