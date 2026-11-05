import React from 'react';

export const StatusBadge = ({ status, isDemo = false }) => {
  if (isDemo || status === 'completed_demo') {
    return (
      <span className="badge badge-demo" title="DEMO DATA – NOT A REAL PATIENT RECORD">
        DEMO DATA
      </span>
    );
  }

  switch (status?.toLowerCase()) {
    case 'completed':
    case 'normal':
    case 'optimal':
      return <span className="badge badge-success">Completed</span>;
    case 'pending':
    case 'awaiting_model':
    case 'staged':
      return <span className="badge badge-warning">Awaiting Model Integration</span>;
    case 'error':
    case 'critical':
      return <span className="badge badge-danger">Alert / Review</span>;
    default:
      return <span className="badge badge-info">{status || 'Active'}</span>;
  }
};
