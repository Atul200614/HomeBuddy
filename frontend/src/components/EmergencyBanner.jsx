import React from 'react';

export default function EmergencyBanner({ onEmergencyClick }) {
  return (
    <div className="container" style={{ marginBottom: '2.5rem' }}>
      <div style={{
        background: '#FEF2F2',
        border: '1px solid #FECACA',
        borderRadius: '16px',
        padding: '1.25rem 1.75rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '1rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <span style={{
            fontSize: '1.75rem',
            background: '#FEE2E2',
            padding: '0.6rem',
            borderRadius: '50%'
          }}>⚡</span>
          <div>
            <h4 style={{ fontWeight: 800, color: '#991B1B', margin: 0 }}>Emergency Home Repair Needed?</h4>
            <p style={{ margin: 0, fontSize: '0.85rem', color: '#7F1D1D' }}>
              Water pipe burst, sudden power outage, or broken door lock? Fast-track 45-minute dispatch in Pune.
            </p>
          </div>
        </div>

        <button 
          onClick={onEmergencyClick}
          style={{
            background: '#DC2626',
            color: '#fff',
            fontWeight: 800,
            border: 'none',
            borderRadius: '9999px',
            padding: '0.65rem 1.4rem',
            fontSize: '0.88rem'
          }}
        >
          🚨 Request Emergency Dispatch
        </button>
      </div>
    </div>
  );
}
