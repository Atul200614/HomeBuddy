import React, { useState } from 'react';

export default function WorkProofModal({ onClose }) {
  const [confirmed, setConfirmed] = useState(false);
  const [feedback, setFeedback] = useState('');

  return (
    <div className="hb-modal-overlay" onClick={onClose}>
      <div className="hb-modal-card" style={{ maxWidth: '640px' }} onClick={(e) => e.stopPropagation()}>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', paddingBottom: '0.75rem', borderBottom: '1px solid #E2E8F0' }}>
          <div>
            <span style={{ fontSize: '0.75rem', color: '#EAB308', fontWeight: 800, textTransform: 'uppercase' }}>Quality Compliance</span>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 800, margin: 0 }}>
              Work Proof Verification #HB-2026-00102
            </h3>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', fontSize: '1.4rem', color: '#94A3B8' }}>✕</button>
        </div>

        <p style={{ fontSize: '0.85rem', color: '#64748B', marginBottom: '1rem' }}>
          Technician <strong>Vikram Shinde</strong> has uploaded work proof photographs for your inspection.
        </p>

        {/* Before and After Image Comparison */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1rem' }}>
          <div>
            <div style={{ background: '#DC2626', color: '#fff', fontSize: '0.7rem', fontWeight: 800, padding: '2px 8px', borderRadius: '4px', display: 'inline-block', marginBottom: '4px' }}>
              BEFORE SERVICE
            </div>
            <img 
              src="https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=400&q=80" 
              alt="Before cleaning" 
              style={{ width: '100%', height: '170px', objectFit: 'cover', borderRadius: '12px', border: '2px solid #E2E8F0' }}
            />
          </div>

          <div>
            <div style={{ background: '#166534', color: '#fff', fontSize: '0.7rem', fontWeight: 800, padding: '2px 8px', borderRadius: '4px', display: 'inline-block', marginBottom: '4px' }}>
              AFTER COMPLETION
            </div>
            <img 
              src="https://images.unsplash.com/photo-1581578731548-c64695cc6952?auto=format&fit=crop&w=400&q=80" 
              alt="After cleaning" 
              style={{ width: '100%', height: '170px', objectFit: 'cover', borderRadius: '12px', border: '2px solid #E2E8F0' }}
            />
          </div>
        </div>

        <div style={{ background: '#F8FAFC', padding: '0.75rem 1rem', borderRadius: '10px', fontSize: '0.82rem', color: '#475569', marginBottom: '1rem' }}>
          <strong>Technician Notes:</strong> Thoroughly degreased kitchen exhaust chimney, sanitized bathroom tiles with Diversey safe chemicals, and mechanized floor buffing completed.
        </div>

        {confirmed ? (
          <div style={{ background: '#ECFDF5', border: '1px solid #A7F3D0', padding: '1rem', borderRadius: '12px', textAlign: 'center' }}>
            <span style={{ fontSize: '1.8rem' }}>✅</span>
            <div style={{ fontWeight: 800, color: '#065F46', marginTop: '4px' }}>Customer Sign-off Granted!</div>
            <p style={{ fontSize: '0.8rem', color: '#047857', margin: 0 }}>
              Invoice #INV-2026-00102 generated and technician earnings ledger updated.
            </p>
          </div>
        ) : (
          <div>
            <textarea 
              rows="2"
              placeholder="Add your satisfaction feedback (Optional)..."
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              style={{ width: '100%', padding: '0.6rem', borderRadius: '10px', border: '1px solid #CBD5E1', fontSize: '0.85rem', marginBottom: '1rem' }}
            />

            <button 
              onClick={() => setConfirmed(true)}
              style={{
                width: '100%',
                background: '#0F4A3C',
                color: '#fff',
                fontWeight: 800,
                borderRadius: '9999px',
                padding: '0.75rem',
                border: 'none',
                fontSize: '0.9rem'
              }}
            >
              ✓ Approve Work & Confirm Completion
            </button>
          </div>
        )}

      </div>
    </div>
  );
}
