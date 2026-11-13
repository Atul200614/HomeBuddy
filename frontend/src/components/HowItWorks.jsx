import React from 'react';

export default function HowItWorks() {
  const steps = [
    { num: '1', icon: '📱', title: 'Choose Service & Slot', desc: 'Select your home care package, address, and arrival window.' },
    { num: '2', icon: '🛡️', title: 'Verified Team Arrives', desc: 'Police-verified technician arrives in uniform with eco-friendly tools.' },
    { num: '3', icon: '✨', title: 'Inspect Proof & Confirm', desc: 'Review before/after work photos, sign off satisfaction, and pay.' },
  ];

  return (
    <div className="container" style={{ marginBottom: '3.5rem', textAlign: 'center' }}>
      <h2 style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '0.5rem' }}>How to get Started</h2>
      <p style={{ color: '#64748B', fontSize: '0.92rem', marginBottom: '2.5rem' }}>
        Book your cleaning or repair service in just a few easy steps.
      </p>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
        gap: '1.5rem',
        textAlign: 'left'
      }}>
        {steps.map((s, i) => (
          <div key={i} style={{
            background: '#fff',
            border: '1px solid #E2E8F0',
            borderRadius: '20px',
            padding: '2rem',
            boxShadow: 'var(--hb-shadow)',
            position: 'relative'
          }}>
            <div style={{
              width: '54px',
              height: '54px',
              borderRadius: '50%',
              background: '#F0FDF4',
              color: '#0F4A3C',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.5rem',
              marginBottom: '1rem'
            }}>
              {s.icon}
            </div>
            <div style={{ fontSize: '0.8rem', fontWeight: 800, color: '#EAB308', marginBottom: '4px' }}>
              STEP 0{s.num}
            </div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 800, marginBottom: '8px' }}>{s.title}</h3>
            <p style={{ fontSize: '0.85rem', color: '#64748B', margin: 0 }}>{s.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
