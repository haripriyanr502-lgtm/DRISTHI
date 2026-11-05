import React from 'react';

export const MetricCard = ({ title, value, unit, icon: Icon, color = 'var(--color-navy)', subtitle }) => {
  return (
    <div className="card" style={{ padding: '1.25rem', position: 'relative', overflow: 'hidden' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
        <span style={{ fontSize: '0.825rem', fontWeight: 600, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
          {title}
        </span>
        {Icon && (
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '6px',
            backgroundColor: `${color}15`,
            color: color,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <Icon size={18} />
          </div>
        )}
      </div>

      <div style={{ display: 'flex', alignItems: 'baseline', gap: '0.35rem', marginBottom: '0.25rem' }}>
        <span style={{ fontSize: '1.85rem', fontWeight: 700, color: color, lineHeight: 1 }}>
          {value !== null && value !== undefined ? value : '—'}
        </span>
        {unit && (
          <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--color-text-muted)' }}>
            {unit}
          </span>
        )}
      </div>

      {subtitle && (
        <div style={{ fontSize: '0.775rem', color: 'var(--color-text-muted)' }}>
          {subtitle}
        </div>
      )}
    </div>
  );
};
