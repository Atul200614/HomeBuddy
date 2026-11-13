import React from 'react';
import { commercialServices } from '../data/mockData';

export default function CommercialSpaces({ onSelectService }) {
  return (
    <div className="container" style={{ marginBottom: '3.5rem' }}>
      <div className="hb-section-head">
        <div>
          <h2>Corporates & Commercial Spaces</h2>
          <p style={{ color: '#64748B', fontSize: '0.9rem' }}>Keeping your business spaces spotless, fresh, and welcoming.</p>
        </div>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: '1.25rem'
      }}>
        {commercialServices.map((c, i) => (
          <div key={i} style={{
            background: '#fff',
            borderRadius: '16px',
            overflow: 'hidden',
            border: '1px solid #E2E8F0',
            boxShadow: 'var(--hb-shadow)'
          }}>
            <img src={c.img} alt={c.name} style={{ width: '100%', height: '150px', objectFit: 'cover' }} />
            <div style={{ padding: '1.2rem' }}>
              <h4 style={{ fontWeight: 800, fontSize: '1rem', marginBottom: '6px' }}>{c.name}</h4>
              <p style={{ fontSize: '0.8rem', color: '#64748B', marginBottom: '14px' }}>{c.desc}</p>
              <button 
                onClick={() => onSelectService(c.name)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#0F4A3C',
                  fontWeight: 700,
                  fontSize: '0.85rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: 0
                }}
              >
                Inquire Commercial Quote ➔
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
